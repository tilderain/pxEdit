import os
import struct
from stage import Stage, Layer, Entity
from pxMap import PxEve, PxMap, PxMapAttr

# --- Cave Story Format Model ---

class CaveStoryFormat:
    def __init__(self):
        self.pxm = PxMap()
        self.pxa = PxMapAttr()
        self.entities = []

    def load(self, game_manager, stage_name):
        """Loads data from .pxm, .pxa, and .pxe files into this object."""
        game = game_manager.get_current_game()
        base_path = os.path.join(game.base_path, game.get('data_path'), game.get('stage_path'))
        
        map_path = os.path.join(base_path, stage_name + game.get('stage_ext'))
        entities_path = os.path.join(base_path, stage_name + game.get('entity_ext'))

        if not self.pxm.load(map_path, printError=False):
            raise FileNotFoundError(f"Could not load map file: {map_path}")
        
        self.entities = self._load_entities(entities_path)
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
        stage.spritesheet = "Prt" + stage_name
        
        stage.layers = [Layer(self.pxm.width, self.pxm.height), Layer(0, 0), Layer(0, 0)]
        stage.layers[0].tiles = self.pxm.tiles
        
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

# --- Public Interface Functions (Now extremely simple) ---

def load_stage(game_manager, stage_name):
    return CaveStoryFormat().load(game_manager, stage_name).to_stage(stage_name)

def save_stage(game_manager, stage):
    return CaveStoryFormat.from_stage(stage).save(game_manager, stage.name)