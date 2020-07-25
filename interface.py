# pylint: disable=no-member

import sdl2.ext
import const
import math
import ctypes

import util

from sdl2.sdlttf import *

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

SURF_SDLCOLOR_MAGENTA = 13
SURF_SDLCOLOR_GREEN = 14
SURF_SDLCOLOR_GOLD = 15
SURF_SDLCOLOR_RED = 16

gSurfaces = [None] * surfaceCount

#rect enums
rectUIWindow1TopLeft = (0, 0, 2, 2)
rectUIWindow1TopRight = (4, 0, 2, 2)
rectUIWindow1BottomLeft = (0, 3, 2, 2)
rectUIWindow1BottomRight = (4, 3, 2, 2)

rectUIWindow1Top = (2, 0, 1, 1)
rectUIWindow1Right = (5, 2, 1, 1)
rectUIWindow1Bottom = (0, 2, 1, 1)
rectUIWindow1Left = (0, 2, 1, 1)


rectUIWindow1ColorFill = (2, 2, 1, 1)

rectUIWindow2TopLeft = (6, 0, 2, 2)
rectUIWindow2TopRight = (10, 0, 2, 2)
rectUIWindow2BottomLeft = (6, 3, 2, 2)
rectUIWindow2BottomRight = (10, 3, 2, 2)

rectUIWindow2Top = (8, 0, 1, 1)
rectUIWindow2Right = (11, 2, 1, 1)
rectUIWindow2Bottom = (8, 4, 1, 1)
rectUIWindow2Left = (6, 2, 1, 1)


rectUITooltipColorFill = (14, 2, 1, 1)
rectUITooltipTopLeft = (12, 0, 2, 2)
rectUITooltipTopRight = (16, 0, 2, 2)
rectUITooltipBottomLeft = (12, 3, 2, 2)
rectUITooltipBottomRight = (16, 3, 2, 2)
rectUITooltipTop = (14, 0, 1, 1)
rectUITooltipRight = (17, 2, 1, 1)
rectUITooltipBottom = (14, 4, 1, 1)
rectUITooltipLeft = (12, 2, 1, 1)

rectsUITooltipBlack = (rectUITooltipColorFill, rectUITooltipTopLeft, rectUITooltipTopRight, rectUITooltipBottomLeft, rectUITooltipBottomRight,
rectUITooltipTop, rectUITooltipRight, rectUITooltipBottom, rectUITooltipLeft)

rectUITooltipYellowColorFill = (20, 2, 1, 1)
rectUITooltipYellowTopLeft = (18, 0, 2, 2)
rectUITooltipYellowTopRight = (22, 0, 2, 2)
rectUITooltipYellowBottomLeft = (18, 3, 2, 2)
rectUITooltipYellowBottomRight = (22, 3, 2, 2)
rectUITooltipYellowTop = (20, 0, 1, 1)
rectUITooltipYellowRight = (23, 2, 1, 1)
rectUITooltipYellowBottom = (20, 4, 1, 1)
rectUITooltipYellowLeft = (18, 2, 1, 1)

rectsUITooltipYellow = (rectUITooltipYellowColorFill, rectUITooltipYellowTopLeft, rectUITooltipYellowTopRight, rectUITooltipYellowBottomLeft, rectUITooltipYellowBottomRight,
rectUITooltipYellowTop, rectUITooltipYellowRight, rectUITooltipYellowBottom, rectUITooltipYellowLeft)

rectsUITooltip = (rectsUITooltipBlack, rectsUITooltipYellow)

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

gFont = None

def getTextSize(font, text):
	w = ctypes.c_int(0)
	h = ctypes.c_int(0)
	TTF_SizeText(font, text, w, h)
	return [w.value, h.value]

class UIElement:
	def __init__(self, x, y, w, h, parent, rect=(0,0,0,0), style=0, tooltip=None):
		self.x = x
		self.y = y
		self.w = w
		self.h = h

		self.rect = rect

		self.style = style

		self.tooltip = tooltip

		self.parent = parent


	def handleMouse1():
		return False

	def handleMouse2():
		return False

	def handleMouse1Up(self, mouse, gxEdit):
		return False

	def handleMouseOver(self, mouse, gxEdit):
		gxEdit.tooltipText = self.tooltip
		gxEdit.tooltipStyle = self.style
		return True


	def render(self, x, y):
		windowsurf = gSurfaces[SURF_UIWINDOW]
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

	def handleMouseOver(self, mouse, gxEdit):
		gxEdit.tooltipText = self.tooltip
		gxEdit.tooltipStyle = self.style
		return True

	def onAction(self, parent, elem):
		pass

	def render(self, x, y):
		UIElement.render(self, x, y)


class UIElementStretch(UIElement):
	def __init__(self, x, y, w, h, parent, rect, style=0, tooltip=None):
		UIElement.__init__(self, x, y, w, h, parent, rect, style, tooltip)

	def render(self, x, y):
		windowsurf = gSurfaces[SURF_UIWINDOW]
		gInterface.renderer.copy(windowsurf, srcrect=self.rect, 
			dstrect=(self.x + x, self.y + y, self.w, self.h))


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

	def handleMouseOver(self, mouse, gxEdit):
		for _, elem in self.elements.items():
			if util.inWindowElemBoundingBox(mouse, self, elem) and elem.handleMouseOver(mouse, gxEdit):
				return True
		gxEdit.tooltipText = []
		return False

	def handleMouse2():
		return False

	def render(self, gxEdit, stage):
		for _, elem in self.elements.items():
			elem.render(self.x, self.y)


#entity types: crash
#background entity
#Background/Beneficial
#Enemy

sdlColorMagenta = sdl2.SDL_Color(255,100,255)
sdlColorCyan = sdl2.SDL_Color(100,255,255)
sdlColorGreen = sdl2.SDL_Color(128,255,0)
sdlColorGold = sdl2.SDL_Color(255,220,100)
sdlColorYellow = sdl2.SDL_Color(255,230,150)
sdlColorOrange = sdl2.SDL_Color(255,150,100)
sdlColorRed = sdl2.SDL_Color(255,100,100)

sdlColorWhite = sdl2.SDL_Color(255,255,255)
sdlColorBlack = sdl2.SDL_Color(0,0,0)


def renderWindowBox(self, fill, topleft, topright, bottomleft, bottomright, top, right, bottom, left):
	windowsurf = gSurfaces[SURF_UIWINDOW]
	gInterface.renderer.copy(windowsurf, srcrect=fill, dstrect=(self.x+1, self.y, self.w-2, self.h))
	gInterface.renderer.copy(windowsurf, srcrect=fill, dstrect=(self.x, self.y+1, self.w, self.h-2))
		
	#corners
	gInterface.renderer.copy(windowsurf, srcrect=topleft, dstrect=(self.x, self.y, 2, 2))
	gInterface.renderer.copy(windowsurf, srcrect=topright, dstrect=(self.x+self.w-2, self.y, 2, 2))
	gInterface.renderer.copy(windowsurf, srcrect=bottomleft, dstrect=(self.x, self.y+self.h-2, 2, 2))
	gInterface.renderer.copy(windowsurf, srcrect=bottomright, dstrect=(self.x+self.w-2, self.y+self.h-2, 2, 2))

	#border
	gInterface.renderer.copy(windowsurf, srcrect=top, dstrect=(self.x+1, self.y, self.w-2, 1))
	gInterface.renderer.copy(windowsurf, srcrect=right, dstrect=(self.x+self.w-1, self.y+1, 1, self.h-2))
	gInterface.renderer.copy(windowsurf, srcrect=bottom, dstrect=(self.x+1, self.y+self.h-1, self.w-2, 1))
	gInterface.renderer.copy(windowsurf, srcrect=left, dstrect=(self.x, self.y+1, 1, self.h-2))


class UITooltip(UIWindow):
	def __init__(self, x, y, w, h, type=const.WINDOW_TOOLTIP, style=const.STYLE_TOOLTIP_BLACK):
		UIWindow.__init__(self, x, y, w, h, type, style)

	def handleMouse1(self, mouse, gxEdit):
		return False

	def handleMouse1Up(self, mouse, gxEdit):
		return False

	def handleMouse2(self, mouse, gxEdit):
		return False

	def render(self, gxEdit, stage):
		if not gxEdit.tooltipText:
			return

		mouse = sdl2.SDL_MouseButtonEvent()
		x,y = ctypes.c_int(0), ctypes.c_int(0)
		mouse.button = sdl2.SDL_GetMouseState(x, y)
		mouse.x, mouse.y = x.value, y.value

		textTexts = []
		textWidths = []
		textHeights = []

		sdlrenderer = gInterface.renderer.sdlrenderer

		for lines in gxEdit.tooltipText:
			TTF_SetFontStyle(gFont, lines[2])
			textSurf = TTF_RenderText_Blended_Wrapped(gFont, ctypes.c_char_p(lines[0].encode("utf-8")), lines[1], ctypes.c_uint(int(200)))

			textWidths.append(textSurf.contents.w)
			textHeights.append(textSurf.contents.h)

			textTexts.append(sdl2.SDL_CreateTextureFromSurface(sdlrenderer, textSurf))
			sdl2.SDL_FreeSurface(textSurf)

		self.w = (max(textWidths) + 12) * gxEdit.tooltipMag
		self.h = (sum(textHeights) + 12) * gxEdit.tooltipMag

		self.x = mouse.x
		self.y = mouse.y - self.h

		if self.x + self.w >= gWindowWidth:
			self.x = gWindowWidth - self.w

		if self.y <= 0:
			self.y = 0

		renderWindowBox(self, *rectsUITooltip[gxEdit.tooltipStyle])

		renderHeight = self.y+6
		for i in range(len(textTexts)):
			dstRect = sdl2.SDL_Rect(self.x+6, renderHeight, textWidths[i]*gxEdit.tooltipMag, textHeights[i]*gxEdit.tooltipMag)
			renderHeight += textHeights[i]*gxEdit.tooltipMag

			sdl2.SDL_RenderCopy(sdlrenderer, textTexts[i], None, dstRect)
			sdl2.SDL_DestroyTexture(textTexts[i])
		

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

			gInterface.drawBox(gInterface.renderer, SURF_COLOR_GREEN, dstx, dsty, w, h)

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
		units = gSurfaces[SURF_UNITS]
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
			gInterface.drawBox(gInterface.renderer, SURF_COLOR_GREEN, dstx, dsty, const.tileWidth * mag, const.tileWidth * mag)

		#crashing entities
		for i in range (const.entityFuncCount):
			if i in const.entityCrashIds:
				dstx = (i % 16) * const.tileWidth * mag + (self.x + self.elements["picker"].x)
				dsty = (i // 16) * const.tileWidth * mag + (self.y + self.elements["picker"].y) 
				gInterface.renderer.copy(gSurfaces[SURF_COLOR_RED_TRANSPARENT], dstrect=(dstx, dsty, const.tileWidth, const.tileWidth))

	def handleMouseOver(self, mouse, gxEdit):
		UIWindow.handleMouseOver(self, mouse, gxEdit)

		x = (mouse.x - self.x - self.elements["picker"].x) // const.tileWidth
		y = (mouse.y - self.y - self.elements["picker"].y) // const.tileWidth

		index = x + (y * 16)
		if index >= const.entityFuncCount:
			return False
		if index < 0:
			return False

		if index in const.entityCrashIds:
			titleColor = sdlColorRed
		elif index in const.entityGoodIds:
			titleColor = sdlColorGreen
		elif index in const.entityUtilIds:
			titleColor = sdlColorGold
		else:
			titleColor = sdlColorMagenta
		
		descColor = sdlColorWhite

		if index in const.entityGoodIds:
			paramColor = sdlColorYellow
		else:
			paramColor = sdlColorCyan

		if gxEdit.entityInfo[index][0] != "":
			gxEdit.tooltipText = ([[gxEdit.entityInfo[index][0], titleColor, TTF_STYLE_BOLD]])
		if gxEdit.entityInfo[index][1] != "":
			 gxEdit.tooltipText.append([gxEdit.entityInfo[index][1], descColor, TTF_STYLE_NORMAL])
		if gxEdit.entityInfo[index][2] != "":
			gxEdit.tooltipText.append([gxEdit.entityInfo[index][2], paramColor, TTF_STYLE_NORMAL])

		gxEdit.tooltipStyle = const.STYLE_TOOLTIP_BLACK
		
		return True



def toggleTilePalette():
	pass	

class ToolsWindow(UIWindow):
	def __init__(self, x, y, w, h, type=const.WINDOW_TOOLS, style=0):
		UIWindow.__init__(self, x, y, w, h, type, style)

		self.elements["textTools"] = UIElement(2, 2, 0, 0, self, rectWindowTextTools)

		self.elements["butToggleTilePalette"] = UIButton(4, 24, 16, 16, self, style=const.STYLE_TOOLTIP_YELLOW, 
												tooltip=[["i hate pxedit", sdlColorBlack, TTF_STYLE_NORMAL]])
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

	def loadSurfaces(self):
		RESOURCES = sdl2.ext.Resources(__file__, "BITMAP")

		gSurfaces[SURF_WINDOWBG] = self.sprfactory.from_image(RESOURCES.get_path("dgBg.bmp"))
		gSurfaces[SURF_WINDOWBG2] = self.sprfactory.from_image(RESOURCES.get_path("dgBg2.bmp"))
		gSurfaces[SURF_COLOR_BLACK] = self.sprfactory.from_color(sdl2.ext.Color(0,0,0),(32,32))
		gSurfaces[SURF_COLOR_ORANGE] = sdl2.ext.Color(0,255,0)
		gSurfaces[SURF_COLOR_ORANGE_DARK] = sdl2.ext.Color(0,255,0)
		gSurfaces[SURF_COLOR_GREEN] = self.sprfactory.from_color(sdl2.ext.Color(0,255,0),(32,32))

		gSurfaces[SURF_COLOR_BLUE] = self.sprfactory.from_color(sdl2.ext.Color(84,108,128),(32,32))

		gSurfaces[SURF_SDLCOLOR_MAGENTA] = self.sprfactory.from_color(sdlColorMagenta,(32,32))
		gSurfaces[SURF_SDLCOLOR_GOLD] = self.sprfactory.from_color(sdlColorGold,(32,32))
		gSurfaces[SURF_SDLCOLOR_GREEN] = self.sprfactory.from_color(sdlColorGreen,(32,32))
		gSurfaces[SURF_SDLCOLOR_RED] = self.sprfactory.from_color(sdlColorRed,(32,32))



		gSurfaces[SURF_COLOR_RED_TRANSPARENT] = self.sprfactory.from_color(sdl2.ext.Color(255,0,0, 80), size=(32, 32),
                   masks=(0xFF000000,           
                          0x00FF0000,           
                          0x0000FF00,           
                          0x000000FF))   

		gSurfaces[SURF_COLOR_ORANGE_TRANSPARENT] = self.sprfactory.from_color(sdl2.ext.Color(250,150,0, 128), size=(32, 32),
                   masks=(0xFF000000,           
                          0x00FF0000,           
                          0x0000FF00,           
                          0x000000FF))   

		gSurfaces[SURF_COLOR_WHITE_TRANSPARENT] = self.sprfactory.from_color(sdl2.ext.Color(255,255,255, 128), size=(32, 32),
           masks=(0xFF000000,           
                  0x00FF0000,           
                  0x0000FF00,           
                  0x000000FF))   

		gSurfaces[SURF_UNITS] = self.sprfactory.from_image(unitsName)


		gSurfaces[SURF_UIWINDOW] = self.sprfactory.from_image(RESOURCES.get_path("Window.bmp"))
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

		#TODO: fix this
		mouse = sdl2.SDL_MouseButtonEvent()
		x,y = ctypes.c_int(0), ctypes.c_int(0)
		mouse.button = sdl2.SDL_GetMouseState(x, y)
		mouse.x, mouse.y = x.value, y.value

		if gxEdit.currentEditMode == const.EDIT_TILE:
			x = int(mouse.x // (const.tileWidth * mag))
			y = int(mouse.y // (const.tileWidth * mag))

			if x >= map.width or y >= map.height: return

			x *= int(const.tileWidth * mag)
			y *= int(const.tileWidth * mag)

			w = stage.selectedTilesEnd[0] - stage.selectedTilesStart[0] + 1
			h = stage.selectedTilesEnd[1] - stage.selectedTilesStart[1] + 1

			w *= int(const.tileWidth * mag)
			h *= int(const.tileWidth * mag)

		elif gxEdit.currentEditMode == const.EDIT_ENTITY:
			x = int(mouse.x // (const.tileWidth//2 * mag)) 
			y = int(mouse.y // (const.tileWidth//2 * mag))

			if x >= map.width*2 or y >= map.height*2: return

			gxEdit.tooltipText = []
			for o in stage.eve.get():
				#TODO: multiple entities
				#TODO: highlight hovered in picker
				if o.x == x + stage.hscroll*2 and o.y == y + stage.scroll*2:
					index = o.type1
					if index in const.entityCrashIds:
						titleColor = sdlColorRed
					elif index in const.entityGoodIds:
						titleColor = sdlColorGreen
					elif index in const.entityUtilIds:
						titleColor = sdlColorGold
					else:
						titleColor = sdlColorMagenta

					gxEdit.tooltipText.append([gxEdit.entityInfo[index][0], titleColor, TTF_STYLE_BOLD])
					gxEdit.tooltipStyle = const.STYLE_TOOLTIP_BLACK

					gxEdit.tooltipText.append(["Param: " + str(o.type2), sdlColorWhite, TTF_STYLE_NORMAL])

			x *= int(const.tileWidth//2 * mag)
			y *= int(const.tileWidth//2 * mag)

			w = int(const.tileWidth//2 * mag)
			h = int(const.tileWidth//2 * mag)

		self.renderer.copy(gSurfaces[SURF_COLOR_WHITE_TRANSPARENT], dstrect=(x, y, w, h))




	def renderTilePalette(self, gxEdit, stage):
		#TODO: placeholder
		pass




	def renderEntities(self, gxEdit, stage):
		#TODO: render to surface
		eve = stage.eve.get()
		units = gSurfaces[SURF_UNITS]
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

			if o.type1 in const.entityCrashIds:
				self.renderer.copy(gSurfaces[SURF_COLOR_RED_TRANSPARENT], dstrect=dstrect)

			if o.type1 in const.entityCrashIds:
				titleColor = SURF_SDLCOLOR_MAGENTA
			elif o.type1 in const.entityGoodIds:
				titleColor = SURF_SDLCOLOR_GREEN
			elif o.type1 in const.entityUtilIds:
				titleColor = SURF_SDLCOLOR_GOLD
			else:
				titleColor = SURF_SDLCOLOR_RED
			#entity borders
			self.drawBox(self.renderer, titleColor, int(dstx*mag), int(dsty*mag), int(const.tileWidth//2*mag), int(const.tileWidth//2*mag))

			if (dstx, dsty) in xys: #distinguish layered entities
				 self.renderer.copy(gSurfaces[SURF_COLOR_ORANGE_TRANSPARENT], dstrect=dstrect)
			xys.append((dstx, dsty))
			
	def drawBox(self, renderer, surf, dstx, dsty, w, h):
		#mag = gxEdit.magnification
		gDrawBoxRect.x = dstx
		gDrawBoxRect.y = dsty
		gDrawBoxRect.w = 1
		gDrawBoxRect.h = h
		sdl2.SDL_RenderCopy(renderer.sdlrenderer, gSurfaces[surf].texture, None, gDrawBoxRect)
		gDrawBoxRect.x = dstx
		gDrawBoxRect.y = dsty
		gDrawBoxRect.w = w
		gDrawBoxRect.h = 1
		sdl2.SDL_RenderCopy(renderer.sdlrenderer, gSurfaces[surf].texture, None, gDrawBoxRect)
		gDrawBoxRect.x = dstx+w
		gDrawBoxRect.y = dsty
		gDrawBoxRect.w = 1
		gDrawBoxRect.h = h
		sdl2.SDL_RenderCopy(renderer.sdlrenderer, gSurfaces[surf].texture, None, gDrawBoxRect)
		gDrawBoxRect.x = dstx
		gDrawBoxRect.y = dsty+h
		gDrawBoxRect.w = w
		gDrawBoxRect.h = 1
		sdl2.SDL_RenderCopy(renderer.sdlrenderer, gSurfaces[surf].texture, None, gDrawBoxRect)
		return
		renderer.copy(gSurfaces[SURF_COLOR_GREEN], dstrect=dstrect1)
		renderer.copy(gSurfaces[SURF_COLOR_GREEN], dstrect=dstrect2)
		renderer.copy(gSurfaces[SURF_COLOR_GREEN], dstrect=dstrect3)
		renderer.copy(gSurfaces[SURF_COLOR_GREEN], dstrect=dstrect4)

	def renderMainBg(self, introAnimTimer, mouseover):
		windowBg = gSurfaces[SURF_WINDOWBG]
		windowBg2 = gSurfaces[SURF_WINDOWBG2]
		if introAnimTimer > 15 and introAnimTimer < 25 and introAnimTimer % 3 == 0 or introAnimTimer > 25:
			if mouseover:
				self.renderer.copy(windowBg, dstrect=(windowBg.x, windowBg.y, windowBg.size[0], windowBg.size[1]))
			else:
				self.renderer.copy(windowBg2, dstrect=(windowBg.x, windowBg.y, windowBg.size[0], windowBg.size[1]))

	def renderFade(self):
		pass

	def renderUIWindows(self, gxEdit):
		#TODO
		windowsurf = gSurfaces[SURF_UIWINDOW]
		scale = 1
		for elem in gxEdit.elements:
			if not elem.visible: continue
			#TODO PLACEHOLDER AGAGHAGH
			if elem.type == const.WINDOW_TOOLTIP: continue
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
		colorBlack = gSurfaces[SURF_COLOR_BLACK]
		windowSurface = self.window.get_surface()
		window = self.window

		self.renderer.copy(colorBlack, dstrect=(0, gWindowHeight//2 + math.ceil(gWindowHeight * 0.05 * introAnimTimer), windowSurface.w, windowSurface.h))
		self.renderer.copy(colorBlack, dstrect=(0, -gWindowHeight//2 - math.ceil(gWindowHeight * 0.05 * introAnimTimer), windowSurface.w, windowSurface.h))
		self.renderer.copy(colorBlack, dstrect=(gWindowWidth//2 + math.ceil(gWindowWidth * 0.05 * introAnimTimer), 0, windowSurface.w, windowSurface.h))
		self.renderer.copy(colorBlack, dstrect=(-gWindowWidth//2 - math.ceil(gWindowWidth * 0.05 * introAnimTimer), 0, windowSurface.w, windowSurface.h))
	
	def fill(self):
		colorBlack = gSurfaces[SURF_COLOR_BLACK]
		window = self.window

		self.renderer.copy(colorBlack, dstrect=(0, 0, gWindowWidth, gWindowHeight))

	'''
	def clampMagnification(self):
		if self.magnification <= 0:
			self.magnification = 1
	'''

