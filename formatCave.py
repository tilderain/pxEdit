import os
import struct
from stage import Stage, Layer, Entity
from pxMap import PxEve, PxMap, PxMapAttr

# --- Cave Story Format Model ---

class CaveStoryFormat:
    def __init__(self):
        self.pxm = PxMap()
        self.pxm_back = PxMap()  # For the background layer map
        self.pxa = PxMapAttr()  
        self.tileset_name = ""
        self.entities = []

    def load(self, game_manager, stage_name, stage_table=None):
        """Loads data from .pxm, .pxa, and .pxe files into this object, using stage.tbl info."""
        game = game_manager.get_current_game()
        
        # Determine the base path for stage-related files.
        stage_files_path = os.path.join(game.base_path, game.get('data_path'), game.get('stage_path'))
        
        map_filename = stage_name
        back_map_filename = ""
        
        # Find stage entry in stage.tbl by its map name (e.g., "Almond")
        tbl_entry = None
        if stage_table:
            for entry in stage_table:
                # stage_name is the map name used for loading, e.g., "Almond"
                if entry.map == stage_name:
                    tbl_entry = entry
                    break
        
        if tbl_entry:
            print(f"Found '{stage_name}' in stage.tbl. Using specified files.")
            # --- THE FIX: Prepend the 'Prt' prefix ---
            # The table stores 'Almond', the filename is 'PrtAlmond'.
            self.tileset_name = "Prt" + tbl_entry.parts
            
            map_filename = tbl_entry.map
            
            # Backgrounds also need their prefix, but are located in the same stage folder.
            if tbl_entry.back:
                 back_map_filename = tbl_entry.back
        else:
            print(f"'{stage_name}' not in stage.tbl. Guessing filenames.")
            # Fallback for custom maps: guess the tileset name
            self.tileset_name = "Prt" + stage_name

        # --- Load main map and entities ---
        map_path = os.path.join(stage_files_path, map_filename + game.get('stage_ext'))
        entities_path = os.path.join(stage_files_path, map_filename + game.get('entity_ext'))

        if not self.pxm.load(map_path, printError=False):
            raise FileNotFoundError(f"Could not load main map file: {map_path}")
        
        self.entities = self._load_entities(entities_path)

        # --- Load background map (if specified and exists) ---
        if back_map_filename:
            back_map_path = os.path.join(stage_files_path, back_map_filename + game.get('stage_ext'))
            # It's okay if this fails; many stages don't have a background layer.
            self.pxm_back.load(back_map_path, printError=False)

        return self

    def save(self, game_manager, stage_name):
        """Saves data from this object into .pxm, .pxa, and .pxe files."""
        game = game_manager.get_current_game()
        base_path = os.path.join(game.base_path, game.get('data_path'), game.get('stage_path'))
        
        self.pxm.save(os.path.join(base_path, stage_name + game.get('stage_ext')))
        self._save_entities(self.entities, os.path.join(base_path, stage_name + game.get('entity_ext')))
        # Cave Story often requires a dummy .pxa file, so we'll save one too
        self.pxa.save(os.path.join(base_path, stage_name + game.get('attr_ext')))
        return self

    def to_stage(self, stage_name):
        """Translates this CaveStoryFormat object into a universal Stage object."""
        stage = Stage(stage_name, self.pxm.width, self.pxm.height)
        stage.eve = PxEve()
        
        # Initialize 3 layers
        stage.layers = [Layer(0, 0) for _ in range(3)]

        # Layer 0: Main map. Its partsName is the primary tileset for the stage.
        stage.layers[0] = Layer(self.pxm.width, self.pxm.height)
        stage.layers[0].tiles = self.pxm.tiles
        stage.layers[0].partsName = self.tileset_name
        
        # Layer 1: Background map (if loaded). It reuses the main tileset.
        if self.pxm_back and self.pxm_back.width > 0:
            stage.layers[1] = Layer(self.pxm_back.width, self.pxm_back.height)
            stage.layers[1].tiles = self.pxm_back.tiles
            stage.layers[1].partsName = self.tileset_name # Re-uses main tileset
        
        stage.eve.units = self.entities
        stage.eve._count = len(self.entities)
        return stage

    @classmethod
    def from_stage(cls, stage):
        """Translates a universal Stage object into a CaveStoryFormat object."""
        model = cls()
        if len(stage.layers) > 0:
            layer = stage.layers[0]
            model.pxm.width, model.pxm.height, model.pxm.tiles = layer.width, layer.height, layer.tiles
        model.entities = stage.eve.units
        return model
        
    def _load_entities(self, path):
        entities = []
        try:
            with open(path, 'rb') as f:
                if f.read(3) != b'PXE': raise ValueError("Invalid PXE file format")
                f.read(1)
                count = struct.unpack('<I', f.read(4))[0]
                for i in range(count):
                    data = f.read(12)
                    if len(data) < 12: break
                    x, y, flag, event, type1, bits = struct.unpack('<HHHHHH', data)
                    entity = Entity(type1, x, y, flag, event, id=i)
                    entity.bits = bits
                    entity.param2 = event
                    entities.append(entity)
        except FileNotFoundError:
            print(f"Entity file not found, creating new list: {path}")
        except (ValueError, struct.error) as e:
            print(f"Error parsing entity file {path}: {e}")
        return entities

    def _save_entities(self, entities, path):
        try:
            with open(path, 'wb') as f:
                f.write(b'PXE\x31'); f.write(struct.pack('<I', len(entities)))
                for entity in entities:
                    f.write(struct.pack('<HHHHHH', entity.x, entity.y, entity.flag, entity.param2, entity.type1, entity.bits))
        except (ValueError, struct.error) as e:
            print(f"Error writing entity file {path}: {e}")
            return False
        return True

# --- Public Interface Functions ---

def load_stage(game_manager, stage_name, stage_table=None):
    return CaveStoryFormat().load(game_manager, stage_name, stage_table).to_stage(stage_name)

def save_stage(game_manager, stage):
    return CaveStoryFormat.from_stage(stage).save(game_manager, stage.name)

def load_attrs(game_manager, tileset_name, tileset_surface):
    """Loads attributes for a Cave Story tileset."""
    from pxMap import PxMapAttr
    import const
    
    game = game_manager.get_current_game()
    # For Cave Story, attributes are in the 'Stage' folder, which img_path_base points to.
    img_path_base = os.path.join(game.base_path, game.get('data_path'), game.get('image_path'))
    attr = PxMapAttr()
    attr_loaded_from_file = False

    attr_ext = game.get('attr_ext')
    if tileset_name:
        # --- THE FIX ---
        # The attribute filename is based on the map name, not the prefixed tileset name.
        # We strip the common "Prt" prefix to get the base name.
        attr_filename_base = tileset_name
        if attr_filename_base.startswith("Prt"):
            attr_filename_base = attr_filename_base[3:]
        # ----------------

        attr_path = os.path.join(img_path_base, attr_filename_base + attr_ext)
        if os.path.exists(attr_path):
            try:
                with open(attr_path, 'rb') as f:
                    data = f.read()
                    if len(data) >= 256:
                        attr.width = 16
                        attr.height = 16
                        attr.tiles = [list(data[i:i+16]) for i in range(0, 256, 16)]
                        attr_loaded_from_file = True
                        print(f"Successfully loaded attributes from {os.path.basename(attr_path)}")
                    else:
                         print(f"Warning: Attribute file '{os.path.basename(attr_path)}' is smaller than 256 bytes. Ignoring.")
            except (IOError, OSError) as e:
                print(f"Error reading attribute file {attr_path}: {e}")
    
    # Fallback: if no .pxa was loaded, create attributes based on the tileset surface
    if not attr_loaded_from_file:
        if tileset_surface:
            tile_width = game.get('tile_size', 8) * const.tileScale
            attr.width = tileset_surface.size[0] // tile_width
            attr.height = tileset_surface.size[1] // tile_width
            attr.tiles = [[0] * attr.width for _ in range(attr.height)]
        else:
            attr.width = 0
            attr.height = 0
    
    return attr