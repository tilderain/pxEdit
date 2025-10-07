import os
import struct
import mmap
from stage import Stage, Layer, Entity
from pxMap import PxEve

from editor import game_manager

# --- Helper Functions for .pxpack format ---
def read_pixel_string(stream):
    try:
        length = stream.read_byte()
        if length > 32: return ""
        return stream.read(length).decode("shift-jis")
    except (struct.error, IndexError, UnicodeDecodeError):
        return ""

def write_pixel_string(fp, string):
    if string:
        try:
            encoded_string = string.encode("shift-jis")
            fp.write(struct.pack("<B", len(encoded_string)))
            fp.write(encoded_string)
        except (UnicodeEncodeError, struct.error):
            fp.write(struct.pack("<B", 0))
    else:
        fp.write(struct.pack("<B", 0))

def read_int(stream, length):
    return int.from_bytes(stream.read(length), byteorder="little")


# --- Kero Blaster Format Model ---

class PxPack:
    class Unit:
	    def __init__(self, bits, code_char, param2, x, y, flag, string, id):
	    	self.bits = bits
	    	self.type1 = code_char
	    	self.param2 = param2
	    	self.x = x
	    	self.y = y
	    	self.flag = flag
	    	self.string = string
	    	self.id = id

    class Layer:
        def __init__(self):
            self.partsName, self.visibility, self.scrolltype = "", 0, 0
            self.width, self.height, self.type = 0, 0, 0
            self.tiles = []

    def __init__(self):
        self.magic = b"PXPACK121127a**\0"
        self.description, self.spritesheet = "", ""
        self.left_field, self.right_field, self.up_field, self.down_field = "", "", "", ""
        self.area_x, self.area_y, self.area_no = 0, 0, 0
        self.bg_r, self.bg_g, self.bg_b = 0, 0, 0
        self.layers = []
        self.units = []

    def load(self, path):
        """Loads data from a .pxpack file, handling Kero Blaster, Rockfish, and Star Frog variants."""
        game = game_manager.get_current_game()
        is_starfrog10x = (game.name == 'star_frog_10x')
        is_rockfish = (game.name == 'rockfish')
        is_multilayer_format = game.get('pxpack_layers', 1) > 1

        with open(path, 'rb') as f, mmap.mmap(f.fileno(), 0, access=mmap.ACCESS_READ) as stream:
            # 1. Magic Header (Kero Blaster / Star Frog 11x only)
            if is_multilayer_format and not is_rockfish:
                stream.seek(16)

            # 2. Description and String Fields
            self.description = read_pixel_string(stream)
            if is_rockfish:
                self.spritesheet = read_pixel_string(stream)
            self.left_field = read_pixel_string(stream)
            self.right_field = read_pixel_string(stream)
            self.up_field = read_pixel_string(stream)
            self.down_field = read_pixel_string(stream)
            if not is_rockfish and not is_starfrog10x: # KB / SF11x
                self.spritesheet = read_pixel_string(stream)
            
            # 3. Area Info and Background Color
            self.area_x = read_int(stream, 2)
            self.area_y = read_int(stream, 2)
            self.area_no = read_int(stream, 1)
            self.bg_r = read_int(stream, 1)
            self.bg_g = read_int(stream, 1)
            self.bg_b = read_int(stream, 1)

            # 4. Layer Metadata
            num_layers = 3 if is_starfrog10x else game.get('pxpack_layers', 1)
            self.layers = [self.Layer() for _ in range(num_layers)]
            
            if is_rockfish:
                self.layers[0].partsName = self.spritesheet
            else: # KB, SF10x, SF11x have per-layer metadata
                for layer in self.layers:
                    layer.partsName = read_pixel_string(stream)
                    layer.visibility = read_int(stream, 1)
                    layer.scrolltype = read_int(stream, 1)
            
            # 5. Layer Tile Data
            for layer in self.layers:
                has_pxmap_header = is_multilayer_format and not is_rockfish
                if has_pxmap_header: stream.read(8)
                
                layer.width = read_int(stream, 2)
                layer.height = read_int(stream, 2)
                if layer.width * layer.height == 0: continue

                layer.type = read_int(stream, 1) if has_pxmap_header else 0
                if layer.type == 0:
                    layer.tiles = [list(stream.read(layer.width)) for _ in range(layer.height)]

            # 6. Entity Data
            entity_count = read_int(stream, 2)
            for i in range(entity_count):
                bits = read_int(stream, 1)
                type1 = read_int(stream, 1)
                param2 = read_int(stream, 1)
                x = struct.unpack('<h', stream.read(2))[0]
                y = struct.unpack('<h', stream.read(2))[0]
                flag = read_int(stream, 2)
                string = read_pixel_string(stream)
                self.units.append(self.Unit(bits, type1, param2, x, y, flag, string, i))
        return self

    def save(self, path):
        """Saves data to a .pxpack file, handling Kero Blaster, Rockfish, and Star Frog variants."""
        game = game_manager.get_current_game()
        is_starfrog10x = (game.name == 'star_frog_10x')
        is_rockfish = (game.name == 'rockfish')
        is_multilayer_format = game.get('pxpack_layers', 1) > 1

        with open(path, 'wb') as f:
            # 1. Magic Header
            if is_multilayer_format and not is_rockfish:
                f.write(self.magic)

            # 2. Description and String Fields
            write_pixel_string(f, self.description)
            if is_rockfish:
                write_pixel_string(f, self.spritesheet)
            write_pixel_string(f, self.left_field)
            write_pixel_string(f, self.right_field)
            write_pixel_string(f, self.up_field)
            write_pixel_string(f, self.down_field)
            if not is_rockfish and not is_starfrog10x:
                write_pixel_string(f, self.spritesheet)

            # 3. Area Info and Background Color
            f.write(struct.pack("<H", self.area_x))
            f.write(struct.pack("<H", self.area_y))
            f.write(struct.pack("<B", self.area_no))
            f.write(struct.pack("<B", self.bg_r))
            f.write(struct.pack("<B", self.bg_g))
            f.write(struct.pack("<B", self.bg_b))

            # 4. Layer Metadata
            if not is_rockfish:
                for layer in self.layers:
                    write_pixel_string(f, layer.partsName)
                    f.write(struct.pack("<B", layer.visibility))
                    f.write(struct.pack("<B", layer.scrolltype))

            # 5. Layer Tile Data
            for layer in self.layers:
                has_pxmap_header = is_multilayer_format and not is_rockfish
                if has_pxmap_header: f.write(b"pxMAP01\0")
                
                f.write(struct.pack("<H", layer.width))
                f.write(struct.pack("<H", layer.height))
                if layer.width * layer.height == 0: continue

                if has_pxmap_header: f.write(struct.pack("<B", layer.type))
                if layer.type == 0: [f.write(bytes(y)) for y in layer.tiles]

            # 6. Entity Data
            f.write(struct.pack("<H", len(self.units)))
            for unit in self.units:
                f.write(struct.pack("<B", unit.bits))
                f.write(struct.pack("<B", unit.type1))
                f.write(struct.pack("<B", unit.param2))
                f.write(struct.pack("<h", unit.x))
                f.write(struct.pack("<h", unit.y))
                f.write(struct.pack("<H", unit.flag))
                write_pixel_string(f, unit.string)
        return self

    def to_stage(self, stage_name):
        """Translates this PxPack object into a universal Stage object."""
        stage = Stage(stage_name, self.layers[0].width, self.layers[0].height)
        stage.description = self.description
        stage.spritesheet = self.spritesheet
        stage.left_field = self.left_field
        stage.right_field = self.right_field
        stage.up_field = self.up_field
        stage.down_field = self.down_field
        stage.area_x = self.area_x
        stage.area_y = self.area_y
        stage.area_no = self.area_no
        stage.bg_r, stage.bg_g, stage.bg_b = self.bg_r, self.bg_g, self.bg_b
        stage.eve = PxEve()
        for l in self.layers:
            new_layer = Layer(l.width, l.height)
            new_layer.tiles = l.tiles
            new_layer.partsName = l.partsName
            new_layer.visibility = l.visibility
            new_layer.scrolltype = l.scrolltype
            stage.layers.append(new_layer)
        for unit in self.units:
            entity = Entity(unit.type1, unit.x, unit.y, unit.flag, id=unit.id)
            entity.bits, entity.param2, entity.string = unit.bits, unit.param2, unit.string
            stage.eve.units.append(entity)
        stage.eve._count = len(self.units)

        # Pad layers to 3 for editor compatibility if needed
        while len(stage.layers) < 3:
            stage.layers.append(Layer(0, 0))
        return stage

    @classmethod
    def from_stage(cls, stage):
        game = game_manager.get_current_game()
        
        # Star Frog 10x always works with 3 layers for I/O
        layer_count = 3 if game.name == 'star_frog_10x' else game.get('pxpack_layers', 3)

        pxpack = cls()
        pxpack.description, pxpack.spritesheet = stage.description, stage.spritesheet
        pxpack.left_field, pxpack.right_field = stage.left_field, stage.right_field
        pxpack.up_field, pxpack.down_field = stage.up_field, stage.down_field
        pxpack.area_x, pxpack.area_y, pxpack.area_no = stage.area_x, stage.area_y, stage.area_no
        pxpack.bg_r, pxpack.bg_g, pxpack.bg_b = stage.bg_r, stage.bg_g, stage.bg_b
        pxpack.layers = [cls.Layer() for _ in range(layer_count)]
        for i, layer_model in enumerate(pxpack.layers):
            if i < len(stage.layers):
                layer = stage.layers[i]
                
                # An empty layer is defined by having no tileset assigned.
                # If partsName is missing, we MUST force width and height to 0.
                if layer.partsName and layer.width > 0 and layer.height > 0:
                    layer_model.width, layer_model.height = layer.width, layer.height
                    layer_model.tiles = layer.tiles
                    layer_model.partsName = layer.partsName
                    layer_model.visibility, layer_model.scrolltype = layer.visibility, layer.scrolltype
                else:
                    layer_model.width, layer_model.height = 0, 0
                    layer_model.tiles = []
                    layer_model.partsName = "" # Ensure partsName is empty
                    layer_model.visibility, layer_model.scrolltype = layer.visibility, layer.scrolltype
                    
        for entity in stage.eve.units:
            unit = cls.Unit(entity.bits, entity.type1, entity.param2, entity.x, entity.y, entity.flag, entity.string, entity.id)
            pxpack.units.append(unit)
        return pxpack

# --- Public Interface Functions ---

def load_stage(game_manager, stage_name, stage_table=None):
    game = game_manager.get_current_game()
    path = os.path.join(game.base_path, game.get('data_path'), game.get('stage_path'), stage_name + game.get('stage_ext'))
    return PxPack().load(path).to_stage(stage_name)

def save_stage(game_manager, stage):
    game = game_manager.get_current_game()
    path = os.path.join(game.base_path, game.get('data_path'), game.get('stage_path'), stage.name + game.get('stage_ext'))
    return PxPack.from_stage(stage).save(path)

import const

def load_attrs(game_manager, tileset_name, tileset_surface):
    """Loads attributes for a Kero Blaster tileset."""
    from pxMap import PxMapAttr
    
    game = game_manager.get_current_game()
    img_path_base = os.path.join(game.base_path, game.get('data_path'), game.get('image_path'))
    attr = PxMapAttr()

    attr_ext = game.get('attr_ext')
    if tileset_name:
        attr_path = os.path.join(img_path_base, tileset_name + attr_ext)
        if os.path.exists(attr_path):
            attr.load(attr_path)
            return attr

    # If file doesn't exist, create attributes based on the loaded image surface
    if tileset_surface:
        tile_width = game.get('tile_size', 8) * const.tileScale
        attr.width = tileset_surface.size[0] // tile_width
        attr.height = tileset_surface.size[1] // tile_width
        attr.tiles = [[0] * attr.width for _ in range(attr.height)]
    else:
        attr.width = 0
        attr.height = 0
        
    return attr

def save_attribute(game_manager, layer, path):
    """Saves a .pxattr file, handling variants for Kero Blaster and Rockfish."""
    import struct
    if not layer: return False
    
    try:
        game = game_manager.get_current_game()
        with open(path, 'wb') as f:
            is_multilayer_format = game.get('pxpack_layers', 1) > 1
            
            # Kero Blaster / SF11x have a header. Rockfish / SF10x do not.
            if is_multilayer_format:
                f.write(b"pxMAP01\0")
                f.write(struct.pack("<H", layer.width))
                f.write(struct.pack("<H", layer.height))
                f.write(struct.pack("<B", 0)) # Type byte is usually 0
            else:
                f.write(struct.pack("<H", layer.width))
                f.write(struct.pack("<H", layer.height))

            # The tile data is written the same way for all.
            for row in layer.tiles:
                f.write(bytes(row))

        print(f"Successfully saved attribute file: {os.path.basename(path)}")
        return True
    except (IOError, OSError) as e:
        print(f"Error saving attribute file {path}: {e}")
        return False