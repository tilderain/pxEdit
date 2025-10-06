#The Doctor invites you to his garage.
#The doctor's garage awaits [new members]

import io, mmap, sys, time, math, random
import ctypes
import glob, os
import copy

from datetime import datetime

from dataclasses import dataclass

from collections import Counter

import pxEve, pxMap, interface, input
import const
os.environ["PYSDL2_DLL_PATH"] = "./"
import sdl2.ext
from sdl2.sdlttf import *

import multi
import util

from game import GameManager
from loader import Loader
from saver import Saver
from stage import Stage, Layer, Entity

#You must agree to the terms of use to continue.
#Terms of Use
#THIS INDEPENDANT
#1.1 You hereby assert that they you not falsify their identity.
#1. Persons Authorized to Use the Software
#1.1 If you have ever used, or ever intend to use the name "NethoWarrior" to identify yourself at any point in the past, present, or future, you are not permitted to use this product, and must terminate the software immediately. / immidiately cease any further utilization of the Software.
#immediately terminate this program and cease any furth
#Please find and press the word "terminate" above to unlock the following buttons.
#Please find and paste the word "terminate" above into this box to unlock the following buttons.

# I have read and accept the terms of use.
# I hereby state that all information asserted above is correct.



# Global instances of our new classes
game_manager = GameManager()
loader = Loader(game_manager)
saver = Saver(game_manager)

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

mapPath = "map{}.pxmap"
partsPath = "parts{}.bmp"
attrPath = "parts{}.pxatrb"
eventPath = "event{}.pxeve"
pximgPath = "parts{}.pximg"

pxPackExt = current_game_config.get('stage_ext')
pxAttrExt = current_game_config.get('attr_ext')

backupFolderName = "backup"
backupFormat = "backup/_{}_{}"
backupTimeFormat = "%Y%m%d-%H%M%S"

windowName = "Doctor's Garage"

#copy tiles
#takes an xy square and copies it to the clipboard (width, height)

#modify tiles
#takes an xy square and applies it to a map list

#modify tileattr
#takes an xy square and applies it to tileattr list

#save tiles (stageNo, mapObject)

#A stage contains an entity list and a map.
#The map loads a tileset, and tileset attributes.
#By default, these are hardcoded to be based off the stage number.


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

def main():
	sdl2.ext.init()
	#To disable texture destruction on window resize
	sdl2.SDL_SetHint(sdl2.SDL_HINT_RENDER_DRIVER, b"opengl")
#	sdl2.SDL_SetHint(sdl2.SDL_HINT_DPI_SCALING "0"
#	sdl2.SDL_SetHint(sdl2.SDL_HINT_DPI_AWARENESS "system"
#	sdl2.SDL_SetHint(sdl2.SDL_HINT_VIDEO_HIGHDPI_DISABLED "1"

	if TTF_Init() == -1:
		print("Error initting ttf: ", TTF_GetError())
		return

	interface.gFont = TTF_OpenFont(b"sserife.fon", ctypes.c_int(12))

	if not interface.gFont:
		print("error opening font:", TTF_GetError())
		return

	#TODO window.rect
	defaultWindowWidth = 1680
	defaultWindowHeight = 960

	interface.gWindow = sdl2.ext.Window(windowName, size=(defaultWindowWidth, defaultWindowHeight), flags=sdl2.SDL_WINDOW_RESIZABLE)
	interface.gWindowWidth = defaultWindowWidth
	interface.gWindowHeight = defaultWindowHeight

	window = interface.gWindow
	window.show()

	interface.gRenderer = sdl2.ext.Renderer(window, flags=sdl2.SDL_RENDERER_ACCELERATED|sdl2.SDL_RENDERER_TARGETTEXTURE)
	renderer = interface.gRenderer

	interface.gSprfactory = sdl2.ext.SpriteFactory(sdl2.ext.TEXTURE, renderer=renderer)
	sprfactory = interface.gSprfactory

	interface.gInterface = interface.Interface(renderer, window, sprfactory)
	gui = interface.gInterface
	gui.loadSurfaces()


	#uifactory = sdl2.ext.UIFactory(sprfactory)

	'''
	windowBg._size = (windowBg.size[0] * 2, windowBg.size[1] * 2)
	windowBg2._size = (windowBg2.size[0] * 2, windowBg2.size[1] * 2)'''
	#easy

	gxEdit.loadMeta(sprfactory)

	gxEdit.loadStage(defaultStage)

	introAnimTimer = 0

	running = True
	mouseover = True

	mouseHeld = False


	#gxEdit.elements.append(UIWindow(100, 100, 128, 64))
	#gxEdit.elements.append(interface.UIWindow(22, 22, 256, 256))
	#gxEdit.elements.append(interface.UIWindow(300, 300, 260, 272, const.WINDOW_TILEPALETTE))

	entityinfoheight = len(gxEdit.entityInfo) // 16 * 34
	gxEdit.elements["tilePalette"] = interface.TilePaletteWindow(1200, 400, 256, 280, const.WINDOW_TILEPALETTE)
	gxEdit.elements["entityPalette"] = interface.EntityPaletteWindow(1450, 400, 256*2, entityinfoheight, const.WINDOW_ENTITYPALETTE)

	gxEdit.elements["toolsWindow"] = interface.ToolsWindow(800, 400, 190, 86, const.WINDOW_TOOLS)

	gxEdit.elements["uiTooltip"] = interface.UITooltip(0,0,1,1)

	gxEdit.elements["entEdit"] = interface.EntityEditWindow(20,20,150,250)

	gxEdit.elements["mapSizeDialog"] = interface.MapResizeDialog(20,20,104,88)

	gxEdit.elements["pxPackAttrDialog"] = interface.PxPackAttrDialog(20,20,405,270)

	gxEdit.elements["dialogMultiplayer"] = interface.MultiplayerWindow(0,0,220,80)

	def renderEditor():
		#TODO: placeholder

		#gui.renderMainBg(introAnimTimer, mouseover)
		gui.renderEditorBg()
		gui.renderBgColor(gxEdit, curStage)
		for i in reversed(range(3)):
			if gxEdit.visibleLayers[i]:
				gui.renderTiles(gxEdit, curStage, i)
		if gxEdit.visibleLayers[4]:
			# This needs to use the pack layers
			map_layer = curStage.pack.layers[gxEdit.currentLayer] if len(curStage.pack.layers) > gxEdit.currentLayer else None
			if map_layer:
				gui.renderTileAttr(gxEdit, curStage, map_layer)

		gui.renderEntitySelectionBox(gxEdit, curStage)
		gui.renderPlayers(gxEdit, curStage)
		gui.renderTilePreview(gxEdit, curStage)

		if gxEdit.visibleLayers[3] or gxEdit.currentEditMode == const.EDIT_ENTITY:
			gui.renderEntities(gxEdit, curStage)
	
		gui.renderEntityPalette(gxEdit, curStage)
		gui.renderTilePalette(gxEdit, curStage)
	
		for _, elem in gxEdit.elements.items():
			if elem.visible: 
				gui.renderUIWindow(gxEdit, elem)
				elem.render(gxEdit, curStage)

		for _, elem in gxEdit.elements.items():
			if elem.type == const.WINDOW_TOOLTIP and elem.visible: elem.render(gxEdit, curStage)

	#for continuous resizing
	def resizeEventWatch(data, event):
		#TODO: recreate map textures for our poor software rendered boys
		if event.contents.type == sdl2.SDL_WINDOWEVENT:
			if event.contents.window.event == sdl2.SDL_WINDOWEVENT_SIZE_CHANGED:
				interface.gWindowWidth = event.contents.window.data1
				interface.gWindowHeight = event.contents.window.data2

				renderer.logical_size = (interface.gWindowWidth, interface.gWindowHeight)
				
				#renderEditor()
				#renderer.present()
		return 0
	reFunc = sdl2.SDL_EventFilter(resizeEventWatch)
	sdl2.SDL_AddEventWatch(reFunc, window.window)

	tickCount = sdl2.timer.SDL_GetTicks()
	gxEdit.lastBackupTick = tickCount

	while running:

		tickCount = sdl2.timer.SDL_GetTicks()
		
		curStage = gxEdit.stages[gxEdit.curStage]
		
		#height of window in tiles
		scaleFactor = (interface.gWindowHeight // gxEdit.stages[gxEdit.curStage].tileWidth // gxEdit.magnification)
		events = sdl2.ext.get_events()

		multiwindowstring = ""
		if gxEdit.multiplayerState == const.MULTIPLAYER_HOST:
			multiwindowstring = "**Hosting**"
		elif gxEdit.multiplayerState == const.MULTIPLAYER_CLIENT:
			multiwindowstring = "**Connected**"

		#set windowname
		interface.gWindow.title = windowName + " [" + "" + str(curStage.stageName) + "]" + " " + multiwindowstring
		
		for event in events:
			#TODO: really really fix this
			if gxEdit.focussedElem:
				if not gxEdit.focussedElem.parent.visible:
					gxEdit.focussedElem.focussed = False
					gxEdit.focussedElem = None

			if event.type == sdl2.SDL_QUIT:
				running = False
				break
			elif event.type == sdl2.SDL_DROPFILE:
				#TODO: drop an exe or event/map to load singular
				print("help")
				if sys.platform == "win32":
					fName = str(event.drop.file).split("\\")[-1].split(".")[0]
				else:
					fName = str(event.drop.file).split("/")[-1].split(".")[0]
				if gxEdit.loadStage(fName):
					gxEdit.curStage = len(gxEdit.stages)
			elif event.type == sdl2.SDL_WINDOWEVENT:
				if event.window.event == sdl2.SDL_WINDOWEVENT_ENTER:
					mouseover = True
				if event.window.event == sdl2.SDL_WINDOWEVENT_LEAVE:
					mouseover = False
			elif event.type == sdl2.SDL_KEYDOWN:
				input.runKeyboard(gxEdit, curStage, scaleFactor, event.key)
			elif event.type == sdl2.SDL_MOUSEMOTION:
				input.runMouseDrag(gxEdit, curStage, event.motion)
			elif event.type == sdl2.SDL_MOUSEWHEEL:
				input.runMouseWheel(curStage, event.wheel)
			elif event.type == sdl2.SDL_MOUSEBUTTONDOWN:
				mouseHeld = True
				input.runMouse1(gxEdit, curStage, event.button)
				input.runMouse2(gxEdit, curStage, event.button)
				input.runMouse3(gxEdit, curStage, event.button)
				input.runMouseDrag(gxEdit, curStage, event.button)
			elif event.type == sdl2.SDL_MOUSEBUTTONUP:
				input.runMouseUp(gxEdit, curStage, event.button)
				mouseHeld = False
				gxEdit.draggedElem = None
			elif event.type == sdl2.SDL_TEXTINPUT:
				if gxEdit.focussedElem:
					gxEdit.focussedElem.handleTextInput(event.text.text.decode("utf-8"), gxEdit)

		#TODO figure out a better way to do this
		def clampCurStage():
			if gxEdit.curStage >= len(gxEdit.stages):
				gxEdit.curStage = len(gxEdit.stages) - 1 
			if gxEdit.curStage < 0:
				gxEdit.curStage = 0
		def clampScroll(stage):
			if stage.scroll >= stage.pack.height - scaleFactor:
				stage.scroll = stage.pack.height - scaleFactor
			
			if stage.scroll < 0:
				stage.scroll = 0

			if stage.hscroll >= stage.pack.width - scaleFactor:
				stage.hscroll = stage.pack.width - scaleFactor
			
			if stage.hscroll < 0:
				stage.hscroll = 0
		def clampMagnification():
			if gxEdit.magnification <= 0:
				gxEdit.magnification = 0.5

		def scrambleEntities(stage):
			types = []
			for o in stage.pack.eve.units:
				types.append((o.id, o.attributes.get('param2')))
			random.shuffle(types)
			for i, o in enumerate(stage.pack.eve.units):
				o.id, o.attributes['param2'] = types[i]

			
		def runTileSelection(stage):
			if not gxEdit.tileSelectionUpdate: return
			tiles = []
			start = stage.selectedTilesStart[:]
			end = stage.selectedTilesEnd[:]

			if end[0] < start[0]:
				start[0], end[0] = end[0], start[0]
			if end[1] < start[1]:
				start[1], end[1] = end[1], start[1]
			for y in range(start[1], end[1]+1):
				for x in range(start[0], end[0]+1):
					tiles.append([x, y])

			if tiles != []: stage.selectedTiles = tiles
			gxEdit.tileSelectionUpdate = False

		def clampUiWindows():
			#TODO: restore original position if user did not move it
			for _, elem in gxEdit.elements.items():
				if elem.y <= 0:
					elem.y = 0
				if elem.x + elem.w - 25 < 0:
					elem.x = -elem.w + 25
				if elem.y + elem.h - 25 < 0:
					elem.x = -elem.w + 25
				if elem.x + 25 > interface.gWindowWidth:
					elem.x = interface.gWindowWidth - 25
				if elem.y + 25 > interface.gWindowHeight:
					elem.y = interface.gWindowHeight - 25

		#windowSurface = window.get_surface()

		#sdl2.ext.fill(windowSurface, sdl2.ext.Color(224,224,224))
		#sdl2.ext.fill(windowSurface, sdl2.ext.Color(0,0,0))

		clampCurStage()
		clampMagnification()
		clampScroll(curStage)
		clampUiWindows()

		curStage = gxEdit.stages[gxEdit.curStage]
		#input.runMouseDrag(gxEdit, curStage)
		runTileSelection(curStage)

		gui.fill()
		if (gxEdit.saveTimer <= 0):
			renderEditor()
			
		gxEdit.saveTimer -= 1

		if introAnimTimer < 60:
			gui.fadeout(introAnimTimer)
		introAnimTimer += 1

		if tickCount >= gxEdit.lastBackupTick + (gxEdit.backupMinutes * 60 * 1000):
			gxEdit.backupStages()
			gxEdit.lastBackupTick = tickCount
			
		if gxEdit.socket and tickCount >= gxEdit.lastMousePosTick + 100:
			if gxEdit.multiplayerState == const.MULTIPLAYER_CLIENT or True:
				mouse = util.getMouseState()

				#maybe it'd be fun to send their zoom level
				x = int(mouse.x // gxEdit.magnification) + int(curStage.hscroll * gxEdit.tileWidth)
				y = int(mouse.y // gxEdit.magnification) + int(curStage.scroll * gxEdit.tileWidth)
				if(x, y) is not gxEdit.lastMousePos:
					if gxEdit.multiplayerState == const.MULTIPLAYER_CLIENT:
						multi.sendMousePosPacket(gxEdit, x, y, gxEdit.curStage)
					elif gxEdit.multiplayerState == const.MULTIPLAYER_HOST:
						try:
							multi.serverSendMousePosPacket(gxEdit, x, y, gxEdit.curStage, "1", gxEdit.serverPlayerNameTemp)
						except:
							pass
					gxEdit.lastMousePosTick = tickCount
					gxEdit.lastMousePos = (x, y)
				

		#TODO: do a getticks system
		renderer.present()
		sdl2.SDL_Delay(12)

		#window.refresh()
	sdl2.ext.quit()
	return 0

if __name__== "__main__":
  sys.exit(main())


#multiplayer editing

#audit log
#User did fill with tiles [x] at [x, y]

#extend class editor?

#sync pxmap, pxeve, pxattr
#verify size is not above kilobytes
#verify checksum with md5

#possibly sync tileset

#launch directly into level -- coop option

#launch directly into level with powerups at scroll, scrollspeed etc
#write debugstart.bin & writeprocessmemory (virtualprotect?) jmp to level load instead of going to menu

#show mouse position of other users

#ruler??
#export map to png


#next on the itnerary
#tooltips
#entity info boxes
#rectangle paint
#copy paint
#undo

#windowtype stage selection
#hidden toolbar at top for open maps../ file view about

#fullscreen mode??!?!?!?!?


#port
#ip
#name
#color


#show grid

#reload tileset button

#bg parallax scrolling

#0.5x zoom type
#/(1*divideFactor)

#statustext
#Hosting...
#() connected! (ip)
#sending .pxm .bmp etc

#pxEdit [00boot]

'''
DONE!!!

#render entity palette
#render tile palette

#render map
#render entities

'''


'''
EditorApp.25=Far back
EditorApp.26=Back
EditorApp.27=Front
EditorApp.28=Far Front
EditorApp.29=Physical
EditorApp.3=By Noxid - 25/09/2012\n
EditorApp.30=Draw
EditorApp.31=Fill
EditorApp.32=Replace
EditorApp.33=Rectangle
EditorApp.34=Copy
EditorApp.35=Show Tile Types
EditorApp.36=Show Grid
EditorApp.37=Show Entity Boxes
EditorApp.38=Show Entity Sprites
EditorApp.39=Show Entity Names'''

#edit bullet atr
#edit npc attr

#render intro
#downwards black line fade


# --render entity tooltips (along with description of entity)

#render ver on menu bg (ala ms beta)




#highlight entities that can be used on this stage
#guxt only? or figure out which entity goes on which sheet for cs..


#render status text bar
#flavor text will appear for 8 seconds at a time, alternating every 5 minutes or so..


#tiles to draw = )yscrollbar) 

#custom scrollbar

#normal entity ui (instant tooltips)

#longform entity placement (large unit bitmaps)
# 	display large bitmaps from RECT table..

#Unsaved changes... Do you wish to save? "Yes, Cancel"

#periodic autosave of map, tileatr, and eve

#decode images
#apply hex patch to exe to disable decode

#copy images to bkupfolder in data

#Various tasks are repeated over and over until the game is completed.
#When you want to open the stage next to the stage you are editing,
#select "Open File" from the menu, and the simple action of selecting the stage
#repeats thousands of times until the game is completed, which makes you uneasy.
#
#The next stage can be set for each stage data so that the next stage can be
#opened with the cursor keys up/down/left/right.
#I want to bring extra energy to the washing machine, clothesline, and closet.

#Arrangement of parts to put between the block and the other place.
#Up until now, I have placed each one by hand, but since
#it is too workable, I added an automatic placement function to the editor.
#It's just now, but I was impressed when it worked properly with one touch.
#It's been about 4 months since I made it.
#Is it going to be completed in the summer? I have to think about efficiency.
