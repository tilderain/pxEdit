# pylint: disable=no-member
import os
os.environ["PYSDL2_DLL_PATH"] = "./"
import sdl2.ext
import const
import math
import ctypes

import util

import multi

import copy


from sdl2.sdlttf import *

#from gxEdit import gxEdit as gxEdit

unitsName = "assist/unittype.png"

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

SURF_NUMBER = 17

SURF_EDITORBG = 18

SURF_SDLCOLOR_CYAN = 19
SURF_ATTRIBUTE = 20

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

rectsUIWindow2 = (rectUIWindow1ColorFill, rectUIWindow2TopLeft, rectUIWindow2TopRight, rectUIWindow2BottomLeft, rectUIWindow2BottomRight, 
rectUIWindow2Top, rectUIWindow2Right, rectUIWindow2Bottom, rectUIWindow2Left)


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

rectUIConcaveColorFill = (26, 2, 1, 1)
rectUIConcaveTopLeft = (24, 0, 2, 2)
rectUIConcaveTopRight = (28, 0, 2, 2)
rectUIConcaveBottomLeft = (24, 3, 2, 2)
rectUIConcaveBottomRight = (28, 3, 2, 2)
rectUIConcaveTop = (26, 0, 1, 1)
rectUIConcaveRight = (29, 2, 1, 1)
rectUIConcaveBottom = (26, 4, 1, 1)
rectUIConcaveLeft = (24, 2, 1, 1)

rectsUIConcave = (rectUIConcaveColorFill, rectUIConcaveTopLeft, rectUIConcaveTopRight, rectUIConcaveBottomLeft, rectUIConcaveBottomRight,
rectUIConcaveTop, rectUIConcaveRight, rectUIConcaveBottom, rectUIConcaveLeft)

rectWindowTextPalette = (80, 48, 68, 12)
rectWindowTextTools = (80, 64, 54, 12)
rectWindowTextLayer = (80, 80, 64, 16)

rectWindowTextLVMP = (192, 32, 16, 16)

rectButtonMinimizeNormal = (80, 16, 16, 16)
rectButtonMinimizeClicked = (96, 16, 16, 16)

rectsButtonMinimize = [rectButtonMinimizeNormal, None, rectButtonMinimizeClicked, None, None]

rectButtonCheckbox = (80, 0, 16, 12)
rectButtonCheckboxChecked = (96, 0, 16, 12)
rectButtonCheckboxHalfChecked = (112, 0, 16, 12)

rectsButtonCheckbox = rectButtonCheckbox, None, rectButtonCheckboxHalfChecked, rectButtonCheckboxChecked, None


#y+=16
BUTTON_NORMAL = 0
BUTTON_DRAW = 1
BUTTON_ERASE = 2
BUTTON_COPY = 3
BUTTON_SCRIPT = 4
BUTTON_EXIT = 5
BUTTON_CURRENTLAYER = 6
BUTTON_SAVE = 7
BUTTON_UNITS = 8
BUTTON_TILETYPE = 9
BUTTON_EDITATTRIBUTE = 10
BUTTON_EDITIMAGE = 11
BUTTON_RELOAD = 12
BUTTON_FILL = 13
BUTTON_REPLACE = 14
BUTTON_MAP0 = 15
BUTTON_MAP1 = 16
BUTTON_MAP2 = 17
BUTTON_MULTIPLAYER = 18

rectButtonNormal = [0, 16, 16, 16]
rectButtonNormalDisabled = [16, 16, 16, 16]
rectButtonNormalClicked = [32, 16, 16, 16]
rectButtonNormalActive = [48, 16, 16, 16]
rectButtonNormalHovered = [64, 16, 16, 16]


rectButtonRectangle = [80, 224, 16, 16]
rectButtonRectangleActive = [128, 224, 16, 16]
rectsButtonRectangle = [rectButtonRectangle, None, None, rectButtonRectangleActive, None]


rectsButtonNormal = [rectButtonNormal, rectButtonNormalDisabled, rectButtonNormalClicked, rectButtonNormalActive, rectButtonNormalHovered]

rectMultiplayerCursor = (128, 0, 16, 16)
rectMultiplayerArrowLeft = (128, 16, 16, 16)
rectMultiplayerArrowUp = (144, 16, 16, 16)
rectMultiplayerArrowRight = (160, 16, 16, 16)
rectMultiplayerArrowDown = (176, 16, 16, 16)

rectsMultiplayerArrow = rectMultiplayerArrowLeft, rectMultiplayerArrowUp, rectMultiplayerArrowRight, rectMultiplayerArrowDown

gRenderer = None
gWindow = None
gSprfactory = None
gInterface = None

gWindowWidth = 0
gWindowHeight = 0

gDrawBoxRect = sdl2.SDL_Rect(0,0,0,0)

gFont = None

def getTextSize(text, font):
	w = ctypes.c_int(0)
	h = ctypes.c_int(0)
	TTF_SizeText(font, ctypes.c_char_p(text.encode("utf-8")), w, h)
	return [w.value, h.value]

#lazy function
def renderText(text, color, style, x, y):
	if text == "" or text == None: return

	sdlrenderer = gInterface.renderer.sdlrenderer

	TTF_SetFontStyle(gFont, style)
	textSurf = TTF_RenderText_Blended(gFont, ctypes.c_char_p(text.encode("utf-8")), color)

	textWidth = textSurf.contents.w
	textHeight = textSurf.contents.h

	textText = (sdl2.SDL_CreateTextureFromSurface(sdlrenderer, textSurf))
	sdl2.SDL_FreeSurface(textSurf)

	dstRect = sdl2.SDL_Rect(int(x), int(y), textWidth, textHeight)

	sdl2.SDL_RenderCopy(sdlrenderer, textText, None, dstRect)
	sdl2.SDL_DestroyTexture(textText)

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

		#TODO: self.draggable


	def handleMouse1(self, mouse, gxEdit):
		return False

	def handleMouse2():
		return False

	def handleMouse1Up(self, mouse, gxEdit):
		return False

	def handleMouseOver(self, mouse, gxEdit):
		gxEdit.tooltipText = self.tooltip
		gxEdit.tooltipStyle = self.style
		return True

	def handleTextInput(self, text):
		return False

	def render(self, x, y):
		windowsurf = gSurfaces[SURF_UIWINDOW]
		gInterface.renderer.copy(windowsurf, srcrect=self.rect, 
			dstrect=(self.x + x, self.y + y, self.rect[2], self.rect[3]))



class UIText(UIElement):
	def __init__(self, x, y, text, color, fontStyle, parent, rect=(0,0,0,0), style=0, tooltip=None, type=None):
		UIElement.__init__(self, x, y, 1, 1, parent, rect, style, tooltip)

		self.text = text
		self.color = color
		self.fontStyle = fontStyle
	
	def render(self, x, y):
		renderText(self.text, self.color, self.fontStyle, self.x + x, self.y + y)
		
class UITextInput(UIElement):
	def __init__(self, x, y, w, h, text, color, fontStyle, parent, rect=(0,0,0,0), style=const.TEXTINPUTTYPE_NORMAL, 
		tooltip=None, maxlen=0, paramtype=None):
		UIElement.__init__(self, x, y, w, h, parent, rect, style, tooltip)

		self.text = text
		self.placeholderText = None
		self.color = color
		self.fontStyle = fontStyle

		self.focussed = False
		self.blinkTimer = 0

		self.onAction = None

		self.maxlen = maxlen

		self.paramtype = paramtype

	def handleMouse1(self, mouse, gxEdit):
		#TODO: fix this
		if gxEdit.focussedElem:
			gxEdit.focussedElem.focussed = False
		gxEdit.focussedElem = self
		self.focussed = True
		return True
	
	def handleTextInput(self, text, gxEdit):
		if self.style == const.TEXTINPUTTYPE_NUMBER:
			if not text.isdigit() and not (self.text == "" and text == "-"):
				return False
			try:
				if self.maxlen and int(self.text + text) > self.maxlen or \
					self.maxlen and -int(self.text + text) > self.maxlen:
					return False
			except:
				pass
		elif self.maxlen and len(self.text + text) > self.maxlen:
			return False
		
		self.text += text
		if self.onAction: 
			self.onAction(self, gxEdit)
		return True

	def render(self, x, y):
		renderWindowBox(self, *rectsUIConcave, self.parent.x, self.parent.y)

		text = self.text
		color = self.color
		style = self.fontStyle
		if self.focussed:
			self.blinkTimer += 1
			if self.blinkTimer % 100 < 50:
				text += "_"
		else:
			self.blinkTimer = 0

		if text == "" and not self.focussed:
			text = self.placeholderText
			color = sdlColorOlive
			style = TTF_STYLE_ITALIC

		renderText(text, color, style, self.x + x + 5, self.y + y + (self.h // 8))


class UIScrollbar(UIElement):
	def __init__(self, x, y, w, h, parent, control, rect=(0,0,0,0), style=0, tooltip=None):
		UIElement.__init__(self, x, y, w, h, parent, rect, style, tooltip)

		self.control = control
	pass

BUTTON_STATE_NORMAL = 0
BUTTON_STATE_DISABLED = 1
BUTTON_STATE_CLICKED = 2
BUTTON_STATE_ACTIVE = 3
BUTTON_STATE_HOVERED = 4

BUTTON_TYPE_NORMAL = 0
BUTTON_TYPE_CHECKBOX = 1
BUTTON_TYPE_RADIO = 2


class UIButton:
	def __init__(self, x, y, w, h, parent, group=0, rects=rectsButtonNormal, style=0, tooltip=None, type=BUTTON_TYPE_NORMAL,
				 enum=BUTTON_NORMAL,
				 var=None, state=BUTTON_STATE_NORMAL,
				 text=None, fontStyle=None, fontColor=None):
		
		UIElement.__init__(self, x, y, w, h, parent, None, style, tooltip)

		self.rects = copy.deepcopy(rects)

		self.state = state

		self.type = type
		
		self.group = group

		self.text=text
		self.fontStyle=fontStyle
		self.fontColor=fontColor

		self.enum = enum

		self.var = var

		if self.enum:
			for i in range(len(self.rects)):
				self.rects[i][1] = 16 + (self.enum * 16)

	def handleMouse1(self, mouse, gxEdit):
		if self.type == BUTTON_TYPE_RADIO or self.type == BUTTON_TYPE_CHECKBOX:
			if self.type == BUTTON_TYPE_RADIO:
				self.state = BUTTON_STATE_ACTIVE
				for _, elem in self.parent.elements.items(): #uncheck other radios
					try:
						if elem != self and elem.group == self.group:
							elem.state = BUTTON_STATE_NORMAL
					except:
						pass
			else: #checkbox
				if self.state == BUTTON_STATE_ACTIVE: #toggle check
					self.state = BUTTON_STATE_NORMAL
				else:
					self.state = BUTTON_STATE_ACTIVE
			self.onAction(self.parent, self, gxEdit)		
		else: #normal button
			self.state = BUTTON_STATE_CLICKED
		return True

	def handleMouse2(self):
		return False

	def handleMouse1Up(self, mouse, gxEdit):
		if self.type == BUTTON_TYPE_RADIO or self.type == BUTTON_TYPE_CHECKBOX:
			return True
		self.state = BUTTON_STATE_NORMAL

		if util.inWindowElemBoundingBox(mouse, self.parent, self):
			self.onAction(self.parent, self, gxEdit)				
		return True

	def handleMouseOver(self, mouse, gxEdit):
		gxEdit.tooltipText = self.tooltip
		gxEdit.tooltipStyle = self.style
		return True

	def onAction(self, parent, elem, gxEdit):
		pass

	def render(self, x, y):
		self.rect = self.rects[self.state]
		UIElement.render(self, x, y)

		if self.text:
			xx = self.x + x
			yy = self.y + y
			renderText(self.text, self.color, self.fontStyle, xx, yy)



class UIElementStretch(UIElement):
	def __init__(self, x, y, w, h, parent, rect, style=0, tooltip=None):
		UIElement.__init__(self, x, y, w, h, parent, rect, style, tooltip)

	def render(self, x, y):
		windowsurf = gSurfaces[SURF_UIWINDOW]
		gInterface.renderer.copy(windowsurf, srcrect=self.rect, 
			dstrect=(self.x + x, self.y + y, self.w, self.h))


def minimizeButtonAction(window, elem, gxEdit):
	window.visible = False

class UIWindow:
	def __init__(self, x, y, w, h, type=const.WINDOW_NONE, style=0, visible=False):
		self.x = x
		self.y = y
		self.w = w
		self.h = h

		self.type = type
		self.style = style

		self.elements = {}

		self.draghitbox = [0, 0, self.w, 24]

		self.surface = gSprfactory.from_color(sdl2.ext.Color(0,0,0),(w,h))

		self.visible = visible

		self.priority = 0

	def handleMouse1(self, mouse, gxEdit):
		for _, elem in self.elements.items():
			if util.inWindowElemBoundingBox(mouse, self, elem) and elem.handleMouse1(mouse, gxEdit):
				gxEdit.activeElem = elem
				return True
		if gxEdit.focussedElem:
			gxEdit.focussedElem.focussed = False
		gxEdit.focussedElem = None
		return False

	def handleMouse1Up(self, mouse, gxEdit):
		for _, elem in self.elements.items():
			if(util.inWindowElemBoundingBox(mouse, self, elem) and elem.handleMouse1Up(mouse, gxEdit)):
				gxEdit.activeElem = None
				return True
		return False

	def handleMouseOver(self, mouse, gxEdit):
		for _, elem in self.elements.items():
			if util.inWindowElemBoundingBox(mouse, self, elem) and elem.handleMouseOver(mouse, gxEdit):
				return True
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
sdlColorOlive = sdl2.SDL_Color(128,180,0)
sdlColorGold = sdl2.SDL_Color(255,220,100)
sdlColorYellow = sdl2.SDL_Color(255,230,150)
sdlColorOrange = sdl2.SDL_Color(255,150,100)
sdlColorRed = sdl2.SDL_Color(255,100,100)

sdlColorWhite = sdl2.SDL_Color(255,255,255)
sdlColorBlack = sdl2.SDL_Color(0,0,0)


def renderWindowBox(self, fill, topleft, topright, bottomleft, bottomright, top, right, bottom, left, xoff=0, yoff=0):
	windowsurf = gSurfaces[SURF_UIWINDOW]
	gInterface.renderer.copy(windowsurf, srcrect=fill, dstrect=(self.x+xoff+1, self.y+yoff, self.w-2, self.h))
	gInterface.renderer.copy(windowsurf, srcrect=fill, dstrect=(self.x+xoff, self.y+yoff+1, self.w, self.h-2))
		
	#corners
	gInterface.renderer.copy(windowsurf, srcrect=topleft, dstrect=(self.x+xoff, self.y+yoff, 2, 2))
	gInterface.renderer.copy(windowsurf, srcrect=topright, dstrect=(self.x+xoff+self.w-2, self.y+yoff, 2, 2))
	gInterface.renderer.copy(windowsurf, srcrect=bottomleft, dstrect=(self.x+xoff, self.y+yoff+self.h-2, 2, 2))
	gInterface.renderer.copy(windowsurf, srcrect=bottomright, dstrect=(self.x+xoff+self.w-2, self.y+yoff+self.h-2, 2, 2))

	#border
	gInterface.renderer.copy(windowsurf, srcrect=top, dstrect=(self.x+xoff+1, self.y+yoff, self.w-2, 1))
	gInterface.renderer.copy(windowsurf, srcrect=right, dstrect=(self.x+xoff+self.w-1, self.y+yoff+1, 1, self.h-2))
	gInterface.renderer.copy(windowsurf, srcrect=bottom, dstrect=(self.x+xoff+1, self.y+yoff+self.h-1, self.w-2, 1))
	gInterface.renderer.copy(windowsurf, srcrect=left, dstrect=(self.x+xoff, self.y+yoff+1, 1, self.h-2))


class UITooltip(UIWindow):
	def __init__(self, x, y, w, h, type=const.WINDOW_TOOLTIP, style=const.STYLE_TOOLTIP_BLACK, visible=True):
		UIWindow.__init__(self, x, y, w, h, type, style, visible)
		self.draghitbox = [0, 0, 0, 0]

	def handleMouse1(self, mouse, gxEdit):
		return False

	def handleMouse1Up(self, mouse, gxEdit):
		return False

	def handleMouse2(self, mouse, gxEdit):
		return False

	def render(self, gxEdit, stage):
		if not gxEdit.tooltipText:
			return

		mouse = util.getMouseState()

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

		self.x = mouse.x + 4
		self.y = mouse.y - self.h - 16

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
	def __init__(self, x, y, w, h, type=const.WINDOW_TILEPALETTE, style=0, visible=True):
		UIWindow.__init__(self, x, y, w, h, type, style, visible)

		self.elements["picker"] = UIElement(0, 40, 0, 0, self, (0,0,0,0))
		self.elements["textPalette"] = UIElement(6, 6, 1, 1, self, rectWindowTextPalette)

		#textMouseX
		#textMouseY
		#textMapWidth
		#textMapHeight

		self.elements["editLayer"] = UIButton(128, 24, 16, 16, self, enum=BUTTON_SCRIPT, style=const.STYLE_TOOLTIP_YELLOW,
				tooltip=[["Edit layer", sdlColorBlack, TTF_STYLE_NORMAL]])

		self.elements["editLayer"].onAction = toggleResizeDialog

		self.elements["buttonMinimize"] = UIButton(0, 4, 16, 16, self, rects=rectsButtonMinimize)
		self.elements["buttonMinimize"].onAction = minimizeButtonAction

	def render(self, gxEdit, stage):
		UIWindow.render(self, gxEdit, stage)

		mag = gxEdit.tilePaletteMag

		if not stage.attrs[gxEdit.currentLayer].width: return
		if not stage.parts[gxEdit.currentLayer]: return
		#reset width
		self.w = (stage.attrs[gxEdit.currentLayer].width * const.tileWidth) * mag
		self.h = (stage.attrs[gxEdit.currentLayer].height * const.tileWidth) * mag + 24 + 2 + 16

		self.draghitbox = [0, 0, self.w, 24]

		self.elements["buttonMinimize"].x = self.w - 24
		##

		srcrect = (0,0, stage.attrs[gxEdit.currentLayer].width * const.tileWidth, 
			stage.attrs[gxEdit.currentLayer].height * const.tileWidth)
		
		dstx = self.x + self.elements["picker"].x
		dsty = self.y + self.elements["picker"].y



		#TODO: add dstrect mag
		dstrect = (dstx, dsty, stage.attrs[gxEdit.currentLayer].width * const.tileWidth * mag, 
							   stage.attrs[gxEdit.currentLayer].height * const.tileWidth * mag)
		gInterface.renderer.copy(stage.parts[gxEdit.currentLayer], srcrect=srcrect, dstrect=dstrect)

		if gxEdit.visibleLayers[4]:
			attr = stage.attrs[gxEdit.currentLayer]
			mag = gxEdit.tilePaletteMag
			for y in range(attr.height):
				for x in range(attr.width):
					dstxx = dstx + (x * const.tileWidth * mag)
					dstyy = dsty + (y * const.tileWidth * mag)

					tile = attr.tiles[y][x]

					xxx = tile % 16 
					yyy = tile // 16
					srcx = xxx * 16
					srcy = yyy * 16

					srcrect = (srcx, srcy, 16, 16)
					dstrect = (dstxx, dstyy, const.tileWidth*mag, const.tileWidth*mag)

					gRenderer.copy(gSurfaces[SURF_ATTRIBUTE], srcrect=srcrect, dstrect=dstrect)
				

		#TODO: add selected tile border (properly)
		if gxEdit.currentEditMode == const.EDIT_TILE:
			start = stage.selectedTilesStart[:]
			end = stage.selectedTilesEnd[:]

			if start[0] > end[0]:
				start[0], end[0] = end[0], start[0]
			if end[1] < start[1]:
				start[1], end[1] = end[1], start[1]

			dstx = dstx + ((start[0] * const.tileWidth) * mag)
			dsty = dsty + ((start[1] * const.tileWidth) * mag)
			w = (end[0]+1 - start[0]) * const.tileWidth * mag
			h =  (end[1]+1 - start[1]) * const.tileWidth * mag

			gInterface.drawBox(gInterface.renderer, SURF_COLOR_GREEN, dstx, dsty, w, h, 2)

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
		gxEdit.tileSelectionUpdate = True

	def handleMouseDrag(self, gxEdit):
		return False
		
def getEntityColors(index):
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
	
	return titleColor, descColor, paramColor

class EntityPaletteWindow(UIWindow):
	def __init__(self, x, y, w, h, type=const.WINDOW_TILEPALETTE, style=0, visible=True):
		UIWindow.__init__(self, x, y, w, h, type, style, visible)

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
			dstx = dstx + ((gxEdit.currentEntity % 16) * const.tileWidth2 * mag)
			dsty = dsty + ((gxEdit.currentEntity // 16) * const.tileWidth2 * mag)
			gInterface.drawBox(gInterface.renderer, SURF_COLOR_GREEN, dstx, dsty, const.tileWidth2 * mag, const.tileWidth2 * mag)

		#crashing entities
		for i in range (const.entityFuncCount):
			if i in const.entityCrashIds:
				dstx = (i % 16) * const.tileWidth * mag + (self.x + self.elements["picker"].x)
				dsty = (i // 16) * const.tileWidth * mag + (self.y + self.elements["picker"].y) 
				gInterface.renderer.copy(gSurfaces[SURF_COLOR_RED_TRANSPARENT], dstrect=(dstx, dsty, const.tileWidth, const.tileWidth))

	def handleMouseOver(self, mouse, gxEdit):
		UIWindow.handleMouseOver(self, mouse, gxEdit)

		x = (mouse.x - self.x - self.elements["picker"].x) // const.tileWidth2
		y = (mouse.y - self.y - self.elements["picker"].y) // const.tileWidth2

		index = x + (y * 16)
		if index >= const.entityFuncCount:
			return False
		if index < 0:
			return False

		titleColor, descColor, paramColor = getEntityColors(index)
		
		if gxEdit.entityInfo[index][0] != "":
			gxEdit.tooltipText = ([[gxEdit.entityInfo[index][0], titleColor, TTF_STYLE_BOLD]])
		if gxEdit.entityInfo[index][1] != "":
			 gxEdit.tooltipText.append([gxEdit.entityInfo[index][1], descColor, TTF_STYLE_NORMAL])
		if gxEdit.entityInfo[index][2] != "":
			gxEdit.tooltipText.append([gxEdit.entityInfo[index][2], paramColor, TTF_STYLE_NORMAL])

		gxEdit.tooltipStyle = const.STYLE_TOOLTIP_BLACK
		
		return True


#todo: put this globally in uiwindow
def toggleTilePalette(window, elem, gxEdit):
	gxEdit.elements["tilePalette"].visible ^= 1	
def toggleEntityPalette(window, elem, gxEdit):
	gxEdit.elements["entityPalette"].visible ^= 1	

def editPxPackAttributes(window, elem, gxEdit):
	
	curStage = window.curStage
	curStage.pack.description = window.elements["descEdit"].text
	curStage.pack.spritesheet = window.elements["sprEdit"].text

	curStage.pack.left_field = window.elements["leftEdit"].text
	curStage.pack.right_field = window.elements["rightEdit"].text 
	curStage.pack.up_field = window.elements["upEdit"].text 
	curStage.pack.down_field = window.elements["downEdit"].text

	paramX = window.elements["areaXEdit"].text
	paramY = window.elements["areaYEdit"].text

	paramAreaNo = window.elements["areaNoEdit"].text
	paramR = window.elements["rEdit"].text
	paramG = window.elements["gEdit"].text
	paramB = window.elements["bEdit"].text
	try:
		int(paramX)
	except:
		paramX = 0
	try:
		int(paramY)
	except:
		paramY = 0
	try:
		int(paramAreaNo)
	except:
		paramAreaNo = 0
	try:
		int(paramR)
	except:
		paramR = 0
	try:
		int(paramG)
	except:
		paramG = 0
	try:
		int(paramB)
	except:
		paramB = 0
	curStage.pack.area_x = int(paramX)
	curStage.pack.area_y = int(paramY)
	curStage.pack.area_no = int(paramAreaNo)
	curStage.pack.bg_r = int(paramR)
	curStage.pack.bg_g = int(paramG)
	curStage.pack.bg_b = int(paramB)

	for i in range(3):
		paramST = window.elements[f"map{i}STEdit"].text
		paramV = window.elements[f"map{i}VEdit"].text
		try:
			int(paramST)
		except:
			paramST = 0
		try:
			int(paramV)
		except:
			paramV = 0
		curStage.pack.layers[i].scrolltype = int(paramST)
		curStage.pack.layers[i].visibility = int(paramV)

		paramParts = window.elements[f"map{i}PartsEdit"].text
		oldParts = curStage.pack.layers[i].partsName

		if paramParts == oldParts: continue

		#TODO fix path var
		curStage.pack.layers[i].partsName = paramParts
		if curStage.loadParts(i):
			curStage.attrs[i].load("./Kero Blaster/rsc_k/img/" + paramParts + ".pxattr")
			curStage.createMapSurface(i)
			curStage.renderMapToSurface(i)
		else:
			curStage.pack.layers[i].partsName = oldParts

	window.visible = False


def togglePxPackAttributes(window, elem, gxEdit):
	elem = gxEdit.elements["pxPackAttrDialog"]

	elem.curStage = gxEdit.stages[gxEdit.curStage]
	curStage = gxEdit.stages[gxEdit.curStage]

	elem.elements["descEdit"].text = curStage.pack.description
	elem.elements["sprEdit"].text = curStage.pack.spritesheet

	elem.elements["areaXEdit"].text = str(curStage.pack.area_x)
	elem.elements["areaYEdit"].text = str(curStage.pack.area_y)

	elem.elements["areaNoEdit"].text = str(curStage.pack.area_no)

	elem.elements["rEdit"].text = str(curStage.pack.bg_r)
	elem.elements["gEdit"].text = str(curStage.pack.bg_g)
	elem.elements["bEdit"].text = str(curStage.pack.bg_b)

	elem.elements["leftEdit"].text = curStage.pack.left_field
	elem.elements["rightEdit"].text = curStage.pack.right_field
	elem.elements["upEdit"].text = curStage.pack.up_field
	elem.elements["downEdit"].text = curStage.pack.down_field


	elem.elements["map0PartsEdit"].text = curStage.pack.layers[0].partsName
	elem.elements["map0STEdit"].text = str(curStage.pack.layers[0].scrolltype)
	elem.elements["map0VEdit"].text = str(curStage.pack.layers[0].visibility)

	elem.elements["map1PartsEdit"].text = curStage.pack.layers[1].partsName
	elem.elements["map1STEdit"].text = str(curStage.pack.layers[1].scrolltype)
	elem.elements["map1VEdit"].text = str(curStage.pack.layers[1].visibility)

	elem.elements["map2PartsEdit"].text = curStage.pack.layers[2].partsName
	elem.elements["map2STEdit"].text = str(curStage.pack.layers[2].scrolltype)
	elem.elements["map2VEdit"].text = str(curStage.pack.layers[2].visibility)

	elem.x = gWindowWidth // 2 - elem.w // 2
	elem.y = gWindowHeight // 2 - elem.h // 2
	gxEdit.elements["pxPackAttrDialog"] = gxEdit.elements.pop("pxPackAttrDialog")
	elem.visible ^= 1


def toggleResizeDialog(window, elem, gxEdit):
	elem = gxEdit.elements["mapSizeDialog"]

	elem.currentLayer = gxEdit.currentLayer
	elem.curStage = gxEdit.stages[gxEdit.curStage]
	curStage = gxEdit.stages[gxEdit.curStage]

	elem.elements["paramX"].text = str(curStage.pack.layers[elem.currentLayer].width)
	elem.elements["paramY"].text = str(curStage.pack.layers[elem.currentLayer].height)



	elem.x = gWindowWidth // 2 - elem.w // 2
	elem.y = gWindowHeight // 2 - elem.h // 2
	gxEdit.elements["mapSizeDialog"] = gxEdit.elements.pop("mapSizeDialog")
	elem.visible ^= 1

def toggleMultiplayerMenu(window, elem, gxEdit):
	elem = gxEdit.elements["dialogMultiplayer"]
	elem.x = gWindowWidth // 2 - elem.w // 2
	elem.y = gWindowHeight // 2 - elem.h // 2
	gxEdit.elements["dialogMultiplayer"] = gxEdit.elements.pop("dialogMultiplayer")
	elem.visible ^= 1

def toggleLayerVisibility(window, elem, gxEdit):
	gxEdit.visibleLayers[elem.var] = True if elem.state == BUTTON_STATE_ACTIVE else False

def changeTilePaintMode(window, elem, gxEdit):
	if elem.enum == BUTTON_DRAW:
		gxEdit.currentTilePaintMode = const.PAINT_NORMAL
	elif elem.enum == BUTTON_ERASE:
		gxEdit.currentTilePaintMode = const.PAINT_ERASE
	elif elem.enum == BUTTON_COPY:
		gxEdit.currentTilePaintMode = const.PAINT_COPY
	elif elem.enum == BUTTON_FILL:
		gxEdit.currentTilePaintMode = const.PAINT_FILL
	elif elem.enum == BUTTON_REPLACE:
		gxEdit.currentTilePaintMode = const.PAINT_REPLACE
	elif elem.rects == rectsButtonRectangle:
		gxEdit.currentTilePaintMode = const.PAINT_RECTANGLE
	gxEdit.copyingTiles = False

class MultiplayerWindow(UIWindow):
	def __init__(self, x, y, w, h, type=const.WINDOW_TOOLS, style=0,):
		UIWindow.__init__(self, x, y, w, h, type, style)

		self.elements["paramIP"] = UITextInput(40, 5, 160, 18, "", sdlColorGreen, TTF_STYLE_NORMAL, self)
		self.elements["paramIP"].placeholderText = "pixeltellsthetruth.solutions"
		self.elements["paramPort"] = UITextInput(40, 30, 40, 18, "", sdlColorGreen, TTF_STYLE_NORMAL, self, style=const.TEXTINPUTTYPE_NUMBER, maxlen=5)
		self.elements["paramPort"].placeholderText = "7777"

		self.elements["paramName"] = UITextInput(120, 30, 80, 18, "", sdlColorGreen, TTF_STYLE_NORMAL, self, maxlen=16)

		self.elements["textXs"] = UIText(6, 6, "IP:", sdlColorBlack, TTF_STYLE_NORMAL, self)
		self.elements["textX"] = UIText(7, 7, "IP:", sdlColorYellow, TTF_STYLE_NORMAL, self)
		self.elements["textYs"] = UIText(6, 30, "Port:", sdlColorBlack, TTF_STYLE_NORMAL, self)
		self.elements["textY"] = UIText(7, 31, "Port:", sdlColorYellow, TTF_STYLE_NORMAL, self)

		self.elements["textNames"] = UIText(84, 30, "Name:", sdlColorBlack, TTF_STYLE_NORMAL, self)
		self.elements["textName"] = UIText(85, 31, "Name:", sdlColorYellow, TTF_STYLE_NORMAL, self)

		self.elements["textHost"] = UIText(12, 68, "Host", sdlColorBlack, TTF_STYLE_NORMAL, self)
		self.elements["textConnect"] = UIText(48, 68, "Connect", sdlColorBlack, TTF_STYLE_NORMAL, self)

		self.elements["buttonHost"] = UIButton(12, 54, 16, 16, self)
		self.elements["buttonHost"].onAction = multi.hostButtonAction
		self.elements["buttonConnect"] = UIButton(54, 54, 16, 16, self)
		self.elements["buttonConnect"].onAction = multi.connectButtonAction
	
	
class ToolsWindow(UIWindow):
	def __init__(self, x, y, w, h, type=const.WINDOW_TOOLS, style=0, visible=True):
		UIWindow.__init__(self, x, y, w, h, type, style, visible)

		#---TOOLS
		self.elements["textTools"] = UIElement(4, 2, 0, 0, self, rectWindowTextTools)

		self.elements["butDraw"] = UIButton(8, 20, 16, 16, self, style=const.STYLE_TOOLTIP_YELLOW, enum=BUTTON_DRAW, type=BUTTON_TYPE_RADIO, group=2,
										tooltip=[["Paint", sdlColorBlack, TTF_STYLE_NORMAL]],
										state=BUTTON_STATE_ACTIVE)
		self.elements["butDraw"].onAction = changeTilePaintMode

		self.elements["butErase"] = UIButton(28, 20, 16, 16, self, style=const.STYLE_TOOLTIP_YELLOW, enum=BUTTON_ERASE, type=BUTTON_TYPE_RADIO, group=2,
										tooltip=[["Erase", sdlColorBlack, TTF_STYLE_NORMAL]])
		self.elements["butErase"].onAction = changeTilePaintMode

		self.elements["butCopy"] = UIButton(48, 20, 16, 16, self, style=const.STYLE_TOOLTIP_YELLOW, enum=BUTTON_COPY, type=BUTTON_TYPE_RADIO, group=2,
										tooltip=[["Copy", sdlColorBlack, TTF_STYLE_NORMAL]])
		self.elements["butCopy"].onAction = changeTilePaintMode

		self.elements["butFill"] = UIButton(20, 36, 16, 16, self, style=const.STYLE_TOOLTIP_YELLOW, enum=BUTTON_FILL, type=BUTTON_TYPE_RADIO, group=2,
										tooltip=[["Fill", sdlColorBlack, TTF_STYLE_NORMAL]])
		self.elements["butFill"].onAction = changeTilePaintMode

		self.elements["butReplace"] = UIButton(40, 36, 16, 16, self, style=const.STYLE_TOOLTIP_YELLOW, enum=BUTTON_REPLACE, type=BUTTON_TYPE_RADIO, group=2,
										tooltip=[["Replace", sdlColorBlack, TTF_STYLE_NORMAL]])
		self.elements["butReplace"].onAction = changeTilePaintMode

		self.elements["butRectangle"] = UIButton(60, 36, 16, 16, self, style=const.STYLE_TOOLTIP_YELLOW, rects=rectsButtonRectangle, type=BUTTON_TYPE_RADIO, group=2,
										tooltip=[["Rectangle", sdlColorBlack, TTF_STYLE_NORMAL]])
		self.elements["butRectangle"].onAction = changeTilePaintMode

		#---LAYER

				#---TOOLS
		self.elements["textLayer"] = UIElement(88, 2, 0, 0, self, rectWindowTextLayer)

		self.elements["butMap0"] = UIButton(88, 20, 16, 16, self, style=const.STYLE_TOOLTIP_YELLOW, enum=BUTTON_MAP0, type=BUTTON_TYPE_CHECKBOX,
										var=0, 	state=BUTTON_STATE_ACTIVE,
										tooltip=[["Display foreground", sdlColorBlack, TTF_STYLE_NORMAL]])
		self.elements["butMap0"].onAction = toggleLayerVisibility

		self.elements["butMap1"] = UIButton(104, 20, 16, 16, self, style=const.STYLE_TOOLTIP_YELLOW, enum=BUTTON_MAP1, type=BUTTON_TYPE_CHECKBOX, 
										var=1, state=BUTTON_STATE_ACTIVE,
										tooltip=[["Display midground", sdlColorBlack, TTF_STYLE_NORMAL]])
		self.elements["butMap1"].onAction = toggleLayerVisibility

		self.elements["butMap2"] = UIButton(120, 20, 16, 16, self, style=const.STYLE_TOOLTIP_YELLOW, enum=BUTTON_MAP2, type=BUTTON_TYPE_CHECKBOX,
										var=2,	state=BUTTON_STATE_ACTIVE,
										tooltip=[["Display background", sdlColorBlack, TTF_STYLE_NORMAL]])
		self.elements["butMap2"].onAction = toggleLayerVisibility

		self.elements["textLVMP"] = UIElement(136, 20, 0, 0, self, rectWindowTextLVMP)

		self.elements["butUnits"] = UIButton(152, 20, 16, 16, self, style=const.STYLE_TOOLTIP_YELLOW, enum=BUTTON_UNITS, type=BUTTON_TYPE_CHECKBOX,
										var=3,	state=BUTTON_STATE_ACTIVE,
										tooltip=[["Display entities (units)", sdlColorBlack, TTF_STYLE_NORMAL]])
		self.elements["butUnits"].onAction = toggleLayerVisibility

		self.elements["butAttr"] = UIButton(168, 20, 16, 16, self, style=const.STYLE_TOOLTIP_YELLOW, enum=BUTTON_TILETYPE, type=BUTTON_TYPE_CHECKBOX,
										var=4,
										tooltip=[["Display tile attributes", sdlColorBlack, TTF_STYLE_NORMAL]])
		self.elements["butAttr"].onAction = toggleLayerVisibility

		self.elements["butToggleMultiplayer"] = UIButton(132, 60, 16, 16, self, style=const.STYLE_TOOLTIP_YELLOW,
												enum=BUTTON_MULTIPLAYER,
												tooltip=[["multiplayer", sdlColorBlack, TTF_STYLE_NORMAL]])
		self.elements["butToggleMultiplayer"].onAction = toggleMultiplayerMenu

		self.elements["butTogglePackAttr"] = UIButton(160, 60, 16, 16, self, style=const.STYLE_TOOLTIP_YELLOW,
												enum=BUTTON_SCRIPT,
												tooltip=[["Edit pxpack attributes", sdlColorBlack, TTF_STYLE_NORMAL]])
		self.elements["butTogglePackAttr"].onAction = togglePxPackAttributes


def editEntityAttributes(control, gxEdit):
	param = control.text
	try:
		int(param)
	except ValueError:
		param = 0
	
	stage = gxEdit.stages[gxEdit.curStage]
	select = stage.selectedEntities

	ids = [o.id for o in select]

	if control.paramtype == const.PARAM_FLAG:
		stage.pack.eve.modify(ids, flag=int(param))
	elif control.paramtype == const.PARAM_PARAM2:
		stage.pack.eve.modify(ids, param2=int(param))
	elif control.paramtype == const.PARAM_BITS:
		stage.pack.eve.modify(ids, bits=int(param))
		control.parent.elements["textHexBitsS"].text = util.lazybin(select[0].bits, 8)
		control.parent.elements["textHexBits"].text = util.lazybin(select[0].bits, 8)

	#stage.pack.eve.modify(ids, type2=int(param))

def editEntityBits(window, elem, gxEdit):
	stage = gxEdit.stages[gxEdit.curStage]
	select = stage.selectedEntities

	ids = [o.id for o in select]
	if elem.state == BUTTON_STATE_ACTIVE:
		stage.pack.eve.modify(ids, bits=select[0].bits | elem.var)
	else:
		stage.pack.eve.modify(ids, bits=select[0].bits & ~(elem.var))

	window.elements["textHexBitsS"].text = util.lazybin(select[0].bits, 8)
	window.elements["textHexBits"].text = util.lazybin(select[0].bits, 8)




def editEntityString(control, gxEdit):
	param = control.text
	stage = gxEdit.stages[gxEdit.curStage]
	select = stage.selectedEntities

	ids = [o.id for o in select]
	stage.pack.eve.modify(ids, string=param)


class EntityEditWindow(UIWindow):
	def __init__(self, x, y, w, h, type=const.WINDOW_ENTITYEDIT, style=0):
		UIWindow.__init__(self, x, y, w, h, type, style)

		self.selectedEntities = []

		self.elements["textAppearShadow"] = UIText(6, 6, "Flag:", sdlColorBlack, TTF_STYLE_NORMAL, self)
		self.elements["textAppear"] = UIText(5, 5, "Flag:", sdlColorYellow, TTF_STYLE_NORMAL, self)
		self.elements["flagEdit"] = UITextInput(60, 5, 80, 18, "", sdlColorGreen, TTF_STYLE_BOLD, self, style=const.TEXTINPUTTYPE_NUMBER,
			paramtype=const.PARAM_FLAG, maxlen=65535)
		self.elements["flagEdit"].onAction = editEntityAttributes

		self.elements["textDirShadow"] = UIText(6, 25, "Param2:", sdlColorBlack, TTF_STYLE_NORMAL, self)
		self.elements["textDir"] = UIText(5, 25, "Param2:", sdlColorYellow, TTF_STYLE_NORMAL, self)
		self.elements["dirEdit"] = UITextInput(60, 25, 80, 18, "", sdlColorGreen, TTF_STYLE_BOLD, self, style=const.TEXTINPUTTYPE_NUMBER,
			paramtype=const.PARAM_PARAM2, maxlen=255)
		self.elements["dirEdit"].onAction = editEntityAttributes

		self.elements["textStrShadow"] = UIText(6, 45, "String:", sdlColorBlack, TTF_STYLE_NORMAL, self)
		self.elements["textStr"] = UIText(5, 45, "String:", sdlColorYellow, TTF_STYLE_NORMAL, self)
		self.elements["stringEdit"] = UITextInput(60, 45, 80, 18, "", sdlColorGreen, TTF_STYLE_BOLD, self,
			paramtype=const.PARAM_STRING, maxlen=15)
		self.elements["stringEdit"].onAction = editEntityString

		self.elements["textBitsShadow"] = UIText(6, 69, "Bits:", sdlColorBlack, TTF_STYLE_NORMAL, self)
		self.elements["textBits"] = UIText(5, 68, "Bits:", sdlColorYellow, TTF_STYLE_NORMAL, self)

		self.elements["textHexBitsS"] = UIText(74, 70, "a", sdlColorBlack, TTF_STYLE_NORMAL, self)
		self.elements["textHexBits"] = UIText(73, 70, "a", sdlColorYellow, TTF_STYLE_NORMAL, self)

		self.elements["butCheckBits1"] = UIButton(120, 90, 16, 12, self, rects=rectsButtonCheckbox, type=BUTTON_TYPE_CHECKBOX, var=1)
		#seems to only have an effect when spawning, (is set during creation)
		self.elements["textBitsDesc1"] = UIText(15, 88, "I don't know", sdlColorYellow, TTF_STYLE_NORMAL, self)
		self.elements["butCheckBits2"] = UIButton(120, 110, 16, 12, self, rects=rectsButtonCheckbox, type=BUTTON_TYPE_CHECKBOX, var=2)
		#365 may use this
		self.elements["textBitsDesc2"] = UIText(15, 109, "unused?", sdlColorYellow, TTF_STYLE_NORMAL, self)
		self.elements["butCheckBits3"] = UIButton(120, 130, 16, 12, self, rects=rectsButtonCheckbox, type=BUTTON_TYPE_CHECKBOX, var=4)
		self.elements["textBitsDesc3"] = UIText(15, 128, "Run script on touch:", sdlColorYellow, TTF_STYLE_NORMAL, self)
		self.elements["butCheckBits4"] = UIButton(120, 150, 16, 12, self, rects=rectsButtonCheckbox, type=BUTTON_TYPE_CHECKBOX, var=8)
		self.elements["textBitsDesc4"] = UIText(15, 148, "Run script on death:", sdlColorYellow, TTF_STYLE_NORMAL, self)
		self.elements["butCheckBits5"] = UIButton(120, 170, 16, 12, self, rects=rectsButtonCheckbox, type=BUTTON_TYPE_CHECKBOX, var=16)
		self.elements["textBitsDesc5"] = UIText(15, 168, "Spawn with alt dir:", sdlColorYellow, TTF_STYLE_NORMAL, self)
		self.elements["butCheckBits6"] = UIButton(120, 190, 16, 12, self, rects=rectsButtonCheckbox, type=BUTTON_TYPE_CHECKBOX, var=32)
		#631, 446, 448, 447, 197, 179, 177 npc acts may use this
		self.elements["textBitsDesc6"] = UIText(15, 188, "unused?", sdlColorYellow, TTF_STYLE_NORMAL, self)
		
		self.elements["butCheckBits7"] = UIButton(120, 210, 16, 12, self, rects=rectsButtonCheckbox, type=BUTTON_TYPE_CHECKBOX, var=64)
		self.elements["textBitsDesc7"] = UIText(15, 208, "No appear if flag set", sdlColorYellow, TTF_STYLE_NORMAL, self)
		self.elements["butCheckBits8"] = UIButton(120, 230, 16, 12, self, rects=rectsButtonCheckbox, type=BUTTON_TYPE_CHECKBOX, var=128)
		self.elements["textBitsDesc8"] = UIText(15, 228, "Appear if flag set", sdlColorYellow, TTF_STYLE_NORMAL, self)
		self.elements["butCheckBits1"].onAction = editEntityBits
		self.elements["butCheckBits2"].onAction = editEntityBits
		self.elements["butCheckBits3"].onAction = editEntityBits
		self.elements["butCheckBits4"].onAction = editEntityBits
		self.elements["butCheckBits5"].onAction = editEntityBits
		self.elements["butCheckBits6"].onAction = editEntityBits
		self.elements["butCheckBits7"].onAction = editEntityBits
		self.elements["butCheckBits8"].onAction = editEntityBits


class YesNoCancelDialog(UIWindow):
	pass

class YesNoDialog(UIWindow):
	pass

class ResizeControl(UIElement):
	pass

def mapResizeAction(window, elem, gxEdit):
	paramX = window.elements["paramX"].text
	paramY = window.elements["paramY"].text
	curStage = window.curStage
	curLayer = curStage.pack.layers[window.currentLayer]
	try:
		x = int(paramX)
	except:
		x = curLayer.width
	try:
		y = int(paramY)
	except:
		x = curLayer.height

	if x == curLayer.width and y == curLayer.height:
		window.visible = False
		return

	#"max texture dimensions are 16384x16384"
	if x * const.tileWidth > 16384: x = 16384 // const.tileWidth
	if y * const.tileWidth > 16384: y = 16384 // const.tileWidth

	curLayer.resize(x, y)
	curStage.createMapSurface(window.currentLayer)
	curStage.renderMapToSurface(window.currentLayer)
	window.visible = False

class MapResizeDialog(UIWindow):
	def __init__(self, x, y, w, h, type=const.WINDOW_ENTITYEDIT, style=0):
		UIWindow.__init__(self, x, y, w, h, type, style)

		self.elements["textXs"] = UIText(6, 6, "X:", sdlColorBlack, TTF_STYLE_NORMAL, self)
		self.elements["textX"] = UIText(7, 7, "X:", sdlColorYellow, TTF_STYLE_NORMAL, self)
		self.elements["textYs"] = UIText(6, 30, "Y:", sdlColorBlack, TTF_STYLE_NORMAL, self)
		self.elements["textY"] = UIText(7, 31, "Y:", sdlColorYellow, TTF_STYLE_NORMAL, self)

		self.elements["paramX"] = UITextInput(20, 5, 80, 18, "", sdlColorGreen, TTF_STYLE_BOLD, self, style=const.TEXTINPUTTYPE_NUMBER)
		self.elements["paramY"] = UITextInput(20, 28, 80, 18, "", sdlColorGreen, TTF_STYLE_BOLD, self, style=const.TEXTINPUTTYPE_NUMBER)

		self.elements["textOk"] = UIText(16, 68, "Ok", sdlColorYellow, TTF_STYLE_NORMAL, self)
		self.elements["textCancel"] = UIText(54, 68, "Cancel", sdlColorYellow, TTF_STYLE_NORMAL, self)

		self.elements["buttonOk"] = UIButton(15, 50, 16, 16, self)
		self.elements["buttonOk"].onAction = mapResizeAction
		self.elements["buttonCancel"] = UIButton(60, 50, 16, 16, self)
		self.elements["buttonCancel"].onAction = minimizeButtonAction

		#TODO: stage parameter

class PxPackAttrDialog(UIWindow):
	def __init__(self, x, y, w, h, type=const.WINDOW_ENTITYEDIT, style=0):
		UIWindow.__init__(self, x, y, w, h, type, style)

		self.elements["textDesc"] = UIText(6, 6, "Map Name", sdlColorYellow, TTF_STYLE_NORMAL, self)
		self.elements["descEdit"] = UITextInput(68, 6, 120, 18, "", sdlColorGreen, TTF_STYLE_BOLD, self,
			maxlen=16)


		self.elements["textSpr"] = UIText(6, 34, "Spritesheet", sdlColorYellow, TTF_STYLE_NORMAL, self)
		self.elements["sprEdit"] = UITextInput(68, 34, 80, 18, "", sdlColorGreen, TTF_STYLE_BOLD, self,
			maxlen=16)

		self.elements["textAreaxy"] = UIText(6, 72, "Area x, y", sdlColorYellow, TTF_STYLE_NORMAL, self)
		self.elements["areaXEdit"] = UITextInput(68, 72, 40, 18, "", sdlColorGreen, TTF_STYLE_BOLD, self, style=const.TEXTINPUTTYPE_NUMBER,
			maxlen=255)
		self.elements["areaYEdit"] = UITextInput(112, 72, 40, 18, "", sdlColorGreen, TTF_STYLE_BOLD, self, style=const.TEXTINPUTTYPE_NUMBER,
			maxlen=255)

		self.elements["textAreano"] = UIText(6, 96, "Area no.", sdlColorYellow, TTF_STYLE_NORMAL, self)
		self.elements["areaNoEdit"] = UITextInput(68, 96, 40, 18, "", sdlColorGreen, TTF_STYLE_BOLD, self, style=const.TEXTINPUTTYPE_NUMBER,
			maxlen=255)


		self.elements["textRGB"] = UIText(6, 120, "R,G,B", sdlColorYellow, TTF_STYLE_NORMAL, self)
		self.elements["rEdit"] = UITextInput(68, 120, 40, 18, "", sdlColorGreen, TTF_STYLE_BOLD, self, style=const.TEXTINPUTTYPE_NUMBER,
			maxlen=255)
		self.elements["gEdit"] = UITextInput(112, 120, 40, 18, "", sdlColorGreen, TTF_STYLE_BOLD, self, style=const.TEXTINPUTTYPE_NUMBER,
			maxlen=255)
		self.elements["bEdit"] = UITextInput(154, 120, 40, 18, "", sdlColorGreen, TTF_STYLE_BOLD, self, style=const.TEXTINPUTTYPE_NUMBER,
			maxlen=255)

		self.elements["textLeft"] = UIText(6, 160, "Left", sdlColorYellow, TTF_STYLE_NORMAL, self)
		self.elements["leftEdit"] = UITextInput(68, 160, 120, 18, "", sdlColorGreen, TTF_STYLE_BOLD, self,
			maxlen=16)

		self.elements["textRight"] = UIText(6, 180, "Right", sdlColorYellow, TTF_STYLE_NORMAL, self)
		self.elements["rightEdit"] = UITextInput(68, 180, 120, 18, "", sdlColorGreen, TTF_STYLE_BOLD, self,
			maxlen=16)

		self.elements["textUp"] = UIText(6, 200, "Up", sdlColorYellow, TTF_STYLE_NORMAL, self)
		self.elements["upEdit"] = UITextInput(68, 200, 120, 18, "", sdlColorGreen, TTF_STYLE_BOLD, self,
			maxlen=16)
		self.elements["textDown"] = UIText(6, 220, "Down", sdlColorYellow, TTF_STYLE_NORMAL, self)
		self.elements["downEdit"] = UITextInput(68, 220, 120, 18, "", sdlColorGreen, TTF_STYLE_BOLD, self,
			maxlen=16)


		self.elements["textMap0Parts"] = UIText(200, 6, "Map0 Parts", sdlColorYellow, TTF_STYLE_NORMAL, self)
		self.elements["map0PartsEdit"] = UITextInput(280, 6, 120, 18, "", sdlColorGreen, TTF_STYLE_BOLD, self,
			maxlen=16)
		self.elements["textMap0ST"] = UIText(200, 26, "Map0 ScrollType", sdlColorYellow, TTF_STYLE_NORMAL, self)
		self.elements["map0STEdit"] = UITextInput(280, 26, 120, 18, "", sdlColorGreen, TTF_STYLE_BOLD, self, style=const.TEXTINPUTTYPE_NUMBER,
			maxlen=16)
		self.elements["textMap0V"] = UIText(200, 46, "Map0 Visibility", sdlColorYellow, TTF_STYLE_NORMAL, self)
		self.elements["map0VEdit"] = UITextInput(280, 46, 120, 18, "", sdlColorGreen, TTF_STYLE_BOLD, self, style=const.TEXTINPUTTYPE_NUMBER,
			maxlen=16)
		self.elements["textMap1Parts"] = UIText(200, 86, "Map1 Parts", sdlColorYellow, TTF_STYLE_NORMAL, self)
		self.elements["map1PartsEdit"] = UITextInput(280, 86, 120, 18, "", sdlColorGreen, TTF_STYLE_BOLD, self,
			maxlen=16)
		self.elements["textMap1ST"] = UIText(200, 106, "Map1 ScrollType", sdlColorYellow, TTF_STYLE_NORMAL, self)
		self.elements["map1STEdit"] = UITextInput(280, 106, 120, 18, "", sdlColorGreen, TTF_STYLE_BOLD, self, style=const.TEXTINPUTTYPE_NUMBER,
			maxlen=16)
		self.elements["textMap1V"] = UIText(200, 126, "Map1 Visibility", sdlColorYellow, TTF_STYLE_NORMAL, self)
		self.elements["map1VEdit"] = UITextInput(280, 126, 120, 18, "", sdlColorGreen, TTF_STYLE_BOLD, self, style=const.TEXTINPUTTYPE_NUMBER,
			maxlen=16)
		self.elements["textMap2Parts"] = UIText(200, 166, "Map2 Parts", sdlColorYellow, TTF_STYLE_NORMAL, self)
		self.elements["map2PartsEdit"] = UITextInput(280, 166, 120, 18, "", sdlColorGreen, TTF_STYLE_BOLD, self,
			maxlen=16)
		self.elements["textMap2ST"] = UIText(200, 186, "Map2 ScrollType", sdlColorYellow, TTF_STYLE_NORMAL, self)
		self.elements["map2STEdit"] = UITextInput(280, 186, 120, 18, "", sdlColorGreen, TTF_STYLE_BOLD, self, style=const.TEXTINPUTTYPE_NUMBER,
			maxlen=16)
		self.elements["textMap2V"] = UIText(200, 206, "Map2 Visibility", sdlColorYellow, TTF_STYLE_NORMAL, self)
		self.elements["map2VEdit"] = UITextInput(280, 206, 120, 18, "", sdlColorGreen, TTF_STYLE_BOLD, self, style=const.TEXTINPUTTYPE_NUMBER,
			maxlen=16)


		self.elements["textOk"] = UIText(290, 255, "Ok", sdlColorYellow, TTF_STYLE_NORMAL, self)
		self.elements["textCancel"] = UIText(360, 255, "Cancel", sdlColorYellow, TTF_STYLE_NORMAL, self)

		self.elements["buttonOk"] = UIButton(290, 235, 16, 16, self)
		self.elements["buttonOk"].onAction = editPxPackAttributes
		self.elements["buttonCancel"] = UIButton(365, 235, 16, 16, self)
		self.elements["buttonCancel"].onAction = minimizeButtonAction

		#TODO: stage parameter

class StartGameDialog(UIWindow):
	pass

def safe_div(a, b):
	return 0 if b == 0 else a / b

def lerp(a, b, percent):
	return a * (1 - percent) + b * percent

#this probably shouldn't be a class but i don't want to refactor it again
class Interface:
	def __init__(self, renderer, window, sprfactory):
		self.renderer = renderer
		self.window = window
		self.sprfactory = sprfactory

	def loadSurfaces(self):
		RESOURCES = "./BITMAP/"

		gSurfaces[SURF_WINDOWBG] = self.sprfactory.from_image(RESOURCES + "dgBg.bmp")
		gSurfaces[SURF_WINDOWBG2] = self.sprfactory.from_image(RESOURCES + "dgBg2.bmp")
		gSurfaces[SURF_COLOR_BLACK] = self.sprfactory.from_color(sdl2.ext.Color(0,0,0),(32,32))
		gSurfaces[SURF_COLOR_ORANGE] = sdl2.ext.Color(0,255,0)
		gSurfaces[SURF_COLOR_ORANGE_DARK] = sdl2.ext.Color(0,255,0)
		gSurfaces[SURF_COLOR_GREEN] = self.sprfactory.from_color(sdl2.ext.Color(0,255,0),(32,32))

		gSurfaces[SURF_COLOR_BLUE] = self.sprfactory.from_color(sdl2.ext.Color(84,108,128),(32,32))

		gSurfaces[SURF_SDLCOLOR_MAGENTA] = self.sprfactory.from_color(sdlColorMagenta,(32,32))
		gSurfaces[SURF_SDLCOLOR_GOLD] = self.sprfactory.from_color(sdlColorGold,(32,32))
		gSurfaces[SURF_SDLCOLOR_GREEN] = self.sprfactory.from_color(sdlColorGreen,(32,32))
		gSurfaces[SURF_SDLCOLOR_RED] = self.sprfactory.from_color(sdlColorRed,(32,32))
		gSurfaces[SURF_SDLCOLOR_CYAN] = self.sprfactory.from_color(sdlColorCyan,(32,32))



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

		gSurfaces[SURF_COLOR_WHITE_TRANSPARENT] = self.sprfactory.from_color(sdl2.ext.Color(255,255,255, 255), size=(32, 32),
           masks=(0xFF000000,           
                  0x00FF0000,           
                  0x0000FF00,           
                  0x000000FF))   

		gSurfaces[SURF_UNITS] = self.sprfactory.from_image(unitsName)
		gSurfaces[SURF_ATTRIBUTE] = self.sprfactory.from_image("assist/attribute.png")


		gSurfaces[SURF_UIWINDOW] = self.sprfactory.from_image(RESOURCES + "Window.bmp")

		gSurfaces[SURF_NUMBER] = self.sprfactory.from_image(RESOURCES + "Number.bmp")

		gSurfaces[SURF_EDITORBG] = self.sprfactory.from_image(RESOURCES + "Background.bmp")

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
	
	def setMapEntityTooltip(self, gxEdit, stage, x, y):
		gxEdit.tooltipText = []
		for o in stage.pack.eve.units:
			#TODO: multiple entities
			#TODO: highlight hovered in picker
			if o.x == x + stage.hscroll*const.ENTITY_SCALE and o.y == y + stage.scroll*const.ENTITY_SCALE:
				index = o.type1

				titleColor, descColor, paramColor = getEntityColors(index)

				gxEdit.tooltipText.append([gxEdit.entityInfo[index][0], titleColor, TTF_STYLE_BOLD])
				gxEdit.tooltipStyle = const.STYLE_TOOLTIP_BLACK

				if gxEdit.elements["entEdit"].visible:
					if gxEdit.entityInfo[index][2] != "":
						gxEdit.tooltipText.append([gxEdit.entityInfo[index][2], paramColor, TTF_STYLE_NORMAL])

				gxEdit.tooltipText.append(["Param2: " + str(o.param2), sdlColorWhite, TTF_STYLE_NORMAL])

	def renderTilePreview(self, gxEdit, stage):

		mouse = util.getMouseState()
		mag = gxEdit.magnification
		map = stage.pack.layers[gxEdit.currentLayer]

		if gxEdit.currentEditMode == const.EDIT_TILE:
			if gxEdit.rectanglePaintBoxStart == [-1, -1]: #normal
				x = int(mouse.x // (const.tileWidth * mag))
				y = int(mouse.y // (const.tileWidth * mag))

				if x >= map.width or y >= map.height: return

				start = stage.selectedTilesStart[:]
				end = stage.selectedTilesEnd[:]

				negX = negY = False
				if start[0] > end[0]:
					start[0], end[0] = end[0], start[0]
					negX = True
				if end[1] < start[1]:
					start[1], end[1] = end[1], start[1]
					negY = True

				w = end[0] - start[0] + 1
				h = end[1] - start[1] + 1

				if gxEdit.currentTilePaintMode != const.PAINT_COPY:
					if negX: x -= w - 1
					if negY: y -= h - 1
				else:
					if not negX: x -= w - 1
					if not negY: y -= h - 1

				x *= int(const.tileWidth * mag)
				y *= int(const.tileWidth * mag)

				w *= int(const.tileWidth * mag)
				h *= int(const.tileWidth * mag)

				#selected tile preview
				#TODO: how will this work with copy?
				if gxEdit.showTilePreview:
					sdl2.SDL_SetTextureAlphaMod(stage.parts[gxEdit.currentLayer].texture, 128)

					prtrect = (start[0]*const.tileWidth, start[1]*const.tileWidth,
						(end[0] - start[0] + 1) * const.tileWidth, (end[1] - start[1] + 1) * const.tileWidth)
					self.renderer.copy(stage.parts[gxEdit.currentLayer], srcrect=prtrect, dstrect=(x,y,w,h))

					sdl2.SDL_SetTextureAlphaMod(stage.parts[gxEdit.currentLayer].texture, 255)
			else: #rectangle box (should probably still show tile preview)
				start = gxEdit.rectanglePaintBoxStart[:]
				end = gxEdit.rectanglePaintBoxEnd[:]

				negX = negY = False
				if start[0] > end[0]:
					start[0], end[0] = end[0], start[0]
					negX = True
				if end[1] < start[1]:
					start[1], end[1] = end[1], start[1]
					negY = True

				x = start[0] - stage.hscroll
				y = start[1] - stage.scroll
				w = end[0] - start[0] + 1
				h = end[1] - start[1] + 1

				x *= int(const.tileWidth * mag)
				y *= int(const.tileWidth * mag)

				w *= int(const.tileWidth * mag)
				h *= int(const.tileWidth * mag)

		elif gxEdit.currentEditMode == const.EDIT_ENTITY:
			if gxEdit.draggingEntities: return
			x = int(mouse.x // (const.tileWidth2//2 * mag)) 
			y = int(mouse.y // (const.tileWidth2//2 * mag))

			if x >= map.width*const.ENTITY_SCALE or y >= map.height*const.ENTITY_SCALE: return

			self.setMapEntityTooltip(gxEdit, stage, x, y)

			x *= int(const.tileWidth2//2 * mag)
			y *= int(const.tileWidth2//2 * mag)

			w = int(const.tileWidth2//2 * mag)
			h = int(const.tileWidth2//2 * mag)
		#TODO: different color with rectangle and copy?
		sdl2.SDL_SetTextureColorMod(gSurfaces[SURF_COLOR_WHITE_TRANSPARENT].texture, *gxEdit.tileHighlightColor)
		sdl2.SDL_SetTextureAlphaMod(gSurfaces[SURF_COLOR_WHITE_TRANSPARENT].texture, gxEdit.tileHighlightTimer)

		if gxEdit.tileHighlightAnimate:
			gxEdit.tileHighlightTimer+= 2 if gxEdit.tileHighlightDir else -2
			if gxEdit.tileHighlightTimer*2 > 90*2:
				gxEdit.tileHighlightDir = 0
			if gxEdit.tileHighlightTimer <= 0:
				gxEdit.tileHighlightDir = 1
		else:
			gxEdit.tileHighlightTimer = 48*2
		
		self.renderer.copy(gSurfaces[SURF_COLOR_WHITE_TRANSPARENT], dstrect=(x, y, w, h))

		
	def renderPlayers(self, gxEdit, stage):
		mag = gxEdit.magnification
		for _, player in gxEdit.players.items():
			if "mousepos" not in player: continue
			if "curStage" not in player: continue
			if player["curStage"] is not gxEdit.curStage: continue
			if "lerpmousepos" not in player:
				player["lerpmousepos"] = [0, 0]
				player["lerpxm"] = 0
				player["lerpym"] = 1

			xBound = int(stage.hscroll * const.tileWidth * mag)
			yBound = int(stage.scroll * const.tileWidth * mag)
			#TODO: interp
			targetX = int(player["mousepos"][0] * mag) - xBound
			targetY = int(player["mousepos"][1] * mag) - yBound
			x = player["lerpmousepos"][0] 
			y = player["lerpmousepos"][1]

			dx = targetX - x
			dy = targetY - y
			
			player["lerpxm"] += int(dx * 0.16)
			player["lerpym"] += int(dy * 0.16)

			if abs(player["lerpxm"]) > abs(int(dx * 0.1)): player["lerpxm"] = int(dx * 0.16)
			if abs(player["lerpym"]) > abs(int(dy * 0.1)): player["lerpym"] = int(dy * 0.16)
			

			x += player["lerpxm"]
			y += player["lerpym"]

			player["lerpmousepos"] = [x, y]

			#if it is offscreen
			dir = -1
			size = (0, 0)
			if x > gWindowWidth or y > gWindowHeight \
									or x < 0 or y < 0: 
				size = getTextSize(player["name"], gFont)
				if x < 0: #left
					x = 2
					dir = 0
				if y < 0: 
					y = 2
					dir = 1
				if x + size[0] > gWindowWidth: #right
					x = gWindowWidth - (size[0] // 2)
					dir = 2
				if y > gWindowHeight: #down
					y = gWindowHeight - 8 - size[1]
					dir = 3

				self.renderer.copy(gSurfaces[SURF_UIWINDOW], srcrect=rectsMultiplayerArrow[dir], dstrect=(x, y, rectsMultiplayerArrow[dir][2], rectsMultiplayerArrow[dir][3]))
			else:
				self.renderer.copy(gSurfaces[SURF_UIWINDOW], srcrect=rectMultiplayerCursor, 
								dstrect=(x, y, rectMultiplayerCursor[2], rectMultiplayerCursor[3]))

			if dir == 0:
				x += 4
			elif dir == 1:
				y += 8
				x -= size[0] // 2
			elif dir == 2:
				x -= size[0] + (size[0] // 4)
			elif dir == 3:
				y -= 8
				x -= size[0] // 2
			
			renderText(player["name"], sdlColorBlack, TTF_STYLE_NORMAL, x + 9, y + 1)
			renderText(player["name"], sdlColorWhite, TTF_STYLE_NORMAL, x + 8, y)

	def renderEntitySelectionBox(self, gxEdit, stage):
		mag = gxEdit.magnification
		if gxEdit.selectionBoxStart != [-1, -1]:
			x1 = gxEdit.selectionBoxStart[0] -  int(stage.hscroll * const.tileWidth * mag)
			y1 = gxEdit.selectionBoxStart[1] -  int(stage.scroll * const.tileWidth * mag)
			x2 = gxEdit.selectionBoxEnd[0] -  int(stage.hscroll * const.tileWidth * mag)
			y2 = gxEdit.selectionBoxEnd[1] -  int(stage.scroll * const.tileWidth * mag)
			
			if x1 > x2: x1, x2 = x2, x1
			if y1 > y2: y1, y2 = y2, y1
			
			self.drawBox(self.renderer, SURF_SDLCOLOR_CYAN, x1, y1, 
														x2 - x1, 
														y2 - y1)

	def renderTiles(self, gxEdit, stage, layerNo):
		for bit in gxEdit.tileRenderQueue:
			stg = gxEdit.stages[bit[0]]
			for pos, tile in bit[1]:
				stg.renderTileToSurface(pos[0], pos[1], tile[0],
											tile[1], bit[2])
											
		if len(stage.surfaces) < layerNo: return
		if not stage.surfaces[layerNo]: return
		
		gxEdit.tileRenderQueue = []

		map = stage.pack.layers[layerNo]
		mag = gxEdit.magnification

		srcx = int(stage.hscroll * const.tileWidth)
		srcy = int(stage.scroll * const.tileWidth)

		sizex = min(gWindowWidth*max(1, int(1/gxEdit.magnification)), stage.surfaces[layerNo].size[0], stage.surfaces[layerNo].size[0] - srcx)
		sizey = min(gWindowHeight*max(1, int(1/gxEdit.magnification)), stage.surfaces[layerNo].size[1], stage.surfaces[layerNo].size[1] - srcy)

		srcrect = (srcx, srcy, sizex, sizey)
		dstrect = (0, 0, int(sizex*mag), int(sizey*mag))

		self.renderer.copy(stage.surfaces[layerNo].texture, srcrect=srcrect, dstrect=dstrect)

		
	def renderTileAttr(self, gxEdit, stage):
		map = stage.pack.layers[gxEdit.currentLayer]
		attr = stage.attrs[gxEdit.currentLayer]
		mag = gxEdit.magnification
		for y in range(stage.scroll, stage.scroll + int(gWindowHeight // const.tileWidth // mag)):
			if y >= map.height: break
			for x in range(stage.hscroll, stage.hscroll + int(gWindowWidth // const.tileWidth // mag)):
				if x >= map.width: break

				dstx = (x - stage.hscroll) * const.tileWidth
				dsty = (y - stage.scroll) * const.tileWidth

				tile = map.tiles[y][x]
				xx = tile % 16 
				yy = tile // 16
				tile = attr.tiles[yy][xx]

				xxx = tile % 16 
				yyy = tile // 16
				srcx = xxx * 16
				srcy = yyy * 16

				srcrect = (srcx, srcy, 16, 16)
				dstrect = (dstx*int(mag), dsty*int(mag), const.tileWidth*int(mag), const.tileWidth*int(mag))

				self.renderer.copy(gSurfaces[SURF_ATTRIBUTE], srcrect=srcrect, dstrect=dstrect)

	def renderTilePalette(self, gxEdit, stage):
		#TODO: placeholder
		pass




	def renderEntities(self, gxEdit, stage):
		#TODO: render to surface
		eve = stage.pack.eve.units
		units = gSurfaces[SURF_UNITS]
		xys = []
		for o in eve:
			y = o.y
			mag = gxEdit.magnification
			if y < stage.scroll*const.ENTITY_SCALE:
				continue
			if (y - stage.scroll*const.ENTITY_SCALE) * const.tileWidth2//2 * mag > gWindowHeight:	
				continue
			y -= stage.scroll*const.ENTITY_SCALE

			x = o.x
			if x < stage.hscroll*const.ENTITY_SCALE:
				continue
			if (x - stage.hscroll*const.ENTITY_SCALE) * const.tileWidth2//2 * mag > gWindowWidth:
				continue
			x -= stage.hscroll*const.ENTITY_SCALE

			dstx = x * (const.tileWidth2 // 2)
			dsty = y * (const.tileWidth2 // 2)

			x = o.type1 % 16 #row size in units.bmp
			y = o.type1 // 16
			srcx = x * const.tileWidth2
			srcy = y * const.tileWidth2

			srcrect = (srcx, srcy, const.tileWidth2, const.tileWidth2)
			dstrect = (int(dstx*mag), int(dsty*mag), int(const.tileWidth2//2*mag), int(const.tileWidth2//2*mag))

			self.renderer.copy(units, srcrect=srcrect, dstrect=dstrect)

			if o in stage.selectedEntities:
				self.drawBox(self.renderer, SURF_SDLCOLOR_CYAN, int(dstx*mag)-3, int(dsty*mag)-3, int(const.tileWidth2//2*mag)+4, int(const.tileWidth2//2*mag)+4, 2)
			else:
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
				self.drawBox(self.renderer, titleColor, int(dstx*mag), int(dsty*mag), int(const.tileWidth2//2*mag), int(const.tileWidth2//2*mag))

			if (dstx, dsty) in xys: #distinguish layered entities
				 self.renderer.copy(gSurfaces[SURF_COLOR_ORANGE_TRANSPARENT], dstrect=dstrect)

			if o.string:
				renderText(o.string, sdlColorWhite, TTF_STYLE_NORMAL, dstrect[0] + (const.tileWidth*mag), dstrect[1] + 2*mag)
			xys.append((dstx, dsty))
			
	def drawBox(self, renderer, surf, dstx, dsty, w, h, size=1):
		#mag = gxEdit.magnification
		gDrawBoxRect.x = dstx
		gDrawBoxRect.y = dsty
		gDrawBoxRect.w = size
		gDrawBoxRect.h = h
		sdl2.SDL_RenderCopy(renderer.sdlrenderer, gSurfaces[surf].texture, None, gDrawBoxRect)
		gDrawBoxRect.x = dstx
		gDrawBoxRect.y = dsty
		gDrawBoxRect.w = w
		gDrawBoxRect.h = size
		sdl2.SDL_RenderCopy(renderer.sdlrenderer, gSurfaces[surf].texture, None, gDrawBoxRect)
		gDrawBoxRect.x = dstx+w
		gDrawBoxRect.y = dsty
		gDrawBoxRect.w = size
		gDrawBoxRect.h = h
		sdl2.SDL_RenderCopy(renderer.sdlrenderer, gSurfaces[surf].texture, None, gDrawBoxRect)
		gDrawBoxRect.x = dstx
		gDrawBoxRect.y = dsty+h
		gDrawBoxRect.w = w+size #????????????????????
		gDrawBoxRect.h = size
		sdl2.SDL_RenderCopy(renderer.sdlrenderer, gSurfaces[surf].texture, None, gDrawBoxRect)
		return
		renderer.copy(gSurfaces[SURF_COLOR_GREEN], dstrect=dstrect1)
		renderer.copy(gSurfaces[SURF_COLOR_GREEN], dstrect=dstrect2)
		renderer.copy(gSurfaces[SURF_COLOR_GREEN], dstrect=dstrect3)
		renderer.copy(gSurfaces[SURF_COLOR_GREEN], dstrect=dstrect4)
	
	def drawBox2(self, renderer, rect, color):
		sdl2.SDL_SetRenderDrawColor(renderer.sdlrenderer, *color, 255)
		gDrawBoxRect.x,gDrawBoxRect.y,gDrawBoxRect.w,gDrawBoxRect.h = (*rect,)
		sdl2.SDL_RenderDrawRect(renderer.sdlrenderer, gDrawBoxRect)

	def renderMainBg(self, introAnimTimer, mouseover):
		windowBg = gSurfaces[SURF_WINDOWBG]
		windowBg2 = gSurfaces[SURF_WINDOWBG2]
		if introAnimTimer > 15 and introAnimTimer < 25 and introAnimTimer % 3 == 0 or introAnimTimer > 25:
			if mouseover:
				self.renderer.copy(windowBg, dstrect=(windowBg.x, windowBg.y, windowBg.size[0], windowBg.size[1]))
			else:
				self.renderer.copy(windowBg2, dstrect=(windowBg.x, windowBg.y, windowBg.size[0], windowBg.size[1]))

	def renderEditorBg(self):
		editorBg = gSurfaces[SURF_EDITORBG]
		for x in range(gWindowWidth // editorBg.size[0] + 1):
			for y in range(gWindowHeight // editorBg.size[1] + 1):
				self.renderer.copy(editorBg, dstrect=(x*editorBg.size[0], y*editorBg.size[1], editorBg.size[0], editorBg.size[1]))

	def renderBgColor(self, gxEdit, curStage):
		stage = curStage
		srcx = int(stage.hscroll * const.tileWidth)
		srcy = int(stage.scroll * const.tileWidth)

		sizex = min(gWindowWidth*max(1, int(1/gxEdit.magnification)), stage.surfaces[0].size[0], stage.surfaces[0].size[0] - srcx)
		sizey = min(gWindowHeight*max(1, int(1/gxEdit.magnification)), stage.surfaces[0].size[1], stage.surfaces[0].size[1] - srcy)

		#srcrect = (srcx, srcy, sizex, sizey)
		dstrect = (0, 0, int(sizex*gxEdit.magnification), int(sizey*gxEdit.magnification))

		color = sdl2.ext.Color(stage.pack.bg_r, stage.pack.bg_g, stage.pack.bg_b)
		self.renderer.fill(dstrect, color)
	

	def renderFade(self):
		pass

	def renderUIWindow(self, gxEdit, elem):
		#TODO
		windowsurf = gSurfaces[SURF_UIWINDOW]
		scale = 1
		if not elem.visible: return
		#TODO PLACEHOLDER AGAGHAGH
		if elem.type == const.WINDOW_TOOLTIP: return
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


	def fadeout(self, introAnimTimer):
		colorBlack = gSurfaces[SURF_COLOR_BLACK]
		window = self.window

		self.renderer.copy(colorBlack, dstrect=(0, gWindowHeight//2 + math.ceil(gWindowHeight * 0.05 * introAnimTimer), gWindowWidth, gWindowHeight))
		self.renderer.copy(colorBlack, dstrect=(0, -gWindowHeight//2 - math.ceil(gWindowHeight * 0.05 * introAnimTimer), gWindowWidth, gWindowHeight))
		self.renderer.copy(colorBlack, dstrect=(gWindowWidth//2 + math.ceil(gWindowWidth * 0.05 * introAnimTimer), 0, gWindowWidth, gWindowHeight))
		self.renderer.copy(colorBlack, dstrect=(-gWindowWidth//2 - math.ceil(gWindowWidth * 0.05 * introAnimTimer), 0, gWindowWidth, gWindowHeight))
	
	def fill(self):
		colorBlack = gSurfaces[SURF_COLOR_BLACK]
		window = self.window

		self.renderer.copy(colorBlack, dstrect=(0, 0, gWindowWidth, gWindowHeight))

	'''
	def clampMagnification(self):
		if self.magnification <= 0:
			self.magnification = 1
	'''

