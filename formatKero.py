import os
import struct
import mmap
from stage import Stage, Layer, Entity
from pxMap import PxEve

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

        def load_from_pack(self, stream):
            stream.read(8) # pxMAP01
            self.width, self.height = read_int(stream, 2), read_int(stream, 2)
            if self.width * self.height == 0: return True
            self.type = read_int(stream, 1)
            if self.type == 0: self.tiles = [list(stream.read(self.width)) for _ in range(self.height)]
            return True

        def save_to_pack(self, f):
            f.write(b"pxMAP01\0"); f.write(struct.pack("<HH", self.width, self.height))
            if self.width * self.height == 0: return
            f.write(struct.pack("<B", self.type))
            if self.type == 0: [f.write(bytes(y)) for y in self.tiles]

    def __init__(self):
        self.magic = b"PXPACK121127a**\0"
        self.description, self.spritesheet = "", ""
        self.left_field, self.right_field, self.up_field, self.down_field = "", "", "", ""
        self.area_x, self.area_y, self.area_no = 0, 0, 0
        self.bg_r, self.bg_g, self.bg_b = 0, 0, 0
        self.layers = []
        self.units = []

    def load(self, path):
        """Loads data from a .pxpack file into this object."""
        with open(path, 'rb') as f, mmap.mmap(f.fileno(), 0, access=mmap.ACCESS_READ) as stream:
            stream.seek(16)
            
            # --- THIS IS THE FIX: Read fields in the correct order ---
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
            
            self.layers = [self.Layer() for _ in range(3)]
            for layer in self.layers:
                layer.partsName = read_pixel_string(stream)
                layer.visibility = read_int(stream, 1)
                layer.scrolltype = read_int(stream, 1)

            for layer in self.layers:
                layer.load_from_pack(stream)
            
            entity_count = read_int(stream, 2)
            for i in range(entity_count):
                bits = read_int(stream, 1)
                type1 = read_int(stream, 1)
                param2 = read_int(stream, 1)
                x = read_int(stream, 2)
                y = read_int(stream, 2)
                flag = read_int(stream, 2)
                string = read_pixel_string(stream)
                self.units.append(self.Unit(bits, type1, param2, x, y, flag, string, i))
        return self

    def save(self, path):
        """Saves data from this object into a .pxpack file."""
        with open(path, 'wb') as f:
            f.write(self.magic)
            
            # --- THIS IS THE FIX: Write fields in the correct order ---
            write_pixel_string(f, self.description)
            write_pixel_string(f, self.left_field)
            write_pixel_string(f, self.right_field)
            write_pixel_string(f, self.up_field)
            write_pixel_string(f, self.down_field)
            write_pixel_string(f, self.spritesheet)

            f.write(struct.pack("<H", self.area_x))
            f.write(struct.pack("<H", self.area_y))
            f.write(struct.pack("<B", self.area_no))
            f.write(struct.pack("<BBB", self.bg_r, self.bg_g, self.bg_b))
            
            for layer in self.layers:
                write_pixel_string(f, layer.partsName)
                f.write(struct.pack("<BB", layer.visibility, layer.scrolltype))

            for layer in self.layers:
                layer.save_to_pack(f)
            
            f.write(struct.pack("<H", len(self.units)))
            for unit in self.units:
                f.write(struct.pack("<BBB", unit.bits, unit.type1, unit.param2))
                f.write(struct.pack("<hhH", unit.x, unit.y, unit.flag))
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
        stage.set_background_color(self.bg_r, self.bg_g, self.bg_b)
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
        return stage

    @classmethod
    def from_stage(cls, stage):
        pxpack = cls()
        pxpack.description, pxpack.spritesheet = stage.description, stage.spritesheet
        pxpack.left_field, pxpack.right_field = stage.left_field, stage.right_field
        pxpack.up_field, pxpack.down_field = stage.up_field, stage.down_field
        pxpack.area_x, pxpack.area_y, pxpack.area_no = stage.area_x, stage.area_y, stage.area_no
        pxpack.bg_r, pxpack.bg_g, pxpack.bg_b = stage.bg_color
        pxpack.layers = [cls.Layer() for _ in range(3)]
        for i, layer_model in enumerate(pxpack.layers):
            if i < len(stage.layers):
                layer = stage.layers[i]
                
                # --- THIS IS THE FIX ---
                # An empty layer in Kero Blaster is defined by having no tileset assigned.
                # If partsName is missing, we MUST force width and height to 0.
                if layer.partsName and layer.width > 0 and layer.height > 0:
                    layer_model.width, layer_model.height = layer.width, layer.height
                    layer_model.tiles = layer.tiles
                    layer_model.partsName = layer.partsName
                    layer_model.visibility, layer_model.scrolltype = layer.visibility, layer.scrolltype
                else:
                    # This is a guaranteed empty layer.
                    layer_model.width, layer_model.height = 0, 0
                    layer_model.tiles = []
                    layer_model.partsName = "" # Ensure partsName is empty
                    layer_model.visibility, layer_model.scrolltype = layer.visibility, layer.scrolltype
                    
        for entity in stage.eve.units:
            unit = cls.Unit(entity.bits, entity.type1, entity.param2, entity.x, entity.y, entity.flag, entity.string, entity.id)
            pxpack.units.append(unit)
        return pxpack


# --- Public Interface Functions ---

def load_stage(game_manager, stage_name):
    game = game_manager.get_current_game()
    path = os.path.join(game.base_path, game.get('data_path'), game.get('stage_path'), stage_name + game.get('stage_ext'))
    return PxPack().load(path).to_stage(stage_name)

def save_stage(game_manager, stage):
    game = game_manager.get_current_game()
    path = os.path.join(game.base_path, game.get('data_path'), game.get('stage_path'), stage.name + game.get('stage_ext'))
    return PxPack.from_stage(stage).save(path)