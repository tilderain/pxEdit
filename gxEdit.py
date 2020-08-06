#The Doctor invites you to his garage.
#The doctor's garage awaits [new members]

import io, mmap, sys, time, math, random
import ctypes
import glob, os
from datetime import datetime

from dataclasses import dataclass

from collections import Counter

import pxEve, pxMap, interface, input
import const
import sdl2.ext
from sdl2.sdlttf import *

import multi

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



dataPath = "./guxt/data/"
gamePath = "./guxt/"

#for debugging
dataPath = "./" + dataPath
gamePath = "./" + gamePath

entityInfoName = "entityInfo.txt"

mapPath = "map{}.pxmap"
partsPath = "parts{}.bmp"
attrPath = "parts{}.pxatrb"
eventPath = "event{}.pxeve"
pximgPath = "parts{}.pximg"

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
	def __init__(self, stageNo):
		self.stageNo = stageNo
		self.eve = pxEve.PxEve()
		self.map = pxMap.PxMapAttr()
		self.attr = pxMap.PxMapAttr()

		# tileset texture
		self.parts = None
		self.scroll = 0
		self.hscroll = 0

		# x, y of drag selected tiles in the tileset
		self.selectedTiles = [[0, 0]]
		# x, y of drag selection mousedown
		self.selectedTilesStart = [0, 0]
		# x, y of drag selection mouse up
		self.selectedTilesEnd = [0, 0]
		#TODO: tile selection offset

		self.selectedEntities = []

		self.undoStack = [None]
		self.undoPos = 0

		self.lastSavePos = 0
		self.lastBackupPos = 0

		# to not spam edit commands
		self.lastTileEdit = [None, None]

		self.surface = None

	def createMapSurface(self):
		if self.surface: del self.surface
		self.surface = interface.gSprfactory.create_texture_sprite(interface.gRenderer, (self.map.width*const.tileWidth, self.map.height*const.tileWidth), access=sdl2.SDL_TEXTUREACCESS_TARGET)
	
	def load(self):
		#TODO: open dialogue box to see if there is a newer backup
			#read last modified date
			#Choose the backup you want to open.

		self.eve.load(dataPath + eventPath.format(self.stageNo))
		self.map.load(dataPath + mapPath.format(self.stageNo))
		self.attr.load(dataPath + attrPath.format(self.stageNo))

		self.createMapSurface()

		return True

	def loadParts(self, sprfactory):
		self.parts = sprfactory.from_image(dataPath + partsPath.format(self.stageNo))

	def save(self):
		#if self.lastSavePos == self.undoPos: #TODO: and pxattr not modified
		#	return False

		print("--Saving stage {}...--".format(self.stageNo))
		self.eve.save(dataPath + eventPath.format(self.stageNo))
		self.map.save(dataPath + mapPath.format(self.stageNo))
		self.attr.save(dataPath + attrPath.format(self.stageNo))

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

		print("--Backing up stage {}...--".format(self.stageNo))

		date = datetime.now()
		dateMin = date.strftime(backupTimeFormat)

		eventOut = eventPath.format(self.stageNo)
		mapOut = mapPath.format(self.stageNo)
		
		self.eve.save(dataPath + backupFolderName + "/" + dateMin + "_" + eventOut)
		self.map.save(dataPath + backupFolderName + "/" + dateMin + "_" + mapOut)

		self.lastBackupPos = self.undoPos

		#backupId += 1

		return True

	def renderTilesToSurface(self):
		map = self.map
		sdlrenderer = interface.gRenderer.sdlrenderer
		sdl2.SDL_SetRenderTarget(sdlrenderer, self.surface.texture)
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

				sdl2.SDL_RenderCopy(sdlrenderer, self.parts.texture, srcrect, dstrect)
				#interface.gRenderer.copy(self.parts, srcrect, dstrect)
		sdl2.SDL_SetRenderTarget(sdlrenderer, None)
			
	
	def renderTileToSurface(self, x, y, tx, ty):
		dstx = x * const.tileWidth
		dsty = y * const.tileWidth

		srcx = tx * const.tileWidth
		srcy = ty * const.tileWidth

		sdlrenderer = interface.gRenderer.sdlrenderer
		srcrect = (srcx, srcy, const.tileWidth, const.tileWidth)
		dstrect = (dstx, dsty, const.tileWidth, const.tileWidth)

		sdl2.SDL_SetRenderTarget(sdlrenderer, self.surface.texture)
		interface.gRenderer.copy(self.parts, srcrect, dstrect)
		sdl2.SDL_SetRenderTarget(sdlrenderer, None)

class Editor:
	
	def __init__(self):
		self.entityInfo = []
		self.stages = []
		#TODO: remove this
		self.curStage = 2

		# zoom level
		self.magnification = 3
		self.tilePaletteMag = 2
		self.entityPaletteMag = 1

		self.currentEntity = 0
		self.currentEditMode = const.EDIT_TILE

		self.selectionBoxStart = [-1, -1]
		self.selectionBoxEnd = [-1, -1]

		self.draggingEntities = False
		self.entDragPos = []

		#blinks on save
		self.saveTimer = 0

		# all ui windows
		self.elements = {}

		self.draggedElem = None
		self.dragX = 0
		self.dragY = 0

		# for text input or keyboard navigation
		self.focussedElem = None

		self.fullscreen = False

		# toggle setting to display bg parallax as ingame
		self.parallax = True

		self.backupLimit = 5
		self.backupMinutes = 5
		self.lastBackupTick = 0

		self.tooltipText = []
		self.tooltipStyle = const.STYLE_TOOLTIP_BLACK
		self.tooltipMag = 1


		self.multiplayerState = const.MULTIPLAYER_NONE
		self.socket = None
		self.socket_thread = None
		#ip, name, color? curstage:, mousexy pos, ping, last response time
		self.players = {}
		self.playerId = 0
		self.lastMousePosTick = 0
		self.lastMousePos = (0, 0)

	def readEntityInfo(self):
		try:
			with open(entityInfoName) as f:
				self.entityInfo = [line.split("@") for line in f.read().splitlines()]
				
		except(IOError, FileNotFoundError) as e:
			print("Error reading entityInfo! {}".format(e))
			return False
		return True

	def loadMeta(self, sprfactory):
		result = True
		result &= self.readEntityInfo()
		return result

	def loadStage(self, stageNo):
		for stage in self.stages:
			if stage.stageNo == stageNo:
				print("Error: tried loading an already loaded stage")
				return False
		stage = StagePrj(stageNo)
		result = stage.load()
		self.stages.append(stage)
		return result

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
			stage.map.modify(undo.reverse)
			for pos, tile in undo.reverse:
				stage.renderTileToSurface(pos[0], pos[1], tile[0],
												tile[1])
		elif undo.action == const.UNDO_ENTITY_MOVE:
			stage.eve.replace(undo.reverse)

		stage.undoPos -= 1
		

	def executeRedo(self):
		stage = self.stages[self.curStage]
		undoStack = stage.undoStack
		undoPos = stage.undoPos + 1

		if undoPos > len(undoStack)-1:
			return

		redo = undoStack[undoPos]

		if redo.action == const.UNDO_TILE:
			stage.lastTileEdit = [None, None]
			stage.map.modify(redo.forward)
			for pos, tile in redo.forward:
				stage.renderTileToSurface(pos[0], pos[1], tile[0],
												tile[1])
		elif redo.action == const.UNDO_ENTITY_MOVE:
			stage.eve.replace(redo.forward)												
		stage.undoPos += 1

	def backupStages(self):
		if not os.path.exists(dataPath + backupFolderName):
			os.makedirs(dataPath + backupFolderName)

		for stage in self.stages:
			if not stage.backup():
				continue

		#remove oldest backups
		backupFiles = sorted(glob.glob(dataPath + backupFolderName + "/*"))
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


gxEdit = Editor()

def main():
	sdl2.ext.init()
	#To disable texture destruction on window resize
	sdl2.SDL_SetHint(sdl2.SDL_HINT_RENDER_DRIVER, b"opengl")

	if TTF_Init() == -1:
		print("Error initting ttf: ", TTF_GetError())
		return

	interface.gFont = TTF_OpenFont(b"sserife.fon", ctypes.c_int(12))

	if not interface.gFont:
		print("error opening font:", TTF_GetError())
		return

	#TODO window.rect
	defaultWindowWidth = 640
	defaultWindowHeight = 480

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
	for i in range(1,7):
		if i == 5: print("stage... FIVE")
		gxEdit.loadStage(i)
		gxEdit.stages[i-1].loadParts(sprfactory)
		gxEdit.stages[i-1].renderTilesToSurface()


		

	introAnimTimer = 0

	running = True
	mouseover = True

	mouseHeld = False


	#gxEdit.elements.append(UIWindow(100, 100, 128, 64))
	#gxEdit.elements.append(interface.UIWindow(22, 22, 256, 256))
	#gxEdit.elements.append(interface.UIWindow(300, 300, 260, 272, const.WINDOW_TILEPALETTE))

	gxEdit.elements["tilePalette"] = interface.TilePaletteWindow(400, 300, 256, 280, const.WINDOW_TILEPALETTE)
	gxEdit.elements["entityPalette"] = interface.EntityPaletteWindow(400, 0, 256, 156, const.WINDOW_ENTITYPALETTE)

	gxEdit.elements["toolsWindow"] = interface.ToolsWindow(400, 200, 80, 64, const.WINDOW_TOOLS)

	gxEdit.elements["uiTooltip"] = interface.UITooltip(0,0,1,1)

	gxEdit.elements["entEdit"] = interface.EntityEditWindow(20,20,150,25)

	gxEdit.elements["mapSizeDialog"] = interface.MapResizeDialog(20,20,104,88)

	gxEdit.elements["dialogMultiplayer"] = interface.MultiplayerWindow(0,0,220,80)

	def renderEditor():
		#TODO: placeholder

		gui.renderMainBg(introAnimTimer, mouseover)
		gui.renderEditorBg()
		gui.renderTiles(gxEdit, curStage)
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
		if event.contents.type == sdl2.SDL_WINDOWEVENT:
			if event.contents.window.event == sdl2.SDL_WINDOWEVENT_SIZE_CHANGED:
				interface.gWindowWidth = event.contents.window.data1
				interface.gWindowHeight = event.contents.window.data2
				
				renderEditor()
				renderer.present()
		return 0
	reFunc = sdl2.SDL_EventFilter(resizeEventWatch)
	sdl2.SDL_AddEventWatch(reFunc, window.window)

	tickCount = sdl2.timer.SDL_GetTicks()
	gxEdit.lastBackupTick = tickCount

	while running:

		tickCount = sdl2.timer.SDL_GetTicks()
		
		curStage = gxEdit.stages[gxEdit.curStage]
		
		#height of window in tiles
		scaleFactor = (interface.gWindowHeight // const.tileWidth // gxEdit.magnification)
		events = sdl2.ext.get_events()

		multiwindowstring = ""
		if gxEdit.multiplayerState:
			if gxEdit.multiplayerState == const.MULTIPLAYER_HOST:
				multiwindowstring = "**Hosting**"
			elif gxEdit.multiplayerState == const.MULTIPLAYER_CLIENT:
				multiwindowstring = "**Connected**"

		#set windowname
		interface.gWindow.title = windowName + " [" + "map" + str(gxEdit.curStage+1) + "]" + " " + multiwindowstring
		
		for event in events:
			if event.type == sdl2.SDL_QUIT:
				running = False
				break
			elif event.type == sdl2.SDL_DROPFILE:
				#TODO: drop an exe or event/map to load singular
				pass
			elif event.type == sdl2.SDL_WINDOWEVENT:
				if event.window.event == sdl2.SDL_WINDOWEVENT_ENTER:
					mouseover = True
				if event.window.event == sdl2.SDL_WINDOWEVENT_LEAVE:
					mouseover = False
			elif event.type == sdl2.SDL_KEYDOWN:
				input.runKeyboard(gxEdit, curStage, scaleFactor, event.key)
			elif event.type == sdl2.SDL_MOUSEWHEEL:
				input.runMouseWheel(curStage, event.wheel)
			elif event.type == sdl2.SDL_MOUSEBUTTONDOWN:
				mouseHeld = True
				input.runMouse1(gxEdit, curStage, event.button)
				input.runMouse2(gxEdit, curStage, event.button)
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
			if stage.scroll >= stage.map.height - scaleFactor:
				stage.scroll = stage.map.height - scaleFactor
			
			if stage.scroll < 0:
				stage.scroll = 0

			if stage.hscroll >= stage.map.width - scaleFactor:
				stage.hscroll = stage.map.width - scaleFactor
			
			if stage.hscroll < 0:
				stage.hscroll = 0
		def clampMagnification():
			if gxEdit.magnification <= 0:
				gxEdit.magnification = 0.5

		def scrambleEntities(stage):
			types = []
			for o in stage.eve._entities:
				types.append((o.type1, o.type2))
			random.shuffle(types)
			for i, o in enumerate(stage.eve._entities):
				o.type1, o.type2 = types[i]

			
		def runTileSelection(stage):
			tiles = []
			start = stage.selectedTilesStart[:]
			end = stage.selectedTilesEnd[:]

			if end[0] < start[0]:
				start[0], end[0] = end[0], start[0]
			if end[1] < start[1]:
				start[1], end[1] = end[1], start[1]
			for x in range(start[0], end[0]+1):
				for y in range(start[1], end[1]+1):
					tiles.append([x, y])

			if tiles != []: stage.selectedTiles = tiles

		def clampUiWindows():
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
		input.runMouseDrag(gxEdit, curStage)
		if mouseHeld: runTileSelection(curStage)

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
			if gxEdit.multiplayerState == const.MULTIPLAYER_CLIENT:
				mouse = sdl2.SDL_MouseButtonEvent()
				x,y = ctypes.c_int(0), ctypes.c_int(0)
				mouse.button = sdl2.SDL_GetMouseState(x, y)
				mouse.x, mouse.y = x.value, y.value

				if(mouse.x, mouse.y) not gxEdit.lastMousePos:
					multi.sendMousePosPacket(gxEdit, mouse.x, mouse.y)
					gxEdit.lastMousePosTick = tickCount
					gxEdit.lastMousePos = (mouse.x, mouse.y)
				

		#TODO: do a getticks system
		renderer.present()
		sdl2.SDL_Delay(8)

		#window.refresh()
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