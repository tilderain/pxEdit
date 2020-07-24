# pylint: disable=no-member

import sdl2.ext
import const
import math
import ctypes

import util

#from gxEdit import gxEdit as gxEdit

unitsName = "units.bmp"

surfaceCount = 64
#surface enum
SURF_0 = 0
SURF_WINDOWBG = 1
SURF_WINDOWBG2 = 2
SURF_COLOR_BLACK = 3
SURF_COLOR_ORANGE = 4
SURF_COLOR_ORANGE_DARK = 5
SURF_COLOR_RED_TRANSPARENT = 6
SURF_COLOR_ORANGE_TRANSPARENT = 7
SURF_UNITS = 8
SURF_UIWINDOW = 9
SURF_COLOR_BLUE = 10
SURF_COLOR_WHITE_TRANSPARENT = 11
SURF_COLOR_GREEN = 12

#rect enums
rectUIWindow1TopLeft = (0, 0, 2, 2)
rectUIWindow1TopRight = (4, 0, 2, 2)
rectUIWindow1BottomLeft = (0, 3, 2, 2)
rectUIWindow1BottomRight = (4, 3, 2, 2)

rectUIWindow1Top = (2, 0, 1, 1)
rectUIWindow1Right = (4, 2, 1, 1)
rectUIWindow1Bottom = (0, 2, 1, 1)
rectUIWindow1Left = (0, 2, 1, 1)


rectUIWindow1ColorFill = (2, 2, 1, 1)

rectUIWindow2TopLeft = (6, 0, 2, 2)
rectUIWindow2TopRight = (10, 0, 2, 2)
rectUIWindow2BottomLeft = (6, 3, 2, 2)
rectUIWindow2BottomRight = (10, 3, 2, 2)

rectUIWindow2Top = (8, 0, 1, 1)
rectUIWindow2Right = (10, 2, 1, 1)
rectUIWindow2Bottom = (8, 4, 1, 1)
rectUIWindow2Left = (6, 2, 1, 1)

rectWindowTextPalette = (0, 53, 68, 12)
rectWindowTextTools = (0, 64, 54, 12)

rectButtonMinimizeNormal = (80, 5, 16, 16)
rectButtonMinimizeClicked = (96, 5, 16, 16)

gRenderer = None
gWindow = None
gSprfactory = None
gInterface = None

gWindowWidth = 0
gWindowHeight = 0

gDrawBoxRect = sdl2.SDL_Rect(0,0,0,0)

class UIElement:
	def __init__(self, x, y, w, h, parent, rect=(0,0,0,0), style=0, tooltip=None):
		self.x = x
		self.y = y
		self.w = w
		self.h = h

		self.rect = rect

		self.tooltip = tooltip

		self.parent = parent


	def handleMouse1():
		return False

	def handleMouse2():
		return False

	def handleMouse1Up(self, mouse, gxEdit):
		return False

	def handleMouseOver():
		return False


	def render(self, x, y):
		windowsurf = gInterface.surfaces[SURF_UIWINDOW]
		gInterface.renderer.copy(windowsurf, srcrect=self.rect, 
			dstrect=(self.x + x, self.y + y, self.rect[2], self.rect[3]))

BUTTON_NORMAL = 0
BUTTON_CLICKED = 1
BUTTON_ACTIVE = 2

BUTTON_TYPE_NORMAL = 0
BUTTON_TYPE_RADIO = 1



class UIButton:
	def __init__(self, x, y, w, h, parent, rect=(0,0,0,0), style=0, tooltip=None, type=None):
		UIElement.__init__(self, x, y, w, h, parent, rect, style, tooltip)

		self.rectNormal = rectButtonMinimizeNormal
		self.rectActive = None
		self.rectHover = None
		self.rectClick = rectButtonMinimizeClicked

		self.rect = self.rectNormal

		self.state = BUTTON_NORMAL

		self.type = type

	def handleMouse1(self, mouse):
		self.state = BUTTON_CLICKED
		self.rect = self.rectClick
		return True

	def handleMouse2(self):
		return False

	def handleMouse1Up(self, mouse, gxEdit):
		self.state = BUTTON_NORMAL
		self.rect = rectButtonMinimizeNormal

		if util.inWindowElemBoundingBox(mouse, self.parent, self):
			if self.type == BUTTON_TYPE_RADIO:
				self.state = BUTTON_ACTIVE
				self.rect = self.rectActive

			self.onAction(self.parent, self)				
		#self.rect = self.rectActive
		return True

	def handleMouseOver():
		return False

	def onAction(self, parent, elem):
		pass

	def render(self, x, y):
		UIElement.render(self, x, y)


class UIElementStretch(UIElement):
	def __init__(self, x, y, w, h, parent, rect, style=0, tooltip=None):
		UIElement.__init__(self, x, y, w, h, parent, rect, style, tooltip)

	def render(self, x, y):
		windowsurf = gInterface.surfaces[SURF_UIWINDOW]
		gInterface.renderer.copy(windowsurf, srcrect=self.rect, 
			dstrect=(self.x + x, self.y + y, w, h))


def minimizeButtonAction(window, elem):
	window.visible = False

class UIWindow:
	def __init__(self, x, y, w, h, type=const.WINDOW_NONE, style=0):
		self.x = x
		self.y = y
		self.w = w
		self.h = h

		self.type = type
		self.style = style

		self.elements = {}

		self.draghitbox = [0, 0, self.w, 24]

		self.surface = gSprfactory.from_color(sdl2.ext.Color(0,0,0),(w,h))

		self.activeElem = None

		self.visible = True

		self.priority = 0

	def handleMouse1(self, mouse, gxEdit):

		for _, elem in self.elements.items():
			if util.inWindowElemBoundingBox(mouse, self, elem) and elem.handleMouse1(mouse):
				self.activeElem = elem
				return True
		return False

	def handleMouse1Up(self, mouse, gxEdit):
		for _, elem in self.elements.items():
			if(util.inWindowElemBoundingBox(mouse, self, elem) and elem.handleMouse1Up(mouse, gxEdit)):
				self.activeElem = None
				return True
		return False

	def handleMouse2():
		return False

	def render(self, gxEdit, stage):
		for _, elem in self.elements.items():
			elem.render(self.x, self.y)
		

class TilePaletteWindow(UIWindow):
	def __init__(self, x, y, w, h, type=const.WINDOW_TILEPALETTE, style=0):
		UIWindow.__init__(self, x, y, w, h, type, style)

		self.elements["picker"] = UIElement(0, 24, 0, 0, self, (0,0,0,0))
		self.elements["textPalette"] = UIElement(6, 6, 1, 1, self, rectWindowTextPalette)

		self.elements["buttonMinimize"] = UIButton(0, 4, 16, 16, self)
		self.elements["buttonMinimize"].onAction = minimizeButtonAction

	def render(self, gxEdit, stage):
		UIWindow.render(self, gxEdit, stage)

		mag = gxEdit.tilePaletteMag

		#reset width
		self.w = (gxEdit.stages[gxEdit.curStage].attr.width * const.tileWidth) * mag
		self.h = (gxEdit.stages[gxEdit.curStage].attr.height * const.tileWidth) * mag + 24 + 2
		self.draghitbox = [0, 0, self.w, 24]

		self.elements["buttonMinimize"].x = self.w - 24
		##

		srcrect = stage.parts.area
		
		dstx = self.x + self.elements["picker"].x
		dsty = self.y + self.elements["picker"].y



		#TODO: add dstrect mag
		dstrect = (dstx, dsty, stage.parts.size[0] * mag, stage.parts.size[1] * mag)
		gInterface.renderer.copy(stage.parts, srcrect=srcrect, dstrect=dstrect)

		#TODO: add selected tile border (properly)
		if gxEdit.currentEditMode == const.EDIT_TILE:
			dstx = dstx + ((stage.selectedTilesStart[0] * const.tileWidth) * mag)
			dsty = dsty + ((stage.selectedTilesStart[1] * const.tileWidth) * mag)
			w = (stage.selectedTilesEnd[0]+1 - stage.selectedTilesStart[0]) * const.tileWidth * mag
			h =  (stage.selectedTilesEnd[1]+1 - stage.selectedTilesStart[1]) * const.tileWidth * mag

			gInterface.drawBox(gInterface.renderer, dstx, dsty, w, h)

		#show current tile box
		pass

	def handleMouse1(self, mouse, gxEdit):
		return UIWindow.handleMouse1(self, mouse, gxEdit)
		x = (mouse.x - tilePalette.x + tilePalette.elements["picker"].x) // const.tileWidth
		y = (mouse.y - tilePalette.y + tilePalette.elements["picker"].y) // const.tileWidth

		if x >= stage.attr.width:
			return
		if y >= stage.attr.height:
			return

		if x < 0 or y < 0:
			return
		gxEdit.currentEditMode = const.EDIT_TILE
		stage.selectedTilesStart = [x, y]
		stage.selectedTiles = [[x, y]]

	def handleMouseDrag(self, gxEdit):
		return False
		


class EntityPaletteWindow(UIWindow):
	def __init__(self, x, y, w, h, type=const.WINDOW_TILEPALETTE, style=0):
		UIWindow.__init__(self, x, y, w, h, type, style)

		self.elements["picker"] = UIElement(0, 24, 0, 0, self, (0,0,0,0))
		self.elements["textPalette"] = UIElement(6, 6, 1, 1, self, rectWindowTextPalette)

	def render(self, gxEdit, stage):
		UIWindow.render(self, gxEdit, stage)

		mag = gxEdit.entityPaletteMag
		units = gInterface.surfaces[SURF_UNITS]
		srcrect = units.area

		dstx = self.x + self.elements["picker"].x
		dsty = self.y + self.elements["picker"].y
		
		#TODO: add dstrect mag

		dstrect = (dstx, dsty, units.size[0] * mag, units.size[1] * mag)
		gInterface.renderer.copy(units, srcrect=srcrect, dstrect=dstrect)

		#TODO: add selected ent border (properly)
		if gxEdit.currentEditMode == const.EDIT_ENTITY:
			dstx = dstx + ((gxEdit.selectedEntity % 16) * const.tileWidth * mag)
			dsty = dsty + ((gxEdit.selectedEntity // 16) * const.tileWidth * mag)
			gInterface.drawBox(gInterface.renderer, dstx, dsty, const.tileWidth * mag, const.tileWidth * mag)

		#crashing entities
		for i in range (const.entityFuncCount):
			if i in const.entityChildIds:
				dstx = (i % 16) * const.tileWidth * mag + (self.x + self.elements["picker"].x)
				dsty = (i // 16) * const.tileWidth * mag + (self.y + self.elements["picker"].y) 
				gInterface.renderer.copy(gInterface.surfaces[SURF_COLOR_RED_TRANSPARENT], dstrect=(dstx, dsty, const.tileWidth, const.tileWidth))


def toggleTilePalette():
	pass	

class ToolsWindow(UIWindow):
	def __init__(self, x, y, w, h, type=const.WINDOW_TOOLS, style=0):
		UIWindow.__init__(self, x, y, w, h, type, style)

		self.elements["textTools"] = UIElement(2, 2, 0, 0, self, rectWindowTextTools)

		self.elements["butToggleTilePalette"] = UIButton(4, 24, 16, 16, self)
		#self.elements["butToggleTilePalette"].onAction = 


class YesNoCancelDialog(UIWindow):
	pass

class YesNoDialog(UIWindow):
	pass

#this probably shouldn't be a class but i don't want to refactor it again
class Interface:
	def __init__(self, renderer, window, sprfactory):
		self.renderer = renderer
		self.window = window
		self.sprfactory = sprfactory

		self.surfaces = [None] * surfaceCount

	def loadSurfaces(self):
		RESOURCES = sdl2.ext.Resources(__file__, "BITMAP")

		self.surfaces[SURF_WINDOWBG] = self.sprfactory.from_image(RESOURCES.get_path("dgBg.bmp"))
		self.surfaces[SURF_WINDOWBG2] = self.sprfactory.from_image(RESOURCES.get_path("dgBg2.bmp"))
		self.surfaces[SURF_COLOR_BLACK] = self.sprfactory.from_color(sdl2.ext.Color(0,0,0),(32,32))
		self.surfaces[SURF_COLOR_ORANGE] = sdl2.ext.Color(0,255,0)
		self.surfaces[SURF_COLOR_ORANGE_DARK] = sdl2.ext.Color(0,255,0)
		self.surfaces[SURF_COLOR_GREEN] = self.sprfactory.from_color(sdl2.ext.Color(0,255,0),(32,32))

		self.surfaces[SURF_COLOR_BLUE] = self.sprfactory.from_color(sdl2.ext.Color(84,108,128),(32,32))


		self.surfaces[SURF_COLOR_RED_TRANSPARENT] = self.sprfactory.from_color(sdl2.ext.Color(255,0,0, 80), size=(32, 32),
                   masks=(0xFF000000,           
                          0x00FF0000,           
                          0x0000FF00,           
                          0x000000FF))   

		self.surfaces[SURF_COLOR_ORANGE_TRANSPARENT] = self.sprfactory.from_color(sdl2.ext.Color(250,150,0, 128), size=(32, 32),
                   masks=(0xFF000000,           
                          0x00FF0000,           
                          0x0000FF00,           
                          0x000000FF))   

		self.surfaces[SURF_COLOR_WHITE_TRANSPARENT] = self.sprfactory.from_color(sdl2.ext.Color(255,255,255, 128), size=(32, 32),
           masks=(0xFF000000,           
                  0x00FF0000,           
                  0x0000FF00,           
                  0x000000FF))   

		self.surfaces[SURF_UNITS] = self.sprfactory.from_image(unitsName)


		self.surfaces[SURF_UIWINDOW] = self.sprfactory.from_image(RESOURCES.get_path("Window.bmp"))
		#TODO error handling when can't find file

	def RenderMapParts(self):
		pass

	def PutMapParts(self):
		pass

	def loadUnits(self):
		pass

	def MakeSurface_Color(self, color, surf_no):
		pass

	def renderEntityPalette(self, gxEdit, stage):
		return


	def renderTiles(self, gxEdit, stage):
		map = stage.map
		mag = gxEdit.magnification

		#TODO: render tiles out onto a surface once and just draw the relevant part

		srcx = stage.hscroll * const.tileWidth
		srcy = stage.scroll * const.tileWidth

		sizex = min(gWindowWidth*max(1, int(1/gxEdit.magnification)), stage.surface.size[0], stage.surface.size[0] - srcx)
		sizey = min(gWindowHeight*max(1, int(1/gxEdit.magnification)), stage.surface.size[1], stage.surface.size[1] - srcy)

		srcrect = (srcx, srcy, sizex, sizey)
		dstrect = (0, 0, int(sizex*mag), int(sizey*mag))

		self.renderer.copy(stage.surface.texture, srcrect=srcrect, dstrect=dstrect)

		for i, tile in enumerate(map.tiles):
			break
			map = stage.map
			y = i // map.width
			if y < stage.scroll:
				continue
			if (y - stage.scroll) * const.tileWidth > gWindowHeight:	
				continue
			y -= stage.scroll

			x = i % map.width
			dstx = x * const.tileWidth
			dsty = y * const.tileWidth

			x = tile % 16 #the magic number so that each 4 bits in a byte corresponds to the x, y position in the tileset
			y = tile // 16
			srcx = x * const.tileWidth
			srcy = y * const.tileWidth

			
			srcrect = (srcx, srcy, const.tileWidth, const.tileWidth)
			dstrect = (dstx*mag, dsty*mag, const.tileWidth*mag, const.tileWidth*mag)
			#srcrect = 
			self.renderer.copy(stage.parts, srcrect=srcrect, dstrect=dstrect)

		#TODO: add hovered over tile border
		mouse = sdl2.SDL_MouseButtonEvent()
		x,y = ctypes.c_int(0), ctypes.c_int(0)
		mouse.button = sdl2.SDL_GetMouseState(x, y)
		mouse.x, mouse.y = x.value, y.value

		x = int(mouse.x // (const.tileWidth * mag))
		y = int(mouse.y // (const.tileWidth * mag))

		if x >= map.width or y >= map.height: return

		x *= int(const.tileWidth * mag)
		y *= int(const.tileWidth * mag)

		w = stage.selectedTilesEnd[0] - stage.selectedTilesStart[0] + 1
		h = stage.selectedTilesEnd[1] - stage.selectedTilesStart[1] + 1

		w *= int(const.tileWidth * mag)
		h *= int(const.tileWidth * mag)


		self.renderer.copy(gInterface.surfaces[SURF_COLOR_WHITE_TRANSPARENT], dstrect=(x, y, w, h))




	def renderTilePalette(self, gxEdit, stage):
		#TODO: placeholder
		pass




	def renderEntities(self, gxEdit, stage):
		#TODO: render to surface
		eve = stage.eve.get()
		units = self.surfaces[SURF_UNITS]
		xys = []
		for o in eve:
			y = o.y
			if y < stage.scroll*2:
				continue
			if (y - stage.scroll*2) * const.tileWidth//2 > gWindowHeight:	
				continue
			y -= stage.scroll*2

			x = o.x
			if x < stage.hscroll*2:
				continue
			if (y - stage.hscroll*2) * const.tileWidth//2 > gWindowWidth:
				continue
			x -= stage.hscroll*2

			dstx = x * (const.tileWidth // 2)
			dsty = y * (const.tileWidth // 2)

			x = o.type1 % 16 #row size in units.bmp
			y = o.type1 // 16
			srcx = x * const.tileWidth
			srcy = y * const.tileWidth

			mag = gxEdit.magnification
			srcrect = (srcx, srcy, const.tileWidth, const.tileWidth)
			dstrect = (int(dstx*mag), int(dsty*mag), int(const.tileWidth//2*mag), int(const.tileWidth//2*mag))

			self.renderer.copy(units, srcrect=srcrect, dstrect=dstrect)

			if o.type1 in const.entityChildIds:
				self.renderer.copy(self.surfaces[SURF_COLOR_RED_TRANSPARENT], dstrect=dstrect)

			#entity borders
			self.drawBox(self.renderer, int(dstx*mag), int(dsty*mag), int(const.tileWidth//2*mag), int(const.tileWidth//2*mag))

			if (dstx, dsty) in xys: #distinguish layered entities
				 self.renderer.copy(self.surfaces[SURF_COLOR_ORANGE_TRANSPARENT], dstrect=dstrect)
			xys.append((dstx, dsty))
			
	def drawBox(self, renderer, dstx, dsty, w, h):
		#mag = gxEdit.magnification
		gDrawBoxRect.x = dstx
		gDrawBoxRect.y = dsty
		gDrawBoxRect.w = 1
		gDrawBoxRect.h = h
		sdl2.SDL_RenderCopy(renderer.sdlrenderer, self.surfaces[SURF_COLOR_GREEN].texture, None, gDrawBoxRect)
		gDrawBoxRect.x = dstx
		gDrawBoxRect.y = dsty
		gDrawBoxRect.w = w
		gDrawBoxRect.h = 1
		sdl2.SDL_RenderCopy(renderer.sdlrenderer, self.surfaces[SURF_COLOR_GREEN].texture, None, gDrawBoxRect)
		gDrawBoxRect.x = dstx+w
		gDrawBoxRect.y = dsty
		gDrawBoxRect.w = 1
		gDrawBoxRect.h = h
		sdl2.SDL_RenderCopy(renderer.sdlrenderer, self.surfaces[SURF_COLOR_GREEN].texture, None, gDrawBoxRect)
		gDrawBoxRect.x = dstx
		gDrawBoxRect.y = dsty+h
		gDrawBoxRect.w = w
		gDrawBoxRect.h = 1
		sdl2.SDL_RenderCopy(renderer.sdlrenderer, self.surfaces[SURF_COLOR_GREEN].texture, None, gDrawBoxRect)
		return
		renderer.copy(self.surfaces[SURF_COLOR_GREEN], dstrect=dstrect1)
		renderer.copy(self.surfaces[SURF_COLOR_GREEN], dstrect=dstrect2)
		renderer.copy(self.surfaces[SURF_COLOR_GREEN], dstrect=dstrect3)
		renderer.copy(self.surfaces[SURF_COLOR_GREEN], dstrect=dstrect4)

	def renderMainBg(self, introAnimTimer, mouseover):
		windowBg = self.surfaces[SURF_WINDOWBG]
		windowBg2 = self.surfaces[SURF_WINDOWBG2]
		if introAnimTimer > 15 and introAnimTimer < 25 and introAnimTimer % 3 == 0 or introAnimTimer > 25:
			if mouseover:
				self.renderer.copy(windowBg, dstrect=(windowBg.x, windowBg.y, windowBg.size[0], windowBg.size[1]))
			else:
				self.renderer.copy(windowBg2, dstrect=(windowBg.x, windowBg.y, windowBg.size[0], windowBg.size[1]))

	def renderFade(self):
		pass

	def renderUIWindows(self, gxEdit):
		#TODO
		windowsurf = self.surfaces[SURF_UIWINDOW]
		scale = 1
		for elem in gxEdit.elements:
			if not elem.visible: continue
			#middle
			self.renderer.copy(windowsurf, srcrect=rectUIWindow1ColorFill, dstrect=(elem.x+1, elem.y, elem.w-2, elem.h))
			self.renderer.copy(windowsurf, srcrect=rectUIWindow1ColorFill, dstrect=(elem.x, elem.y+1, elem.w, elem.h-2))
			
			#corners
			self.renderer.copy(windowsurf, srcrect=rectUIWindow2TopLeft, dstrect=(elem.x, elem.y, 2, 2))
			self.renderer.copy(windowsurf, srcrect=rectUIWindow2TopRight, dstrect=(elem.x+elem.w-2, elem.y, 2, 2))
			self.renderer.copy(windowsurf, srcrect=rectUIWindow2BottomLeft, dstrect=(elem.x, elem.y+elem.h-2, 2, 2))
			self.renderer.copy(windowsurf, srcrect=rectUIWindow2BottomRight, dstrect=(elem.x+elem.w-2, elem.y+elem.h-2, 2, 2))

			#border
			self.renderer.copy(windowsurf, srcrect=rectUIWindow2Top, dstrect=(elem.x+1, elem.y, elem.w-2, 1))
			self.renderer.copy(windowsurf, srcrect=rectUIWindow2Right, dstrect=(elem.x+elem.w-1, elem.y+1, 1, elem.h-2))
			self.renderer.copy(windowsurf, srcrect=rectUIWindow2Bottom, dstrect=(elem.x+1, elem.y+elem.h-1, elem.w-2, 1))
			self.renderer.copy(windowsurf, srcrect=rectUIWindow2Left, dstrect=(elem.x, elem.y+1, 1, elem.h-2))

			#render
		pass


	def fadeout(self, introAnimTimer):
		colorBlack = self.surfaces[SURF_COLOR_BLACK]
		windowSurface = self.window.get_surface()
		window = self.window

		self.renderer.copy(colorBlack, dstrect=(0, gWindowHeight//2 + math.ceil(gWindowHeight * 0.05 * introAnimTimer), windowSurface.w, windowSurface.h))
		self.renderer.copy(colorBlack, dstrect=(0, -gWindowHeight//2 - math.ceil(gWindowHeight * 0.05 * introAnimTimer), windowSurface.w, windowSurface.h))
		self.renderer.copy(colorBlack, dstrect=(gWindowWidth//2 + math.ceil(gWindowWidth * 0.05 * introAnimTimer), 0, windowSurface.w, windowSurface.h))
		self.renderer.copy(colorBlack, dstrect=(-gWindowWidth//2 - math.ceil(gWindowWidth * 0.05 * introAnimTimer), 0, windowSurface.w, windowSurface.h))
	
	def fill(self):
		colorBlack = self.surfaces[SURF_COLOR_BLACK]
		window = self.window

		self.renderer.copy(colorBlack, dstrect=(0, 0, gWindowWidth, gWindowHeight))

	'''
	def clampMagnification(self):
		if self.magnification <= 0:
			self.magnification = 1
	'''

