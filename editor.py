import const
import os
import glob, os
import copy
import pxMap
import interface
import sdl2

from datetime import datetime

from dataclasses import dataclass, field

@dataclass
class StageInfo:
    """Holds the decoded data for a single entry from stage.tbl."""
    index: int
    parts: str
    map: str
    bkType: int
    back: str
    npc: str
    boss: str
    boss_no: int
    name: str
    name_jp: str

from collections import Counter

from game import GameManager
from formats import FormatManager  # <-- IMPORT the new FormatManager

from stage import Stage, Layer, Entity

# Global instances of our new classes
from game import game_manager # <-- IMPORT the instance
format_manager = FormatManager(game_manager) # <-- CREATE the new manager

# Default game and path for now
# TODO: Make this user selectable
GAME_CHOICE = "guxt" # Options: "cave_story", "kero_blaster", "rockfish"

if GAME_CHOICE == "guxt":
	game_manager.set_game("guxt")
	game_manager.set_game_path("./guxt/")
	defaultStage = "1"
elif GAME_CHOICE == "cave_story":
	game_manager.set_game("cave_story")
	game_manager.set_game_path("./CaveStory/")
	defaultStage = "Almond"
elif GAME_CHOICE == "kero_blaster":
	game_manager.set_game("kero_blaster")
	game_manager.set_game_path("./Kero Blaster/")
	defaultStage = "01field1"
elif GAME_CHOICE == "rockfish":
	game_manager.set_game("rockfish")
	game_manager.set_game_path("./RockfishExe111127-ron/") # Adjust this path as needed
	defaultStage = "rmStart" # A common starting stage for Rockfish
else: # Fallback to a default
	game_manager.set_game("kero_blaster")
	game_manager.set_game_path("./Kero Blaster/")
	defaultStage = "01field1"

current_game_config = game_manager.get_current_game()

dataPath = os.path.join(game_manager.get_current_game().base_path, current_game_config.get('data_path'))
gamePath = game_manager.get_current_game().base_path
fieldPath = os.path.join(dataPath, current_game_config.get('stage_path'))
imgPath = os.path.join(dataPath, current_game_config.get('image_path'))

entityInfoName = current_game_config.get('entity_info')

backupFolderName = "backup"

pxPackExt = current_game_config.get('stage_ext')
pxAttrExt = current_game_config.get('attr_ext')
backupTimeFormat = "%Y%m%d-%H%M%S"

class StagePrj:
	def __init__(self, stageName, pack: Stage, tile_width):
		self.stageName = stageName
		self.pack = pack

		self.is_attribute_stage = False
		self.original_path = None # Store path for saving
		#TODO: for multiplayer
		self.oldEve = None
		self.oldMap = None

		# tileset texture
		self.parts = [None, None, None]

		self.scroll = 0
		self.hscroll = 0

		# x, y of drag selected tiles in the tileset
		self.selectedTiles = [[0, 0]]
		# x, y of drag selection mousedown
		self.selectedTilesStart = [0, 0]
		# x, y of drag selection mouse up
		self.selectedTilesEnd = [0, 0]

		self.selectedEntities = []
		self.selectedEntitiesDragStart = []

		self.undoStack = [None]
		self.undoPos = 0

		self.lastSavePos = 0
		self.lastBackupPos = 0

		# to not spam edit commands
		self.lastTileEdit = [None, None]

		self.attrs = [None, None, None]
		self.surfaces = [None, None, None]

		self.tileWidth = tile_width 

	def createMapSurface(self, layerNo):
		layer = self.pack.layers[layerNo]
		del self.surfaces[layerNo]
		self.surfaces.insert(layerNo, None)
		if layer.width * layer.height == 0: return
		
		self.surfaces[layerNo] = interface.gSprfactory.create_texture_sprite(interface.gRenderer, 
			(layer.width*self.tileWidth, layer.height*self.tileWidth), access=sdl2.SDL_TEXTUREACCESS_TARGET)
	
	def load(self):
		# This method is no longer responsible for loading the stage data itself.
		# It now assumes pack is already loaded.
		# It will load parts (tilesets) and create surfaces.
		
		#TODO: open dialogue box to see if there is a newer backup
			#read last modified date
			#Choose the backup you want to open.
		
		# --- THE FIX for LOOPING ---
		# Loop over the actual number of layers in the pack, not a fixed number.
		for i in range(len(self.pack.layers)):
			if self.loadParts(i):
				# Don't try to load attributes for a layer that has no tileset
				self.loadAttrs(i)
			self.createMapSurface(i)
			self.renderMapToSurface(i)
		# --------------------------
		return True

	def loadParts(self, layerNo):
		# This method is now simpler. It trusts that the format handler
		# has already figured out the correct tileset name.
		current_game_config = game_manager.get_current_game()
		
		if len(self.pack.layers) <= layerNo or not self.pack.layers[layerNo]:
			return False # This layer doesn't exist.
		
		tileset_name = self.pack.layers[layerNo].partsName

		# If the layer exists but has no assigned tileset, do nothing.
		if not tileset_name:
			return False

		# --- NEW LOADING LOGIC ---
		# Build a list of potential file paths to try in order.
		potential_paths = []
		if current_game_config.name == 'cave_story':
			# For Cave Story, prioritize .bmp then .pbm.
			# We now correctly use the full tileset_name ('PrtAlmond'), not the stage name.
			potential_paths.append(os.path.join(imgPath, tileset_name + ".bmp"))
			potential_paths.append(os.path.join(imgPath, tileset_name + ".pbm"))
		else:
			# For other games (like Kero Blaster), use the configured extension.
			tileset_ext = current_game_config.get('tileset_ext', '.png')
			potential_paths.append(os.path.join(imgPath, tileset_name + tileset_ext))

		# Loop through the paths and try to load the first one that exists.
		for path in potential_paths:
			try:
				if os.path.exists(path):
					self.parts[layerNo] = interface.gSprfactory.from_image(path)
					print(f"Successfully loaded tileset: {os.path.basename(path)}")
					return True
			except (OSError, IOError, sdl2.ext.SDLError):
				# This path failed (file corrupt, etc.), so we continue to the next one.
				continue
		
		# If the loop completes, it means no valid tileset could be loaded.
		print(f"Error: Could not find or load a valid tileset for '{tileset_name}'")
		self.parts[layerNo] = None # Ensure it's None on failure
		return False
	def loadAttrs(self, layerNo):
		tileset_name = self.pack.layers[layerNo].partsName
		tileset_surface = self.parts[layerNo]

		# Dispatch to the format manager to handle game-specific loading
		self.attrs[layerNo] = format_manager.load_attrs(tileset_name, tileset_surface)
		
		# Ensure we always have a valid PxMapAttr object, even if loading fails
		if not self.attrs[layerNo]:
			self.attrs[layerNo] = pxMap.PxMapAttr()
			
		return True
	def save(self):
		#if self.lastSavePos == self.undoPos: #TODO: and pxattr not modified
		if self.is_attribute_stage:
			print(f"--Saving attribute file {self.stageName}...--")
			# For attribute stages, the editable data is in Layer 1
			result = format_manager.save_attribute(self.pack.layers[1], self.original_path)
		else:
			print(f"--Saving stage {self.stageName}...--")
			# Use the existing pathway for normal stages
			result = format_manager.save_stage(self.pack)
		#TODO: save to _temp, rename existing to _temp2, rename _temp to orig and delete temp2

		#TODO: for save as, open all pxpacks in folder and change all references to new name
		if result:
			self.lastSavePos = self.undoPos
			self.lastBackupPos = self.undoPos
			print("saved.")
		
		return result
		
	def backup(self):
		#periodic backup...
		#if there are changes to the file, back it up
		#should follow format of backup_[mapname]_[yymmddhhmmss]
		#remove oldest backup (gxedit.backuplimit)
		#msg Backing up unsaved changes..
		if self.lastBackupPos == self.undoPos:
			return False

		print("-- Backing up stage {}... --".format(self.stageName))

		date = datetime.now()
		dateMin = date.strftime(backupTimeFormat)

		# This needs to use the saver as well
		# For now, hardcode for Kero Blaster
		backup_stage = copy.deepcopy(self.pack)
		backup_stage.name = dateMin + "_" + self.stageName
		format_manager.save_stage(backup_stage)
		
		self.lastBackupPos = self.undoPos

		#self.eve.save(dataPath + backupFolderName + "/" + dateMin + "_" + eventOut)
		#self.map.save(dataPath + backupFolderName + "/" + dateMin + "_" + mapOut)

		#backupId += 1

		return True


	def renderMapToSurface(self, layerNo):
		# This needs to use the pack layers
		map_layer = self.pack.layers[layerNo] if len(self.pack.layers) > layerNo else None

		if not map_layer or len(map_layer.tiles) == 0: return

		# --- THE FIX ---
		# Determine the correct tile size for this specific rendering operation.
		# For Layer 1 of an attribute stage, the tileset (attribute.png) is always 16x16.
		# For all other cases, use the game's default tile width.
		render_tile_size = 16 if self.is_attribute_stage and layerNo == 1 else self.tileWidth
		# ---------------

		print(f"DEBUG: map_layer.width: {map_layer.width}, map_layer.height: {map_layer.height}, len(map_layer.tiles): {len(map_layer.tiles)}")

		sdlrenderer = interface.gRenderer.sdlrenderer
		sdl2.SDL_SetRenderTarget(sdlrenderer, self.surfaces[layerNo].texture)
		sdl2.SDL_SetTextureBlendMode(self.surfaces[layerNo].texture, sdl2.SDL_BLENDMODE_BLEND)

		srcrect = sdl2.SDL_Rect(0, 0, render_tile_size, render_tile_size)
		dstrect = sdl2.SDL_Rect(0, 0, render_tile_size, render_tile_size)

		for y in range(map_layer.height):
			for x in range(map_layer.width):
				try:
					#TODO: detect if blank tile
					#if map.tiles[y][x] == 0: continue
					dstx = x * render_tile_size
					dsty = y * render_tile_size

					xx = map_layer.tiles[y][x] % 16 #the magic number so that each 4 bits in a byte corresponds to the x, y position in the tileset
					yy = map_layer.tiles[y][x] // 16

					srcx = xx * render_tile_size
					srcy = yy * render_tile_size

					srcrect.x = srcx
					srcrect.y = srcy
					dstrect.x = dstx
					dstrect.y = dsty
					sdl2.SDL_RenderCopy(sdlrenderer, self.parts[layerNo].texture, srcrect, dstrect)
				except IndexError as e:
					print(f"IndexError in renderMapToSurface at x={x}, y={y}: {e}")
					break # Break inner loop on error
				except Exception as e:
					print(f"Unexpected error in renderMapToSurface at x={x}, y={y}: {e}")
					break # Break inner loop on error
		sdl2.SDL_SetRenderTarget(sdlrenderer, None)
			
	
	def renderTileToSurface(self, x, y, tx, ty, layerNo):

		render_tile_size = 16 if self.is_attribute_stage and layerNo == 1 else self.tileWidth

		dstx = x * render_tile_size
		dsty = y * render_tile_size

		srcx = tx * render_tile_size
		srcy = ty * render_tile_size

		sdlrenderer = interface.gRenderer.sdlrenderer
		srcrect = (srcx, srcy, render_tile_size, render_tile_size)
		dstrect = (dstx, dsty, render_tile_size, render_tile_size)

		sdl2.SDL_SetRenderTarget(sdlrenderer, self.surfaces[layerNo].texture)

		sdl2.SDL_SetTextureBlendMode(self.parts[layerNo].texture, sdl2.SDL_BLENDMODE_NONE)

		interface.gRenderer.copy(self.parts[layerNo], srcrect, dstrect)

		sdl2.SDL_SetTextureBlendMode(self.parts[layerNo].texture, sdl2.SDL_BLENDMODE_BLEND)

		sdl2.SDL_SetRenderTarget(sdlrenderer, None)

	def addUndo(self, undo):
		self.undoPos += 1
		self.undoStack = self.undoStack[:self.undoPos]
		self.undoStack.append(undo)


class Editor:
	
	def __init__(self, game_manager, format_manager):
		self.game_manager = game_manager
		self.format_manager = format_manager 


		self.entityInfo = []
		self.stage_table = []
		self.stages = []

		self.curStage = 0

		self.content_y_offset = 24
		self.entity_sprite_size = 16 # Default, will be updated by update_tile_dimensions

		# Game-specific dimensions
		self.tileWidth = 16 # Default, will be updated

		# zoom level
		self.magnification = 3
		self.tilePaletteMag = 2
		self.entityPaletteMag = 1

		self.currentEntity = 0
		self.currentEditMode = const.EDIT_TILE
		self.currentTilePaintMode = const.PAINT_NORMAL
		self.currentLayer = 0
		
		self.visibleLayers = [True, True, True, True, False]
		self.tileSelectionUpdate = False
		#TODO: replace this with mouse1 behavior
		self.copyingTiles = False

		self.rectanglePaintBoxStart = [-1, -1]
		self.rectanglePaintBoxEnd = [-1, -1]

		self.selectionBoxStart = [-1, -1]
		self.selectionBoxEnd = [-1, -1]

		self.draggingEntities = False
		self.entDragPos = []

		self.copiedEntities = []

		#blinks on save
		self.saveTimer = 0

		# all ui windows
		self.elements = {}

		self.draggedElem = None
		self.dragX = 0
		self.dragY = 0

		# for text input or keyboard navigation
		self.focussedElem = None

		# currently mouse drag element
		self.activeElem = None

		self.fullscreen = False

		#TODO: toggle setting to display bg parallax as ingame
		self.parallax = True

		self.showTilePreview = True
		self.tileHighlightColor = [80, 180, 255]

		self.tileHighlightAnimate = True
		self.tileHighlightTimer = 0
		self.tileHighlightDir = 0

		self.backupLimit = 5
		self.backupMinutes = 5
		self.lastBackupTick = 0

		self.tooltipText = []
		self.tooltipStyle = const.STYLE_TOOLTIP_BLACK
		self.tooltipMag = 1
		#TODO:
		self.tooltipTimer = 0
		self.tooltipThreshold = 0

		self.multiplayerState = const.MULTIPLAYER_NONE
		self.socket = None
		self.socket_thread = None

		self.server_socket = None
		self.server_thread = None

		#ip, name, color? curstage:, mousexy pos, ping, last response time
		# this is a dict however numbers are names
		self.players = {}
		#unique id count of connected clients
		#just like in source the host is playerId 1
		self.playerId = 1
		self.serverPlayerNameTemp = ""
		self.lastMousePosTick = 0
		self.lastMousePos = (0, 0)
		self.tileRenderQueue = []

		self.tileWidth = 16
		self.tileWidth2 = 16

	def readEntityInfo(self):
		# This needs to use the game_manager to get the correct entity info file
		current_game_config = self.game_manager.get_current_game()
		entity_info_file = current_game_config.get('entity_info')
		entity_info_path = os.path.join(os.getcwd(), entity_info_file)

		try:
			with open(entity_info_path) as f:
				self.entityInfo = [line.split("@") for line in f.read().splitlines()]
				
				
		except(IOError, FileNotFoundError) as e:
			print("Error reading entityInfo! {}".format(e))
			return False
		return True
		
	def _decode_tbl_string(self, data: bytes) -> str:
		"""Decodes a null-terminated byte string from the stage table."""
		try:
			null_pos = data.find(b'\x00')
			if null_pos != -1:
				data = data[:null_pos]
			# Shift-JIS is the standard for CS and is compatible with ASCII for English names
			return data.decode('shift-jis')
		except UnicodeDecodeError:
			return "DECODE_ERROR"

	def readStageTable(self):
		"""Loads and parses the stage.tbl file for Cave Story."""
		import struct

		current_game_config = self.game_manager.get_current_game()
		# This file is specific to Cave Story
		if current_game_config.name != "cave_story":
			return True # Not an error, just not applicable for this game.

		stage_tbl_path = os.path.join(
			current_game_config.base_path,
			current_game_config.get('data_path'),
			'stage.tbl'
		)

		try:
			with open(stage_tbl_path, 'rb') as f:
				file_data = f.read()
		except (IOError, FileNotFoundError) as e:
			print(f"Warning: could not load 'stage.tbl': {e}")
			return False

		ENTRY_SIZE = 229  # 0xE5
		entry_count = len(file_data) // ENTRY_SIZE

		if entry_count == 0:
			print("Warning: 'stage.tbl' is empty or has an invalid size.")
			return False

		self.stage_table.clear()
		for i in range(entry_count):
			offset = i * ENTRY_SIZE
			entry = file_data[offset : offset + ENTRY_SIZE]

			stage_info = StageInfo(
				index=i,
				parts=self._decode_tbl_string(entry[0x00:0x20]),
				map=self._decode_tbl_string(entry[0x20:0x40]),
				bkType=struct.unpack('<I', entry[0x40:0x44])[0],
				back=self._decode_tbl_string(entry[0x44:0x64]),
				npc=self._decode_tbl_string(entry[0x64:0x84]),
				boss=self._decode_tbl_string(entry[0x84:0xA4]),
				boss_no=entry[0xA4],
				name_jp=self._decode_tbl_string(entry[0xA5:0xC5]),
				name=self._decode_tbl_string(entry[0xC5:0xE5])
			)
			self.stage_table.append(stage_info)

		print(f"Successfully loaded {len(self.stage_table)} entries from stage.tbl.")
		return True



	def update_tile_dimensions(self):
		current_game = self.game_manager.get_current_game()
		base_tile_size = current_game.get('tile_size', 8)
		self.tileWidth = base_tile_size * const.tileScale

		# --- THE FIX ---
		# Determine the size of icons on the unittype.png sheet.
		# For CS, Rockfish, and Guxt, the icon size matches the tile size.
		# For Kero Blaster, the icons are double the tile size.
		current_game_name = gxEdit.game_manager.get_current_game().name
		if current_game_name in ("cave_story", "rockfish", "guxt"):
			self.tileWidth2 = self.tileWidth # Standard for entities
		else: # kero_blaster
			self.tileWidth2 = self.tileWidth * 2

		if current_game_name == 'guxt':
			const.ENTITY_SCALE = 2
		else:
			const.ENTITY_SCALE = 1

	def loadMeta(self, sprfactory):
		result = True
		result &= self.readEntityInfo()
		result &= self.readStageTable()
		return result

	def loadStage(self, stageName):
		if not len(stageName): return False
		self.update_tile_dimensions()
		print("Loading stage " + stageName)
		try:
			# Pass the stage table to the format manager
			pack = self.format_manager.load_stage(stageName, self.stage_table)
			stage = StagePrj(stageName, pack, self.tileWidth)
			result = stage.load()
			if result:
				self.stages.append(stage)
			else:
				del stage
			return result
		except (ValueError, FileNotFoundError, NotImplementedError) as e:
			print(f"Error loading stage {stageName}: {e}")
			return False

	def getStageById(self, stageNo):
		for stage in self.stages:
			if stage.stageNo == stageNo:
				return stage



	def loadAttributeFileAsStage(self, fName, fPath):
		"""Loads a .pxa or .pxattr file and treats it as an editable stage."""
		print(f"Loading attribute file as a stage: {fName}")
		
		attr_data = pxMap.PxMapAttr()
		if not attr_data.load(fPath):
			print(f"Failed to load attribute file: {fPath}")
			return False

		# --- CONTEXT TILESET LOADING ---
		context_tileset = None
		current_game_config = self.game_manager.get_current_game()
		
		if current_game_config.name == 'cave_story':
			tileset_name = "Prt" + fName
			bmp_path = os.path.join(imgPath, tileset_name + ".bmp")
			pbm_path = os.path.join(imgPath, tileset_name + ".pbm")
			try:
				if os.path.exists(bmp_path):
					context_tileset = interface.gSprfactory.from_image(bmp_path)
				elif os.path.exists(pbm_path):
					context_tileset = interface.gSprfactory.from_image(pbm_path)
			except Exception as e:
				print(f"Could not load context tileset '{tileset_name}': {e}")

		elif current_game_config.name == 'kero_blaster' or current_game_config.name == 'rockfish':
			# --- THE FIX FOR KERO BLASTER ---
			# For KB, the attr filename (e.g. '01field') matches the tileset filename.
			tileset_ext = current_game_config.get('tileset_ext')
			tileset_path = os.path.join(imgPath, fName + tileset_ext)
			try:
				if os.path.exists(tileset_path):
					context_tileset = interface.gSprfactory.from_image(tileset_path)
					print(f"Loaded context tileset: {os.path.basename(tileset_path)}")
			except Exception as e:
				print(f"Could not load context tileset '{tileset_path}': {e}")
		# -------------------------------

		self.update_tile_dimensions()

		# Use tileset dimensions if available, otherwise attr data dimensions
		map_width = context_tileset.size[0] // self.tileWidth if context_tileset else attr_data.width
		map_height = context_tileset.size[1] // self.tileWidth if context_tileset else attr_data.height

		pack = Stage(fName, map_width, map_height)
		pack.eve = pxMap.PxEve()

		# Layer 0 (background): The visual stage tileset.
		layer0 = Layer(map_width, map_height)
		if context_tileset:
			# Create a 1:1 map of the tileset
			layer0.tiles = [[(y * map_width) + x for x in range(map_width)] for y in range(map_height)]
		pack.layers.append(layer0)
		
		# Layer 1 (foreground): The attribute data we are editing.
		layer1 = Layer(map_width, map_height)
		attr_data.resize(map_width, map_height) # Ensure it matches background
		layer1.tiles = attr_data.tiles
		pack.layers.append(layer1)
		
		pack.layers.append(Layer(0,0))

		stage = StagePrj(fName, pack, self.tileWidth)
		stage.is_attribute_stage = True
		stage.original_path = fPath
		
		stage.parts[0] = context_tileset # Main view
		stage.parts[1] = interface.gSurfaces[interface.SURF_ATTRIBUTE] # Palette view

		# Fallback: if still no context tileset, use attribute.png to prevent crash
		if not stage.parts[0]:
			stage.parts[0] = stage.parts[1]

		# Setup attrs for Layer 0 (Context)
		if stage.parts[0]:
			attrs_for_layer0 = pxMap.PxMapAttr()
			attrs_for_layer0.width = stage.parts[0].size[0] // self.tileWidth
			attrs_for_layer0.height = stage.parts[0].size[1] // self.tileWidth
			stage.attrs[0] = attrs_for_layer0

		# Setup attrs for Layer 1 (Palette - always 16x16 tiles)
		palette_source = stage.parts[1]
		attrs_for_layer1 = pxMap.PxMapAttr()
		palette_tile_width = 16 
		attrs_for_layer1.width = palette_source.size[0] // palette_tile_width
		attrs_for_layer1.height = palette_source.size[1] // palette_tile_width
		stage.attrs[1] = attrs_for_layer1

		# Render surfaces
		stage.createMapSurface(0)
		# Special render: copy the context tileset directly to the surface
		if stage.parts[0]:
			sdlrenderer = interface.gRenderer.sdlrenderer
			sdl2.SDL_SetRenderTarget(sdlrenderer, stage.surfaces[0].texture)
			# Clear first in case parts[0] has transparency
			sdl2.SDL_SetRenderDrawColor(sdlrenderer, 0, 0, 0, 0)
			sdl2.SDL_RenderClear(sdlrenderer)
			interface.gRenderer.copy(stage.parts[0])
			sdl2.SDL_SetRenderTarget(sdlrenderer, None)
		
		stage.createMapSurface(1)
		stage.renderMapToSurface(1) # Render attribute data normally
		
		self.stages.append(stage)
		self.currentLayer = 1
		
		return True
	def executeUndo(self):
		#TODO: temp, do smarter implementation
		stage = self.stages[self.curStage]
		undoStack = stage.undoStack
		undoPos = stage.undoPos
		if undoPos == 0:
			return

		undo = undoStack[undoPos]

		if undo.action == const.UNDO_TILE:
			stage.lastTileEdit = [None, None]
			map_layer = stage.pack.layers[undo.param] if len(stage.pack.layers) > undo.param else None
			if map_layer:
				for pos, tile_coords in undo.reverse: # tile_coords is [tx, ty]
					# Reconstruct the single integer tile ID for the map data array
					tile_value = tile_coords[0] + (tile_coords[1] * 16)
					map_layer.tiles[pos[1]][pos[0]] = tile_value
					# Use the tile coordinates directly for rendering to the surface
					stage.renderTileToSurface(pos[0], pos[1], tile_coords[0], tile_coords[1], undo.param)
		elif undo.action == const.UNDO_ENTITY_MOVE:
			stage.pack.eve.replace(undo.reverse)
			stage.selectedEntities = [e for e in stage.pack.eve.units if e.id in [o.id for o in undo.reverse]]

		elif undo.action == const.UNDO_ENTITY_ADD:
			# This needs to use the pack entities
			ids = [o.id for o in undo.forward]
			stage.pack.eve.units = [e for e in stage.pack.eve.units if e.id not in ids]

		elif undo.action == const.UNDO_ENTITY_REMOVE:
			# This needs to use the pack entities
			stage.pack.eve.units.extend(undo.forward)

		stage.undoPos -= 1
		if undoPos == 1:
			return
		if(undoStack[undoPos].commit == False):
			gxEdit.executeUndo()

	def executeRedo(self):
		stage = self.stages[self.curStage]
		undoStack = stage.undoStack
		undoPos = stage.undoPos + 1

		if undoPos > len(undoStack)-1:
			return

		redo = undoStack[undoPos]

		if redo.action == const.UNDO_TILE:
			stage.lastTileEdit = [None, None]
			map_layer = stage.pack.layers[redo.param] if len(stage.pack.layers) > redo.param else None
			if map_layer:
				for pos, tile_coords in redo.forward: # tile_coords is [tx, ty]
					# Reconstruct the single integer tile ID for the map data array
					tile_value = tile_coords[0] + (tile_coords[1] * 16)
					map_layer.tiles[pos[1]][pos[0]] = tile_value
					# Use the tile coordinates directly for rendering to the surface
					stage.renderTileToSurface(pos[0], pos[1], tile_coords[0], tile_coords[1], redo.param)
		elif redo.action == const.UNDO_ENTITY_MOVE:
			stage.pack.eve.replace(redo.forward)
			stage.selectedEntities = [e for e in stage.pack.eve.units if e.id in [o.id for o in redo.forward]]
		elif redo.action == const.UNDO_ENTITY_ADD:
			# This needs to use the pack entities
			for o in redo.forward:
				stage.pack.eve.units.append(o)
		elif redo.action == const.UNDO_ENTITY_REMOVE:
			# This needs to use the pack entities
			ids = [o.id for o in redo.forward]
			stage.pack.eve.units = [e for e in stage.pack.eve.units if e.id not in ids]

											
		stage.undoPos += 1

		if(undoStack[undoPos].commit == False):
			gxEdit.executeRedo()

	def backupStages(self):
		# This needs to use the game_manager to get the correct backup path
		current_game_config = self.game_manager.get_current_game()
		backup_path = os.path.join(self.game_manager.get_current_game().base_path, current_game_config.get('data_path'), backupFolderName)

		if not os.path.exists(backup_path):
			os.makedirs(backup_path)

		for stage_prj in self.stages:
			if not stage_prj.backup():
				continue

		#remove oldest backups
		backupFiles = sorted(glob.glob(backup_path + "/*"))
		names = []
		for backup in backupFiles:
			basename = os.path.basename(backup)
			try:
				suffix = basename.split("_", 1)[1]
				names.append(suffix)
			except IndexError:
				print("Invalid backup name.." + basename)
				return
		
		backupCounts = dict(Counter(names))
		
		for suffix, count in backupCounts.items():
			if count <= gxEdit.backupLimit:
				continue

			backupsMatching = [x for x in backupFiles if x[-len(suffix):] == suffix]
			for i in range(count - gxEdit.backupLimit):
				print("Pruning " + backupsMatching[i])
				os.remove(backupsMatching[i])

		print("backup complete.")


gxEdit = Editor(game_manager, format_manager) 
