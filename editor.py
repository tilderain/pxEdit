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
from editor import gxEdit

with open("./basepath.txt") as f:
	basePath = f.read().strip('\n')
print(basePath)

# Default game and path for now
# TODO: Make this user selectable
game_manager.set_game("cave_story")
game_manager.set_game_path("./CaveStory/")
defaultStage = "Almond"

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
	def __init__(self, stageName):
		self.stageName = stageName
		self.pack = pxMap.PxPack()
		self.attrs = [pxMap.PxPackLayer(), pxMap.PxPackLayer(), pxMap.PxPackLayer()]

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

		self.surfaces = [None, None, None]

	def createMapSurface(self, layerNo):
		del self.surfaces[layerNo]
		self.surfaces.insert(layerNo, None)
		if self.pack.layers[layerNo].width * self.pack.layers[layerNo].height == 0: return
		
		self.surfaces[layerNo] = interface.gSprfactory.create_texture_sprite(interface.gRenderer, 
			(self.pack.layers[layerNo].width*const.tileWidth, self.pack.layers[layerNo].height*const.tileWidth), access=sdl2.SDL_TEXTUREACCESS_TARGET)
	
	def load(self):
		#TODO: open dialogue box to see if there is a newer backup
			#read last modified date
			#Choose the backup you want to open.
		
		if self.pack.load(self.stageName):
			for i in range(1):
				self.loadParts(i)
				self.attrs[i].load(fieldPath + "parts" + self.pack.layers[i].partsName + pxAttrExt, printError=True)
				self.createMapSurface(i)
				self.renderMapToSurface(i)
			return True

		return False

	def loadParts(self, layerNo):
		try:
			self.parts[layerNo] = interface.gSprfactory.from_image(imgPath + "parts" + self.pack.layers[layerNo].partsName + ".png")
			if not self.attrs[layerNo].width:
					self.attrs[layerNo].width = self.parts[layerNo].size[0] // const.tileWidth
					self.attrs[layerNo].height = self.parts[layerNo].size[1] // const.tileWidth
			return True
		except (OSError, IOError, sdl2.ext.SDLError) as e:
			print("Error while loading parts {} {}".format(layerNo, e))
			return False

	def save(self):
		#if self.lastSavePos == self.undoPos: #TODO: and pxattr not modified
		#	return False

		print("--Saving stage {}...--".format(self.stageName))
		
		self.pack.save(self.stageName)
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

		self.pack.save(fieldPath + backupFolderName + "/" + dateMin + "_" + self.stageName + pxPackExt)
		
		#self.eve.save(dataPath + backupFolderName + "/" + dateMin + "_" + eventOut)
		#self.map.save(dataPath + backupFolderName + "/" + dateMin + "_" + mapOut)

		self.lastBackupPos = self.undoPos

		#backupId += 1

		return True

	def renderMapToSurface(self, layerNo):
		map = self.pack.layers[layerNo]
		if len(map.tiles) == 0: return

		sdlrenderer = interface.gRenderer.sdlrenderer
		sdl2.SDL_SetRenderTarget(sdlrenderer, self.surfaces[layerNo].texture)
		#sdl2.SDL_SetRenderDrawBlendMode(sdlrenderer, sdl2.SDL_BLENDMODE_NONE)
		sdl2.SDL_SetTextureBlendMode(self.surfaces[layerNo].texture, sdl2.SDL_BLENDMODE_BLEND)

		srcrect = sdl2.SDL_Rect(0,0,const.tileWidth,const.tileWidth)
		dstrect = sdl2.SDL_Rect(0,0,const.tileWidth,const.tileWidth)


		for x in range(map.width):
			for y in range(map.height):
				#TODO: detect if blank tile
				#if map.tiles[y][x] == 0: continue
				dstx = x * const.tileWidth
				dsty = y * const.tileWidth

				xx = map.tiles[y][x] % 16 #the magic number so that each 4 bits in a byte corresponds to the x, y position in the tileset
				yy = map.tiles[y][x] // 16
				srcx = xx * const.tileWidth
				srcy = yy * const.tileWidth


				srcrect.x = srcx
				srcrect.y = srcy
				dstrect.x = dstx
				dstrect.y = dsty
				try:
					sdl2.SDL_RenderCopy(sdlrenderer, self.parts[layerNo].texture, srcrect, dstrect)
				except:
					break
				#interface.gRenderer.copy(self.parts, srcrect, dstrect)
		sdl2.SDL_SetRenderTarget(sdlrenderer, None)
			
	
	def renderTileToSurface(self, x, y, tx, ty, layerNo):
		dstx = x * const.tileWidth
		dsty = y * const.tileWidth

		srcx = tx * const.tileWidth
		srcy = ty * const.tileWidth

		sdlrenderer = interface.gRenderer.sdlrenderer
		srcrect = (srcx, srcy, const.tileWidth, const.tileWidth)
		dstrect = (dstx, dsty, const.tileWidth, const.tileWidth)

		sdl2.SDL_SetRenderTarget(sdlrenderer, self.surfaces[layerNo].texture)

		sdl2.SDL_SetTextureBlendMode(self.parts[layerNo].texture, sdl2.SDL_BLENDMODE_NONE)

		interface.gRenderer.copy(self.parts[layerNo], srcrect, dstrect)

		sdl2.SDL_SetTextureBlendMode(self.parts[layerNo].texture, sdl2.SDL_BLENDMODE_BLEND)

		sdl2.SDL_SetRenderTarget(sdlrenderer, None)

	def addUndo(self, undo):
		self.undoPos += 1
		self.undoStack = self.undoStack[:self.undoPos]
		self.undoStack.append(undo)

class StagePrj:
	def __init__(self, stageName, pack: Stage):
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

		self.tileWidth = 16

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
			
			tileset_name = self.pack.spritesheet
			if not tileset_name: # Fallback if spritesheet is not set in pack
				if current_game_config.name == "kero_blaster":
					tileset_name = "parts" # Default for Kero Blaster
				elif current_game_config.name == "cave_story":
					tileset_name = "Prt" + self.stageName # Default for Cave Story
				
			self.parts[layerNo] = interface.gSprfactory.from_image(imgPath + tileset_name + tileset_ext)
			
			# The attrs are now part of the pack.layers
			# This logic seems to intend to set the size of an empty layer based on its parts image.
			# We'll apply it to the layer being loaded.
			if len(self.pack.layers) > layerNo and self.pack.layers[layerNo] and not self.pack.layers[layerNo].width:
				self.pack.layers[layerNo].width = self.parts[layerNo].size[0] // self.tileWidth
				self.pack.layers[layerNo].height = self.parts[layerNo].size[1] // self.tileWidth
					
			return True
		except (OSError, IOError, sdl2.ext.SDLError) as e:
			print("Error while loading parts {} {}".format(layerNo, e))
			return False
	def loadAttrs(self, layerNo):
		current_game_config = game_manager.get_current_game()
		self.attrs[layerNo] = pxMap.PxMapAttr() # Create instance

		if current_game_config.name == 'kero_blaster':
			# Kero Blaster uses explicit .pxattr files
			attr_ext = current_game_config.get('attr_ext')
			tileset_name = self.pack.layers[layerNo].partsName
			if tileset_name:
				attr_path = os.path.join(imgPath, tileset_name + attr_ext)
				if os.path.exists(attr_path):
					self.attrs[layerNo].load(attr_path)
				else:
					# If file doesn't exist, create based on image size
					self.attrs[layerNo].width = self.parts[layerNo].size[0] // self.tileWidth
					self.attrs[layerNo].height = self.parts[layerNo].size[1] // self.tileWidth
		
		elif current_game_config.name == 'cave_story':
			# Cave Story has no .pxattr, so we create attributes based on the tileset image size
			if self.parts[layerNo]:
				self.attrs[layerNo].width = self.parts[layerNo].size[0] // self.tileWidth
				self.attrs[layerNo].height = self.parts[layerNo].size[1] // self.tileWidth
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
		self.tileWidth = const.tileWidth # Default, will be updated

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
				# Assuming the format is spritesheet,x,y,id,name
				self.entityInfo = []
				for line in f.read().splitlines():
					if line.strip() and not line.strip().startswith('#'):
						self.entityInfo.append(line.split(','))
				
		except(IOError, FileNotFoundError) as e:
			print("Error reading entityInfo! {}".format(e))
			return False
		return True

	def update_tile_dimensions(self):
		current_game = self.game_manager.get_current_game()
		base_tile_size = current_game.get('tile_size', 8) # Default to 8 if not in config
		self.tileWidth = base_tile_size * const.tileScale

	def loadMeta(self, sprfactory):
		result = True
		result &= self.readEntityInfo()
		return result

	def loadStage(self, stageName):
		if not len(stageName): return False
		self.update_tile_dimensions()
		print("Loading stage " + stageName)
		try:
			pack = self.loader.load_stage(stageName)
			stage = StagePrj(stageName, pack)
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
			# This needs to use the pack layers
			map_layer = stage.pack.layers[undo.param] if len(stage.pack.layers) > undo.param else None
			if map_layer: # Assuming modify method exists on Layer
				# This modify method needs to be implemented in the universal Layer class
				# For now, direct modification
				for pos, tile_val in undo.reverse:
					map_layer.tiles[pos[1]][pos[0]] = tile_val
				for pos, tile in undo.reverse:
					stage.renderTileToSurface(pos[0], pos[1], tile[0],
												tile[1], undo.param)
		elif undo.action == const.UNDO_ENTITY_MOVE:
			# This needs to use the pack entities
			# Assuming replace method exists or direct manipulation
			# For now, direct manipulation
			stage.pack.eve.units = undo.reverse # This is a simplification
			stage.selectedEntities = undo.reverse

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
			# This needs to use the pack layers
			map_layer = stage.pack.layers[redo.param] if len(stage.pack.layers) > redo.param else None
			if map_layer: # Assuming modify method exists on Layer
				# This modify method needs to be implemented in the universal Layer class
				# For now, direct modification
				for pos, tile_val in redo.forward:
					map_layer.tiles[pos[1]][pos[0]] = tile_val
				for pos, tile in redo.forward:
					stage.renderTileToSurface(pos[0], pos[1], tile[0],
												tile[1], redo.param)
		elif redo.action == const.UNDO_ENTITY_MOVE:
			# This needs to use the pack entities
			# Assuming replace method exists or direct manipulation
			# For now, direct manipulation
			stage.pack.eve.units = redo.forward # This is a simplification
			stage.selectedEntities = redo.forward
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