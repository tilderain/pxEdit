
class Entity:
    """Represents a single entity in a stage."""
    def __init__(self, id, x, y, flags=0, event=0):
        self.id = id
        self.x = x
        self.y = y
        self.flags = flags
        self.event = event
        self.attributes = {}

class Layer:
    """Represents a single tile layer in a stage."""
    def __init__(self, width, height):
        self.width = width
        self.height = height
        # Correctly initialize a 2D list to prevent row-sharing bugs
        self.tiles = [[0] * width for _ in range(height)] if width > 0 and height > 0 else []
        
        # Properties for compatibility with different game formats
        self.partsName = ""  # For Kero Blaster tilesets
        self.scrolltype = 0
        self.visibility = 0

    def modify(self, tiles_to_modify):
        """
        Modifies the tile data for the layer. This method was missing after refactoring.
        :param tiles_to_modify: A list of tiles to change.
               Format: [[[map_x, map_y], [tileset_x, tileset_y]], ...]
        """
        for tile_data in tiles_to_modify:
            map_pos = tile_data[0]
            tileset_pos = tile_data[1]

            map_x, map_y = map_pos[0], map_pos[1]
            tileset_x, tileset_y = tileset_pos[0], tileset_pos[1]

            # Check bounds before modifying
            if 0 <= map_y < self.height and 0 <= map_x < self.width:
                # Convert the 2D tileset coordinate to a single byte value.
                # This assumes the tileset is 16 tiles wide, which is standard.
                tile_value = tileset_x + (tileset_y * 16)
                self.tiles[map_y][map_x] = tile_value

class Stage:
    """Represents a full game stage, containing layers and entities."""
    def __init__(self, name, width, height):
        self.name = name
        self.width = width
        self.height = height
        
        self.spritesheet = ""
        self.bg_color = (0, 0, 0)
        
        # A list of Layer objects
        self.layers = []
        
        # Holds entity data (should be a PxEve object)
        self.eve = None
        
        # Properties for .pxpack (Kero Blaster) compatibility
        self.description = ""
        self.left_field = ""
        self.right_field = ""
        self.up_field = ""
        self.down_field = ""
        self.area_x = 0
        self.area_y = 0
        self.area_no = 0

    def set_background_color(self, r, g, b):
        self.bg_color = (r, g, b)