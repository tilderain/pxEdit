# formatGuxt.py

import os
import struct
import mmap
import math
from stage import Stage, Layer, Entity
import util
from pxMap import PxEve

# --- Helper functions for VLQ (Variable-Length Quantity) encoding ---

def read_vlq(stream):
    """Reads a variable-length quantity from a file stream."""
    count = 0
    total = 0
    while True:
        v = stream.read_byte()
        if v >= 0x80:
            total += (v & 0x7f) << (count * 7)
            count += 1
        else:
            total += (v << (count * 7))
            break
    return total

def write_vlq(value):
    """Encodes an integer into a VLQ byte sequence."""
    output = bytearray()
    if value == 0:
        return b'\x00'
    while value > 0:
        byte = value & 0x7F
        value >>= 7
        if value > 0:
            byte |= 0x80
        output.append(byte)
    return bytes(output)

# --- Guxt Format Models ---

class PxMapGuxt:
    """Handles loading and saving of Guxt .pxmap and .pxattr files."""
    def __init__(self):
        self.width = 0
        self.height = 0
        self.tiles = []

    def load(self, path):
        try:
            with open(util.find_case_insensitive_path(os.path.dirname(path), os.path.basename(path)), 'rb') as f:
                data = f.read()
                self.width = struct.unpack('<H', data[0:2])[0]
                self.height = struct.unpack('<H', data[2:4])[0]
                tile_data = data[4:]
                self.tiles = [list(tile_data[i*self.width:(i+1)*self.width]) for i in range(self.height)]
        except (IOError, struct.error, IndexError) as e:
            print(f"Error loading Guxt map/attr file {path}: {e}")
            return False
        return True

    def save(self, path):
        try:
            with open(path, 'wb') as f:
                f.write(struct.pack('<HH', self.width, self.height))
                for row in self.tiles:
                    f.write(bytes(row))
        except IOError as e:
            print(f"Error saving Guxt map/attr file {path}: {e}")
            return False
        return True

class PxEveGuxt:
    """Handles loading and saving of Guxt .pxeve files."""
    class GuxtEntity:
        def __init__(self, unused, x, y, type1, type2):
            self.unused, self.x, self.y, self.type1, self.type2 = unused, x, y, type1, type2

    def __init__(self):
        self.entities = []

    def load(self, path):
        try:
            with open(util.find_case_insensitive_path(os.path.dirname(path), os.path.basename(path)), 'rb') as f, mmap.mmap(f.fileno(), 0, access=mmap.ACCESS_READ) as stream:
                entity_count = read_vlq(stream)
                for _ in range(entity_count):
                    unused = read_vlq(stream)
                    x = read_vlq(stream)
                    y = read_vlq(stream)
                    type1 = read_vlq(stream)
                    type2 = read_vlq(stream)
                    self.entities.append(self.GuxtEntity(unused, x, y, type1, type2))
        except (IOError, ValueError) as e:
            print(f"Error loading Guxt entity file {path}: {e}")
            return False
        return True

    def save(self, path):
        try:
            with open(path, 'wb') as f:
                f.write(write_vlq(len(self.entities)))
                for entity in self.entities:
                    f.write(write_vlq(entity.unused))
                    f.write(write_vlq(entity.x))
                    f.write(write_vlq(entity.y))
                    f.write(write_vlq(entity.type1))
                    f.write(write_vlq(entity.type2))
        except IOError as e:
            print(f"Error saving Guxt entity file {path}: {e}")
            return False
        return True

# --- Public Interface Functions ---

def load_stage(game_manager, stage_name, stage_table=None):
    """Loads a full Guxt stage from its constituent files."""
    game = game_manager.get_current_game()
    base_path = os.path.join(game.base_path, game.get('data_path'), game.get('stage_path'))
    
    map_filename = "map" + stage_name
    eve_filename = "event" + stage_name
    tileset_name = "parts" + stage_name

    map_path = util.find_case_insensitive_path(base_path, map_filename + game.get('stage_ext'))
    eve_path = util.find_case_insensitive_path(base_path, eve_filename + game.get('script_ext'))

    pxmap = PxMapGuxt()
    pxeve = PxEveGuxt()
    if not pxmap.load(map_path) or not pxeve.load(eve_path):
        raise FileNotFoundError(f"Could not load required stage files for '{stage_name}': {map_path} or {eve_path}")

    stage = Stage(stage_name, pxmap.width, pxmap.height)
    
    # --- THIS IS THE FIX: Create 3 layers for editor compatibility ---
    # Layer 0: Main tile layer
    layer0 = Layer(pxmap.width, pxmap.height)
    layer0.tiles = pxmap.tiles
    layer0.partsName = tileset_name
    stage.layers.append(layer0)
    
    # Layers 1 and 2: Empty placeholders
    stage.layers.append(Layer(0, 0))
    stage.layers.append(Layer(0, 0))
    # -----------------------------------------------------------------
    
    # Entity data
    stage.eve = PxEve()
    for i, guxt_entity in enumerate(pxeve.entities):
        entity = Entity(guxt_entity.type1, guxt_entity.x, guxt_entity.y, id=i)
        entity.param2 = guxt_entity.type2
        stage.eve.units.append(entity)
    stage.eve._count = len(stage.eve.units)
    
    return stage

def save_stage(game_manager, stage):
    """Saves a universal Stage object to Guxt's file formats."""
    game = game_manager.get_current_game()
    base_path = os.path.join(game.base_path, game.get('data_path'), game.get('stage_path'))
    
    # --- THIS IS THE FIX: Construct Guxt-specific filenames ---
    map_filename = "map" + stage.name
    eve_filename = "event" + stage.name
    # ---------------------------------------------------------

    map_path = os.path.join(base_path, map_filename + game.get('stage_ext'))
    eve_path = os.path.join(base_path, eve_filename + game.get('script_ext'))

    # --- Save Map Data ---
    pxmap = PxMapGuxt()
    if stage.layers:
        layer0 = stage.layers[0]
        pxmap.width, pxmap.height, pxmap.tiles = layer0.width, layer0.height, layer0.tiles
    if not pxmap.save(map_path): return False

    # --- Save Entity Data ---
    pxeve = PxEveGuxt()
    if stage.eve and stage.eve.units:
        for entity in stage.eve.units:
            # For Guxt, 'unused' is typically 1. Map 'param2' back to 'type2'.
            guxt_entity = PxEveGuxt.GuxtEntity(1, entity.x, entity.y, entity.type1, entity.param2)
            pxeve.entities.append(guxt_entity)
    if not pxeve.save(eve_path): return False
    
    return True

def load_attrs(game_manager, tileset_name, tileset_surface):
    """Loads attributes for a Guxt tileset."""
    game = game_manager.get_current_game()
    img_path_base = os.path.join(game.base_path, game.get('data_path'), game.get('image_path'))
    attr_path = util.find_case_insensitive_path(img_path_base, tileset_name + game.get('attr_ext'))

    attr = PxMapGuxt()
    if os.path.exists(attr_path) and os.path.getsize(attr_path) > 0:
        attr.load(attr_path)
    
    # Guxt's PxMapAttr is compatible with our internal PxMapAttr structure
    from pxMap import PxMapAttr
    px_map_attr = PxMapAttr()
    px_map_attr.width, px_map_attr.height, px_map_attr.tiles = attr.width, attr.height, attr.tiles
    return px_map_attr

def save_attribute(game_manager, layer, path):
    """Saves a Guxt .pxattr file."""
    if not layer: return False
    attr = PxMapGuxt()
    attr.width, attr.height, attr.tiles = layer.width, layer.height, layer.tiles
    return attr.save(path)
