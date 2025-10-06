import const
import os
import glob, os
import copy
import pxMap
import interface
import sdl2

from datetime import datetime

from dataclasses import dataclass

from collections import Counter

from game import GameManager
from loader import Loader
from saver import Saver
from stage import Stage, Layer, Entity

# Global instances of our new classes
game_manager = GameManager()
loader = Loader(game_manager)
saver = Saver(game_manager)

# Default game and path for now
# TODO: Make this user selectable
if False:
	game_manager.set_game("cave_story")
	game_manager.set_game_path("./CaveStory/")
	defaultStage = "Almond"
else:
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
		
		# For now, we assume 3 layers for parts/attrs
		for i in range(3):
			if self.loadParts(i):
				self.loadAttrs(i)
			self.createMapSurface(i)
			self.renderMapToSurface(i)
		return True

	def loadParts(self, layerNo):
		try:
			current_game_config = game_manager.get_current_game()
			tileset_ext = current_game_config.get('tileset_ext')
			
			# Each layer has its own partsName. Get it directly.
			if len(self.pack.layers) <= layerNo or not self.pack.layers[layerNo]:
				return False # This layer doesn't exist.
			
			tileset_name = self.pack.layers[layerNo].partsName

			# If the partsName is empty (e.g., for an unused layer), don't try to load anything.
			if not tileset_name:
				if current_game_config.name == "cave_story" and layerNo == 0:
					# Fallback for Cave Story's main layer
					tileset_name = "Prt" + self.stageName
				else:
					return False

			self.parts[layerNo] = interface.gSprfactory.from_image(imgPath + tileset_name + tileset_ext)
			
			# If the layer dimensions were 0, update them from the image size.
			if not self.pack.layers[layerNo].width and self.parts[layerNo]:
				self.pack.layers[layerNo].width = self.parts[layerNo].size[0] // self.tileWidth
				self.pack.layers[layerNo].height = self.parts[layerNo].size[1] // self.tileWidth
					
			return True
		except (OSError, IOError, sdl2.ext.SDLError) as e:
			print("Error while loading parts for layer {}: {}".format(layerNo, e))
			self.parts[layerNo] = None # Ensure it's None on failure
			return False
	def loadAttrs(self, layerNo):
		current_game_config = game_manager.get_current_game()
		self.attrs[layerNo] = pxMap.PxMapAttr() # ALWAYS create the instance first.

		if current_game_config.name == 'kero_blaster':
			# Kero Blaster uses explicit .pxattr files
			attr_ext = current_game_config.get('attr_ext')
			tileset_name = self.pack.layers[layerNo].partsName
			if tileset_name:
				attr_path = os.path.join(imgPath, tileset_name + attr_ext)
				if os.path.exists(attr_path):
					self.attrs[layerNo].load(attr_path)
				elif self.parts[layerNo]: # If file doesn't exist, create based on image size
					self.attrs[layerNo].width = self.parts[layerNo].size[0] // self.tileWidth
					self.attrs[layerNo].height = self.parts[layerNo].size[1] // self.tileWidth
				else:
					self.attrs[layerNo].width = 0
					self.attrs[layerNo].height = 0
		
		elif current_game_config.name == 'cave_story':
			# Cave Story has no .pxattr, so we create attributes based on the tileset image size
			if self.parts[layerNo]:
				self.attrs[layerNo].width = self.parts[layerNo].size[0] // self.tileWidth
				self.attrs[layerNo].height = self.parts[layerNo].size[1] // self.tileWidth
			else:
				# If no parts exist for this layer, initialize with 0 to prevent crashes.
				self.attrs[layerNo].width = 0
				self.attrs[layerNo].height = 0
		return True
	def save(self):
		#if self.lastSavePos == self.undoPos: #TODO: and pxattr not modified
		#	return False
		print("--Saving stage {}...--".format(self.stageName))
		saver.save_stage(self.pack)
		#TODO: save to _temp, rename existing to _temp2, rename _temp to orig and delete temp2

		#TODO: for save as, open all pxpacks in folder and change all references to new name

		self.lastSavePos = self.undoPos
		self.lastBackupPos = self.undoPos
		print("saved.")
		return True
		
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
		saver.save_stage(backup_stage)
		
		self.lastBackupPos = self.undoPos

		#self.eve.save(dataPath + backupFolderName + "/" + dateMin + "_" + eventOut)
		#self.map.save(dataPath + backupFolderName + "/" + dateMin + "_" + mapOut)

		#backupId += 1

		return True

	def renderMapToSurface(self, layerNo):
		# This needs to use the pack layers
		map_layer = self.pack.layers[layerNo] if len(self.pack.layers) > layerNo else None

		if not map_layer or len(map_layer.tiles) == 0: return

		print(f"DEBUG: map_layer.width: {map_layer.width}, map_layer.height: {map_layer.height}, len(map_layer.tiles): {len(map_layer.tiles)}")

		sdlrenderer = interface.gRenderer.sdlrenderer
		sdl2.SDL_SetRenderTarget(sdlrenderer, self.surfaces[layerNo].texture)
		sdl2.SDL_SetTextureBlendMode(self.surfaces[layerNo].texture, sdl2.SDL_BLENDMODE_BLEND)

		srcrect = sdl2.SDL_Rect(0,0,self.tileWidth,self.tileWidth)
		dstrect = sdl2.SDL_Rect(0,0,self.tileWidth,self.tileWidth)


		for y in range(map_layer.height):
			for x in range(map_layer.width):
				try:
					#TODO: detect if blank tile
					#if map.tiles[y][x] == 0: continue
					dstx = x * self.tileWidth
					dsty = y * self.tileWidth

					xx = map_layer.tiles[y][x] % 16 #the magic number so that each 4 bits in a byte corresponds to the x, y position in the tileset
					yy = map_layer.tiles[y][x] // 16


					srcx = xx * self.tileWidth
					srcy = yy * self.tileWidth


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
		dstx = x * self.tileWidth
		dsty = y * self.tileWidth

		srcx = tx * self.tileWidth
		srcy = ty * self.tileWidth

		sdlrenderer = interface.gRenderer.sdlrenderer
		srcrect = (srcx, srcy, self.tileWidth, self.tileWidth)
		dstrect = (dstx, dsty, self.tileWidth, self.tileWidth)

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
	
	def __init__(self, game_manager, loader, saver):
		self.game_manager = game_manager
		self.loader = loader
		self.saver = saver
		self.entityInfo = []
		self.stages = []

		self.curStage = 0

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

	def update_tile_dimensions(self):
		current_game = self.game_manager.get_current_game()
		base_tile_size = current_game.get('tile_size', 8) # Default to 8 if not in config
		self.tileWidth = base_tile_size * const.tileScale

		current_game_name = gxEdit.game_manager.get_current_game().name
		if current_game_name == "cave_story":
			self.tileWidth2 = self.tileWidth # Standard for entities
		else: # kero_blaster
			self.tileWidth2 = self.tileWidth * 2 # Standard for entities

	def loadMeta(self, sprfactory):
		result = True
		result &= self.readEntityInfo()
		return result

	def loadStage(self, stageName):
		if not len(stageName): return False
		self.update_tile_dimensions() # <-- Must be called FIRST
		print("Loading stage " + stageName)
		try:
			pack = self.loader.load_stage(stageName)
			stage = StagePrj(stageName, pack, self.tileWidth) # <-- Pass the correct width
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


gxEdit = Editor(game_manager, loader, saver)