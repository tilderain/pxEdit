import os
import struct
from stage import Stage, Layer, Entity

def write_pixel_string(fp, string):
    if string:
        length = len(string.encode("shift-jis"))
        fp.write(struct.pack("<B", length))
        fp.write(bytes(string.encode("shift-jis")))
    else:
        fp.write(struct.pack("<B", 0))


pxmapMagic = b"pxMAP01\0"
pxpackMagic = b"PXPACK121127a**\0"

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
        self.partsName = ""
        self.scrolltype = 0
        self.visibility = 0
        self.width = 0
        self.height = 0
        self.type = 0
        self.tiles = []

    def save_to_pack(self, f):
        f.write(pxmapMagic)
        f.write(struct.pack("<H", self.width))
        f.write(struct.pack("<H", self.height))

        if self.width * self.height == 0: return

        f.write(struct.pack("<B", self.type))

        if self.type == 0:
            for y in self.tiles:
                f.write(bytes(y))

class PxPack:
    def __init__(self):
        self.description = ""
        self.left_field = ""
        self.right_field = ""
        self.up_field = ""
        self.down_field = ""
        self.spritesheet = ""
        self.area_x = 0
        self.area_y = 0
        self.area_no = 0
        self.bg_r = 0
        self.bg_g = 0
        self.bg_b = 0
        self.layers = []
        self.units = []

    def save(self, path):
        try:
            with open(path, 'wb') as f:
                f.write(pxpackMagic)
                write_pixel_string(f, self.description)
                write_pixel_string(f, self.left_field)
                write_pixel_string(f, self.right_field)
                write_pixel_string(f, self.up_field)
                write_pixel_string(f, self.down_field)
                write_pixel_string(f, self.spritesheet)

                f.write(struct.pack("<H", self.area_x))
                f.write(struct.pack("<H", self.area_y))
                f.write(struct.pack("<B", self.area_no))

                f.write(struct.pack("<B", self.bg_r))
                f.write(struct.pack("<B", self.bg_g))
                f.write(struct.pack("<B", self.bg_b))

                LAYER_COUNT = 3

                for i in range(LAYER_COUNT):
                    layer = self.layers[i]
                    write_pixel_string(f, layer.partsName)
                    f.write(struct.pack("<B", layer.visibility))
                    f.write(struct.pack("<B", layer.scrolltype))
                
                for i in range(LAYER_COUNT):
                    self.layers[i].save_to_pack(f)

                f.write(struct.pack("<H", len(self.units)))
                for o in self.units:
                    f.write(struct.pack("<B", o.bits))
                    f.write(struct.pack("<B", o.type1))
                    f.write(struct.pack("<B", o.param2))
                    f.write(struct.pack("<h", o.x))
                    f.write(struct.pack("<h", o.y))
                    f.write(struct.pack("<H", o.flag))
                    write_pixel_string(f, o.string)
        except (OSError, IOError) as e:
            print(f"Error while saving {path}: {e}")
            return False
        return True

class PxMapSave:
    def __init__(self):
        self.width = 0
        self.height = 0
        self.tiles = []

    def save(self, path):
        try:
            with open(path, 'wb') as f:
                # Write the required header for .pxm files
                f.write(b'PXM') # 3-byte magic number
                f.write(b'\x01') # 1-byte dummy data

                # Write dimensions and tile data
                f.write(struct.pack("<h", self.width))
                f.write(struct.pack("<h", self.height))
                for y in self.tiles:
                    f.write(bytes(y))
        except (OSError, IOError) as e:
            print(f"Error while saving {path}: {e}")
            return False
        return True

class PxMapAttr:
    def __init__(self):
        self.width = 0
        self.height = 0
        self.tiles = []

    def save(self, path):
        try:
            with open(path, 'wb') as f:
                f.write(struct.pack("<h", self.width))
                f.write(struct.pack("<h", self.height))
                for y in self.tiles:
                    f.write(bytes(y))
        except (OSError, IOError) as e:
            print(f"Error while saving {path}: {e}")
            return False
        return True

class Saver:
    def __init__(self, game_manager):
        self.game_manager = game_manager

    def save_stage(self, stage):
        game = self.game_manager.get_current_game()
        if not game.base_path:
            raise ValueError("Game path not set.")

        if game.name == 'kero_blaster':
            stage_path = os.path.join(
                game.base_path,
                game.get('data_path'),
                game.get('stage_path'),
                stage.name + game.get('stage_ext')
            )
            return self._save_kero_blaster_stage(stage, stage_path)
        elif game.name == 'cave_story':
            return self._save_cave_story_stage(stage)
        else:
            raise NotImplementedError(f"Saving for game '{game.name}' is not implemented.")

    def _save_kero_blaster_stage(self, stage, path):
        pxpack = PxPack()

        # For now, we'll just create 3 empty layers, since the loader creates them.
        for _ in range(3):
            pxpack.layers.append(PxPackLayer())

        # Convert universal Stage to PxPack format
        if len(stage.layers) > 0 and stage.layers[0]:
            layer = pxpack.layers[0]
            layer.width = stage.layers[0].width
            layer.height = stage.layers[0].height
            layer.tiles = stage.layers[0].tiles

        if len(stage.layers) > 1 and stage.layers[1]:
            layer = pxpack.layers[1]
            layer.width = stage.layers[1].width
            layer.height = stage.layers[1].height
            layer.tiles = stage.layers[1].tiles

        if len(stage.layers) > 2 and stage.layers[2]:
            layer = pxpack.layers[2]
            layer.width = stage.layers[2].width
            layer.height = stage.layers[2].height
            layer.tiles = stage.layers[2].tiles

        for entity in stage.eve.units:
            unit = PxPackUnit(
                entity.attributes.get('bits', 0),
                entity.id,
                entity.attributes.get('param2', 0),
                entity.x,
                entity.y,
                entity.flags,
                entity.attributes.get('string', ""),
                0 # id is not saved in the same way
            )
            pxpack.units.append(unit)

        pxpack.save(path)
        print(f"Stage saved to {path}")
        return True

    def _save_cave_story_stage(self, stage):
        game = self.game_manager.get_current_game()
        base_path = os.path.join(game.base_path, game.get('data_path'))

        map_path = os.path.join(base_path, game.get('stage_path'), stage.name + game.get('stage_ext'))
        attr_path = os.path.join(base_path, game.get('stage_path'), stage.name + game.get('attr_ext'))
        entities_path = os.path.join(base_path, game.get('stage_path'), stage.name + game.get('entity_ext'))

        # Save map data
        if len(stage.layers) > 0 and stage.layers[0]:
            pxm = PxMapSave() # Use the correct class for saving .pxm files
            pxm.width = stage.layers[0].width
            pxm.height = stage.layers[0].height
            pxm.tiles = stage.layers[0].tiles
            pxm.save(map_path)
            print(f"Saved map to {map_path}")

        # Save attribute data
        if len(stage.layers) > 2 and stage.layers[2]:
            pxa = PxMapAttr()
            pxa.width = stage.layers[2].width
            pxa.height = stage.layers[2].height
            pxa.tiles = stage.layers[2].tiles
            pxa.save(attr_path)
            print(f"Saved attributes to {attr_path}")

        # Save entities
        self._save_cave_story_entities(stage.eve.units, entities_path)

        return True

    def _save_cave_story_entities(self, entities, path):
        try:
            with open(path, 'wb') as f:
                # Write header
                f.write(b'PXE\x31') # Assuming version 1
                f.write(struct.pack('<I', len(entities)))

                for entity in entities:
                    bits = entity.attributes.get('bits', 0)
                    data = struct.pack('<HHHHHH', entity.x, entity.y, entity.flags, entity.event, entity.id, bits)
                    f.write(data)
            print(f"Saved entities to {path}")
        except (ValueError, struct.error) as e:
            print(f"Error writing entity file {path}: {e}")