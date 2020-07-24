#The Doctor invites you to his garage.
#The doctor's garage awaits [new members]

import io, mmap, sys, time, math, random
from dataclasses import dataclass

import pxEve, pxMap
import sdl2.ext

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

configName = "dgConf.txt"
#currently only Graphics Resolution
modSettingsName = "dgSettings.txt"
unitsName = "units.bmp"

#spawned from children?
entityChildIds = [5, 12, 16, 17, 33, 34, 36, 50, 51, 52, 53, 55, 57, 62, 71, 77, 78, 79, 80, 82, 89, 95, 101, 103, 109, 110, 112, 113]
#total entity ids
entityFuncCount = 121

dataPath = "./guxt/data/"
gamePath = "./guxt/"

#for debugging
dataPath = "/home/god/Desktop/theDoctorsGarage/" + dataPath
gamePath = "/home/god/Desktop/theDoctorsGarage/" + gamePath

entityInfoName = "entityInfo.txt"

mapPath = "map{}.pxmap"
partsPath = "parts{}.bmp"
attrPath = "parts{}.pxatrb"
eventPath = "event{}.pxeve"
pximgPath = "parts{}.pximg"

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
		self.parts = None
		self.backupId = 0
		self.scroll = 0

	def load(self):
		#open dialogue box to see if there is a newer backup

		self.eve.load(dataPath + eventPath.format(self.stageNo))
		self.map.load(dataPath + mapPath.format(self.stageNo))
		self.attr.load(dataPath + attrPath.format(self.stageNo))
		
		#update the backup number based off the highest id on any of the 3

		return True

	def loadParts(self, sprfactory):
		self.parts = sprfactory.from_image(dataPath + partsPath.format(self.stageNo))

	def save(self):
		self.eve.save(dataPath + eventPath.format(self.stageNo))
		self.map.save(dataPath + mapPath.format(self.stageNo))
		self.attr.save(dataPath)
		#save if there are any changes
		pass
	def backup(self):
		#periodic backup...
		#if there are changes to the file, back it up

		#etc.save()

		#backupId += 1
		pass

class Editor:
	
	def __init__(self):
		self.entityInfo = []
		self.stages = []
		self.curStage = 0
		self.units = None
		self.magnification = 3

	def readEntityInfo(self):
		try:
			with open(entityInfoName) as f:
				self.entityInfo = f.read().splitlines()
		except(IOError, FileNotFoundError) as e:
			print("Error reading entityInfo! {}".format(e))
			return False
		return True

	def loadUnits(self, sprfactory):
		self.units = sprfactory.from_image(unitsName)
		return True
		#TODO

	def loadMeta(self, sprfactory):
		result = True
		result &= self.readEntityInfo()
		result &= self.loadUnits(sprfactory)
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

class UIWindow:
	#Draggable area, relative to the origin.
	
	pass



def main():
	sdl2.ext.init()

	RESOURCES = sdl2.ext.Resources(__file__, "BITMAP")
	window = sdl2.ext.Window("Doctor's Garage", size=(640, 480), flags=sdl2.SDL_WINDOW_RESIZABLE)
	window.show()
	renderer = sdl2.ext.Renderer(window, flags=sdl2.SDL_RENDERER_SOFTWARE)
	sprfactory = sdl2.ext.SpriteFactory(sdl2.ext.TEXTURE, renderer=renderer)
	uifactory = sdl2.ext.UIFactory(sprfactory)

	windowBg = sprfactory.from_image(RESOURCES.get_path("dgBg.bmp"))
	colorBlack = sprfactory.from_color(sdl2.ext.Color(0,0,0),(32,32))
	#colorOrange = sprfactory.from_color(sdl2.ext.Color(250,150,0),(16,16))
	colorOrange = sdl2.ext.Color(250,150,0)
	colorOrangeDark = sdl2.ext.Color(160,100,0)

	windowBg2 = sprfactory.from_image(RESOURCES.get_path("dgBg2.bmp"))
	
	windowBg._size = (windowBg.size[0] * 2, windowBg.size[1] * 2)
	windowBg2._size = (windowBg2.size[0] * 2, windowBg2.size[1] * 2)
	#easy

	gxEdit = Editor()
	gxEdit.loadMeta(sprfactory)
	for i in range(1,7):
		if i == 5: print("stage... FIVE")
		gxEdit.loadStage(i)
		gxEdit.stages[i-1].loadParts(sprfactory)

	introAnimTimer = 0

	running = True
	mouseover = True

	while running:
		events = sdl2.ext.get_events()
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
				tempRunInput(event.key)
			elif event.type == sdl2.SDL_MOUSEWHEEL:
				tempRunInputWheel(event.wheel)


		tileScale = 1
		tileWidth = 16 * tileScale

		def renderTiles(stage):
			map = stage.map
			for i, tile in enumerate(map.tiles):
				
				y = i // map.width
				if y < stage.scroll:
					continue
				if (y - stage.scroll) * tileWidth > window.size[1]:	
					continue
				y -= stage.scroll

				x = i % map.width
				dstx = x * tileWidth
				dsty = y * tileWidth

				x = tile % 16 #the magic number so that each 4 bits in a byte corresponds to the x, y position in the tileset
				y = tile // 16
				srcx = x * tileWidth
				srcy = y * tileWidth

				mag = gxEdit.magnification
				srcrect = (srcx, srcy, tileWidth, tileWidth)
				dstrect = (dstx*mag, dsty*mag, tileWidth*mag, tileWidth*mag)
				#srcrect = 
				renderer.copy(stage.parts, srcrect=srcrect, dstrect=dstrect)

		def renderEntities(stage):
			eve = stage.eve.get()
			for o in eve:
				
				y = o.y
				if y < stage.scroll:
					continue
				if (y - (stage.scroll)) > window.size[1]:	
					continue
				y -= stage.scroll * 2
				x = o.x
				dstx = x * (tileWidth // 2)
				dsty = y * (tileWidth // 2)

				x = o.type1 % 16 #row size in units.bmp
				y = o.type1 // 16
				srcx = x * tileWidth
				srcy = y * tileWidth

				mag = gxEdit.magnification
				srcrect = (srcx, srcy, tileWidth, tileWidth)
				dstrect = (dstx*mag, dsty*mag, tileWidth*mag, tileWidth*mag)

				renderer.copy(gxEdit.units, srcrect=srcrect, dstrect=dstrect)

				#entity borders
				'''
				dstrect = (dstx+tileWidth, dsty, dstx, dsty,
								dstx, dsty, dstx, dsty+tileWidth)
				dstrect2 = (dstx+tileWidth, dsty+tileWidth, dstx+tileWidth, dsty,
								dstx+tileWidth, dsty+tileWidth, dstx, dsty+tileWidth)
				dstrect = [i * mag for i in dstrect]
				dstrect2 = [i * mag for i in dstrect2]

				renderer.draw_line(dstrect, color=colorOrange)
				renderer.draw_line(dstrect2, color=colorOrangeDark)'''

		def scrambleEntities():
			stage = gxEdit.stages[gxEdit.curStage]
			types = []
			for o in stage.eve._entities:
				types.append((o.type1, o.type2))
			random.shuffle(types)
			for i, o in enumerate(stage.eve._entities):
				o.type1, o.type2 = types[i]
			
		def clampMagnification():
			if gxEdit.magnification <= 0:
				gxEdit.magnification = 1

		clampMagnification()
		scaleFactor = (window.size[1] // tileWidth // gxEdit.magnification)
		def tempRunInput(key):
			stage = gxEdit.stages[gxEdit.curStage]
			sym = key.keysym.sym
			if sym == sdl2.SDLK_LEFT:
				gxEdit.curStage -= 1
			if sym == sdl2.SDLK_RIGHT:
				gxEdit.curStage += 1

			if sym == sdl2.SDLK_DOWN:
				stage.scroll += 1
			if sym == sdl2.SDLK_UP:
				stage.scroll -= 1
			if sym == sdl2.SDLK_HOME:
				stage.scroll = 0
			if sym == sdl2.SDLK_END:
				stage.scroll = stage.map.height - scaleFactor
			if sym == sdl2.SDLK_PAGEDOWN:
				stage.scroll += int(scaleFactor // 1.5)
			if sym == sdl2.SDLK_PAGEUP:
				stage.scroll -= int(scaleFactor // 1.5)

			if sym == sdl2.SDLK_MINUS:
				gxEdit.magnification -= 1

			if sym == sdl2.SDLK_EQUALS:
				gxEdit.magnification += 1

			if sym == sdl2.SDLK_d:
				scrambleEntities()
			if sym == sdl2.SDLK_s:
				stage.save()


			clampCurStage()

		def tempRunInputWheel(wheel):
			stage = gxEdit.stages[gxEdit.curStage]
			stage.scroll -= wheel.y

		def clampScroll():
			stage = gxEdit.stages[gxEdit.curStage]
			if stage.scroll >= stage.map.height - scaleFactor:
				stage.scroll = stage.map.height - scaleFactor
			
			if stage.scroll < 0:
				stage.scroll = 0
		def clampCurStage():
			if gxEdit.curStage >= len(gxEdit.stages):
				gxEdit.curStage = len(gxEdit.stages) - 1 
			if gxEdit.curStage < 0:
				gxEdit.curStage = 0

		def renderMainBg():
			if introAnimTimer > 15 and introAnimTimer < 25 and introAnimTimer % 3 == 0 or introAnimTimer > 25:
				if mouseover:
					renderer.copy(windowBg, dstrect=(windowBg.x, windowBg.y, windowBg.size[0], windowBg.size[1]))
				else:
					renderer.copy(windowBg2, dstrect=(windowBg.x, windowBg.y, windowBg.size[0], windowBg.size[1]))

		def fadeout():
			renderer.copy(colorBlack, dstrect=(0, window.size[1]//2 + math.ceil(window.size[1] * 0.05 * introAnimTimer), windowSurface.w, windowSurface.h))
			renderer.copy(colorBlack, dstrect=(0, -window.size[1]//2 - math.ceil(window.size[1] * 0.05 * introAnimTimer), windowSurface.w, windowSurface.h))
			renderer.copy(colorBlack, dstrect=(window.size[0]//2 + math.ceil(window.size[0] * 0.05 * introAnimTimer), 0, windowSurface.w, windowSurface.h))
			renderer.copy(colorBlack, dstrect=(-window.size[0]//2 - math.ceil(window.size[0] * 0.05 * introAnimTimer), 0, windowSurface.w, windowSurface.h))

		windowSurface = window.get_surface()

		sdl2.ext.fill(windowSurface, sdl2.ext.Color(224,224,224))
		#windowBg._size = (math.ceil(windowBg._size[0] * 1.5), math.floor(windowBg._size[1] * 1.5))

		windowBg.x = windowSurface.w//2 - windowBg.size[0]//2
		windowBg.y = windowSurface.h//2 - windowBg.size[1]//2

		#renderer.copy(colorBlack, dstrect=(0, math.ceil(window.size[1] * 0.05 * introAnimTimer), windowSurface.w, windowSurface.h))

		clampScroll()

		renderMainBg()
		renderTiles(gxEdit.stages[gxEdit.curStage])
		renderEntities(gxEdit.stages[gxEdit.curStage])


		if introAnimTimer < 60:
			fadeout()
		introAnimTimer += 1

		#TODO: do a getticks system
		sdl2.SDL_Delay(20)
		renderer.present()
		#window.refresh()
	return 0
	


	'''
	for i in range(1,6):
		if i == 5: print("stage... FIVE")
		gxEdit.loadStage(i)

	for stage in gxEdit.stages:
		print("====stage {}=====".format(stage.stageNo))
		events = stage.eve.get()
		for o in events:
			pxEve.printEntity(o, gxEdit.entityInfo)
			#pass
	'''

	#gxEdit.stages[1].eve.save(dataPath, 7)


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

#show mouse position of other users

#edit bullet atr
#edit npc attr

#render intro
#downwards black line fade

#render entity palette
# --render entity tooltips (along with description of entity)

#render ver on menu bg (ala ms beta)

#render tile palette
#render map
#render entities

#highlight entities that can be used on this stage

#tiles to draw = )yscrollbar) 

#custom scrollbar

#normal entity ui (instant tooltips)

#longform entity placement (large unit bitmaps)

#Unsaved changes... Do you wish to save? "Yes, Cancel"

#periodic autosave of map, tileatr, and eve

#decode images
#apply hex patch to exe to disable decode

#copy images to bkupfolder in data

