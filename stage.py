class Entity:
	"""Represents a single, unified entity in a stage."""
	def __init__(self, type1, x, y, flag=0, event=0, id=0):
		# --- Common properties ---
		self.type1 = type1	  # The entity type ID (e.g., 4 for a Critter).
		self.x = x
		self.y = y
		self.flag = flag		# `flag` in KB, `code_flag` in CS.
		self.id = id			# A unique ID for editor operations (selection, undo, etc.).

		# --- Game-specific or extended properties ---
		self.bits = 0		   # `bits` is used in both games.
		self.event = event	  # For Cave Story's `code_event`.
		self.param2 = 0		 # For Kero Blaster's `param2`.
		self.string = ""		# For Kero Blaster's `string`.

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
	def resize(self, new_width, new_height):
		"""Resizes the tile grid, preserving existing tiles."""
		if new_width < 0 or new_height < 0: return

		new_tiles = []
		for y in range(new_height):
			if y >= self.height:
				# Add a new, empty row if the new height is greater
				new_tiles.append([0] * new_width)
			else:
				# Copy and adjust an existing row
				row = self.tiles[y][:new_width]
				if new_width > self.width:
					# Pad the row with empty tiles if the new width is greater
					row.extend([0] * (new_width - self.width))
				new_tiles.append(row)
		
		self.tiles = new_tiles
		self.width = new_width
		self.height = new_height

class Stage:
	"""Represents a full game stage, containing layers and entities."""
	def __init__(self, name, width, height):
		self.name = name
		self.width = width
		self.height = height
		
		self.spritesheet = ""
		
		self.bg_r = 0
		self.bg_g = 0
		self.bg_b = 0
		# -----------------------
		
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

	# DELETE THE ENTIRE set_background_color METHOD