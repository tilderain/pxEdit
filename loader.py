import os
import struct
import mmap
from stage import Stage, Layer, Entity
from pxMap import PxEve

def read_pixel_string(stream):
    length = stream.read_byte()
    if length >= 32: return ""
    string = stream.read(length)
    return string.decode("shift-jis")

def read_int(stream, length):
    return int.from_bytes(stream.read(length), byteorder="little")

class PxPackUnit:
    def __init__(self, bits, code_char, param2, x, y, flag, string, id):
        self.bits = bits
        self.type1 = code_char
        self.param2 = param2
        self.x = x
        self.y = y
        self.flag = flag
        self.string = string
        self.id = id

class PxPackLayer:
    def __init__(self):
        self.partsName = None
        self.scrolltype = 0
        self.visibility = 0
        self.width = 16
        self.height = 16
        self.type = 0
        self.tiles = [[0] * self.width] * self.height

    def load_from_pack(self, stream):
        self.tiles = []
        stream.read(8)  # PXMAP01
        self.width = read_int(stream, 2)
        self.height = read_int(stream, 2)

        if self.width * self.height == 0: return True

        self.type = read_int(stream, 1)
        if self.type == 0:
            for i in range(self.height):
                byt = stream.read(self.width)
                self.tiles.append([tile for tile in byt])
            return True

class PxPack:
    def __init__(self):
        self.description = None
        self.left_field = None
        self.right_field = None
        self.up_field = None
        self.down_field = None
        self.spritesheet = None
        self.area_x = None
        self.area_y = None
        self.area_no = None
        self.bg_r = None
        self.bg_g = None
        self.bg_b = None
        self.layers = []
        self.units = []
        self._entity_count = 0

    def load(self, path):
        try:
            f = open(path, 'rb')
            stream = mmap.mmap(f.fileno(), 0, access=mmap.ACCESS_READ)
        except (OSError, IOError) as e:
            raise FileNotFoundError(f"Error while opening {path}: {e}")

        LAYER_COUNT = 3

        stream.seek(16)

        self.description = read_pixel_string(stream)
        self.left_field = read_pixel_string(stream)
        self.right_field = read_pixel_string(stream)
        self.up_field = read_pixel_string(stream)
        self.down_field = read_pixel_string(stream)
        self.spritesheet = read_pixel_string(stream)

        self.area_x = read_int(stream, 2)
        self.area_y = read_int(stream, 2)
        self.area_no = read_int(stream, 1)

        self.bg_r = read_int(stream, 1)
        self.bg_g = read_int(stream, 1)
        self.bg_b = read_int(stream, 1)

        for i in range(LAYER_COUNT):
            layer = PxPackLayer()
            layer.partsName = read_pixel_string(stream)
            layer.visibility = read_int(stream, 1)
            layer.scrolltype = read_int(stream, 1)
            self.layers.append(layer)

        for i in range(LAYER_COUNT):
            layer = self.layers[i]
            layer.load_from_pack(stream)

        entity_count = read_int(stream, 2)
        for i in range(entity_count):
            bits = read_int(stream, 1)
            code_char = read_int(stream, 1)
            param2 = read_int(stream, 1)
            x = read_int(stream, 2)
            y = read_int(stream, 2)
            flag = read_int(stream, 2)
            string = read_pixel_string(stream)
            self.units.append(PxPackUnit(bits, code_char, param2, x, y, flag, string, self._entity_count))
            self._entity_count += 1

        stream.close()
        f.close()
        return True

import struct

class PxMap:
    def __init__(self):
        self.width = 0
        self.height = 0
        self.tiles = []

    def load(self, path):
        try:
            with open(path, 'rb') as f:
                # Check magic number "PXM"
                magic = f.read(3)
                if magic != b'PXM':
                    raise ValueError(f"Invalid PXM file format in {path}")

                # Skip one dummy byte
                f.read(1)

                # Read width and height (2 bytes each, little-endian)
                width_bytes = f.read(2)
                height_bytes = f.read(2)
                self.width = int.from_bytes(width_bytes, byteorder='little')
                self.height = int.from_bytes(height_bytes, byteorder='little')

                # Read tile data
                data = f.read(self.width * self.height)
                for i in range(self.height):
                    start = i * self.width
                    end = start + self.width
                    self.tiles.append(list(data[start:end]))
        except (OSError, IOError) as e:
            raise FileNotFoundError(f"Error while opening {path}: {e}")
        except (ValueError, struct.error) as e:
            print(f"Error parsing map file {path}: {e}")
        return True

class PxMapAttr: #use the same class for both
    def __init__(self):
        self.width = None
        self.height = None
        self.tiles = []
    def load(self, path):
        try:
            with open(path, 'rb') as f:
                data = f.read()
        except (OSError, IOError) as e:
            raise FileNotFoundError(f"Error while opening {path}: {e}")
        
        self.width = int.from_bytes(data[0:2], byteorder='little')
        self.height = int.from_bytes(data[2:4], byteorder='little')
        for i in range(self.height):
            self.tiles.append(list( data[4+i*self.width:
                                    4+(i*self.width)+self.width] ))
        return True

class Loader:
    def __init__(self, game_manager):
        self.game_manager = game_manager

    def load_stage(self, stage_name):
        game = self.game_manager.get_current_game()
        if not game.base_path:
            raise ValueError("Game path not set.")

        if game.name == 'kero_blaster':
            stage_path = os.path.join(
                game.base_path,
                game.get('data_path'),
                game.get('stage_path'),
                stage_name + game.get('stage_ext')
            )
            return self._load_kero_blaster_stage(stage_path, stage_name)
        elif game.name == 'cave_story':
            return self._load_cave_story_stage(stage_name)
        else:
            raise NotImplementedError(f"Loading for game '{game.name}' is not implemented.")

    def _load_kero_blaster_stage(self, path, name):
        pxpack = PxPack()
        pxpack.load(path)

        # Convert PxPack to universal Stage format
        stage = Stage(name, pxpack.layers[0].width, pxpack.layers[0].height)
        stage.eve = PxEve()
        stage.spritesheet = pxpack.layers[0].partsName # Set the spritesheet name
        stage.set_background_color(pxpack.bg_r, pxpack.bg_g, pxpack.bg_b)
        
        # Layers
        stage.layers = []
        for i in range(len(pxpack.layers)):
            l = pxpack.layers[i]
            new_layer = Layer(l.width, l.height)
            new_layer.tiles = l.tiles
            stage.layers.append(new_layer)
        # Ensure 3 layers exist for consistency, even if empty
        while len(stage.layers) < 3:
            stage.layers.append(Layer(0, 0))

        # Entities
        for unit in pxpack.units:
            # unit.id is the unique editor id from the PxPack loader
            entity = Entity(unit.type1, unit.x, unit.y, unit.flag, id=unit.id)
            entity.bits = unit.bits
            entity.param2 = unit.param2
            entity.string = unit.string
            stage.eve.units.append(entity)
        stage.eve._count = len(pxpack.units)

        return stage

    def _load_cave_story_stage(self, stage_name):
        game = self.game_manager.get_current_game()
        base_path = os.path.join(game.base_path, game.get('data_path'))

        map_path = os.path.join(base_path, game.get('stage_path'), stage_name + game.get('stage_ext'))
        attr_path = os.path.join(base_path, game.get('stage_path'), stage_name + game.get('attr_ext'))
        entities_path = os.path.join(base_path, game.get('stage_path'), stage_name + game.get('entity_ext'))

        # Load map data
        pxm = PxMap()
        pxm.load(map_path)
        
        stage = Stage(stage_name, pxm.width, pxm.height)
        stage.eve = PxEve()
        # For Cave Story, the spritesheet is usually derived from the stage name itself
        stage.spritesheet = "Prt" + stage_name # Example: PrtAlmond.pbm

        stage.layers = [Layer(0,0) for _ in range(3)] # Init 3 layers
        stage.layers[0] = Layer(pxm.width, pxm.height)
        stage.layers[0].tiles = pxm.tiles

        # Load attribute data
        pxa = PxMapAttr()
        pxa.load(attr_path)
        #stage.layers[2] = Layer(pxa.width, pxa.height)
        #stage.layers[2].tiles = pxa.tiles
        
        # Load entities
        stage.eve.units = self._load_cave_story_entities(entities_path)
        stage.eve._count = len(stage.eve.units)

        return stage

    def _load_cave_story_entities(self, path):
        entities = []
        try:
            with open(path, 'rb') as f:
                # Read header
                magic = f.read(4)
                if magic[0:3] != b'PXE':
                    raise ValueError("Invalid PXE file format")
                
                count = struct.unpack('<I', f.read(4))[0]

                for i in range(count):
                    data = f.read(12) # 6 * 2 bytes
                    if len(data) < 12:
                        break # End of file
                    
                    x, y, code_flag, code_event, code_char, bits = struct.unpack('<HHHHHH', data)
                    
                    entity = Entity(code_char, x, y, code_flag, code_event, id=i)
                    entity.bits = bits
                    entities.append(entity)
        except FileNotFoundError:
            print(f"Entity file not found: {path}")
        except (ValueError, struct.error) as e:
            print(f"Error parsing entity file {path}: {e}")

        return entities