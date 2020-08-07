import sdl2.ext
import const
import ctypes
import math
import interface
import util
import multi

#TODO: find a better place for this
class UndoAction:
	def __init__(self, action, reverse, forward):
		self.action = action
		self.reverse = reverse
		self.forward = forward

def runMouseWheel(stage, wheel):
	stage.scroll -= wheel.y


def runMouse1(gxEdit, stage, mouse):
	if mouse.button != sdl2.SDL_BUTTON_LEFT: return False

	map = stage.map
	eve = stage.eve
	mag = gxEdit.magnification

	for i, elem in reversed(list(gxEdit.elements.items())):
		if not elem.visible: continue

		if util.inWindowBoundingBox(mouse, elem):
			#move to top
			gxEdit.elements[i] = gxEdit.elements.pop(i)
			if elem.handleMouse1(mouse, gxEdit):
				return
		if util.inDragHitbox(mouse, elem):
			#move to top
			gxEdit.elements[i] = gxEdit.elements.pop(i)
			
			gxEdit.draggedElem = elem
			gxEdit.dragX = mouse.x - elem.x
			gxEdit.dragY = mouse.y - elem.y
			return

	#TODO: placeholder
	tilePalette = gxEdit.elements["tilePalette"]
	if tilePalette.visible and util.inWindowBoundingBox(mouse, tilePalette):
		#tile select
		x = (mouse.x - tilePalette.x - tilePalette.elements["picker"].x) // const.tileWidth // gxEdit.tilePaletteMag
		y = (mouse.y - tilePalette.y - tilePalette.elements["picker"].y) // const.tileWidth // gxEdit.tilePaletteMag

		if x >= stage.attr.width:
			return
		if y >= stage.attr.height:
			return

		if x < 0 or y < 0:
			return
		gxEdit.currentEditMode = const.EDIT_TILE
		stage.selectedTilesStart = [x, y]
		stage.selectedTilesEnd = [x, y]
		stage.selectedTiles = [[x, y]]

		stage.lastTileEdit = [None, None]
	tilePalette = gxEdit.elements["entityPalette"]
	if tilePalette.visible and util.inWindowBoundingBox(mouse, tilePalette):
		#entity select
		#TODO: add mag
		x = (mouse.x - tilePalette.x - tilePalette.elements["picker"].x) // const.tileWidth
		y = (mouse.y - tilePalette.y - tilePalette.elements["picker"].y) // const.tileWidth

		index = x + (y * 16)
		if index > const.entityFuncCount:
			return
		if index < 0:
			return
		gxEdit.currentEditMode = const.EDIT_ENTITY
		gxEdit.currentEntity = index

	elif gxEdit.currentEditMode == const.EDIT_ENTITY:
		x = int(mouse.x + (stage.hscroll * const.tileWidth * mag))
		y = int(mouse.y + (stage.scroll * const.tileWidth * mag))

		if stage.selectedEntities != []:
			xe = int(mouse.x // (const.tileWidth//2 * mag)) + stage.hscroll*2
			ye = int(mouse.y // (const.tileWidth//2 * mag)) + stage.scroll*2
			for o in stage.selectedEntities:
				if o.x == xe and o.y == ye:
					gxEdit.draggingEntities = True
					gxEdit.entDragPos = [xe, ye]
					return
		gxEdit.selectionBoxStart = [x, y]
		gxEdit.selectionBoxEnd = [x, y]

def runMouseUp(gxEdit, curStage, mouse):
	if mouse.button != sdl2.SDL_BUTTON_LEFT: return False

	if gxEdit.currentEditMode == const.EDIT_ENTITY:
		gxEdit.selectionBoxStart = [-1, -1]
		gxEdit.selectionBoxEnd = [-1, -1]
		gxEdit.draggingEntities = False

	for i, elem in reversed(list(gxEdit.elements.items())):
		if elem.activeElem:
			if(elem.activeElem.handleMouse1Up(mouse, gxEdit)):
				elem.activeElem = None
			return


def runMouseDrag(gxEdit, stage):			
	#it just works
	mouse = sdl2.SDL_MouseButtonEvent()
	x,y = ctypes.c_int(0), ctypes.c_int(0)
	mouse.button = sdl2.SDL_GetMouseState(x, y)
	mouse.x, mouse.y = x.value, y.value

	for i, elem in reversed(list(gxEdit.elements.items())):
		if not elem.visible: continue

		if util.inWindowBoundingBox(mouse, elem):
			if elem.handleMouseOver(mouse, gxEdit):
				break

	if (mouse.button != sdl2.SDL_BUTTON_LEFT): return False

	map = stage.map
	mag = gxEdit.magnification

	tileEndX = int(const.tileWidth * mag * map.width)

	if gxEdit.draggedElem:
		gxEdit.draggedElem.x = mouse.x - gxEdit.dragX
		gxEdit.draggedElem.y = mouse.y - gxEdit.dragY
		return
	
	for _, elem in gxEdit.elements.items():
		if not elem.visible: continue
		if util.inBoundingBox(mouse.x, mouse.y, elem.x, elem.y, elem.w, elem.h):
			if gxEdit.draggedElem:
				return
			if elem.type != const.WINDOW_TILEPALETTE and elem.type != const.WINDOW_TOOLTIP:
				return

	tilePalette = gxEdit.elements["tilePalette"]
	#Tiles selection
	if util.inWindowBoundingBox(mouse, tilePalette):
		x = (mouse.x - tilePalette.x - tilePalette.elements["picker"].x) // const.tileWidth // gxEdit.tilePaletteMag
		y = (mouse.y - tilePalette.y - tilePalette.elements["picker"].y) // const.tileWidth // gxEdit.tilePaletteMag

		if x < 0 or y < 0:
			return
		if x >= stage.attr.width:
			return
		if y >= stage.attr.height:
			return
		stage.selectedTilesEnd = [x, y]

	#tiles Paint
	elif gxEdit.currentEditMode == const.EDIT_TILE:

		x = int(mouse.x // (const.tileWidth * mag) + stage.hscroll)
		y = int(mouse.y // (const.tileWidth * mag) + stage.scroll)

		if x >= map.width or y >= map.height:
			return

		if stage.lastTileEdit == [x, y]:
			return
		stage.lastTileEdit = [x, y]

		startX = stage.selectedTilesStart[0]
		startY = stage.selectedTilesStart[1]
		tiles = []
		oldTiles = []
		for tile in stage.selectedTiles:
			xx = tile[0] - startX + x
			yy = tile[1] - startY + y

			if xx >= map.width or yy >= map.height: 
				continue

			tiles.append([[xx,yy], [tile[0], tile[1]]])

			oldTileX = map.tiles[yy][xx] % 16
			oldTileY = map.tiles[yy][xx] // 16

			oldTiles.append([[xx,yy], [oldTileX, oldTileY]])

		if gxEdit.multiplayerState == const.MULTIPLAYER_CLIENT:
			multi.sendTileEditPacket(gxEdit, gxEdit.curStage, tiles)
			return
		if gxEdit.multiplayerState == const.MULTIPLAYER_HOST:
			multi.serverSendTileEdit(gxEdit, gxEdit.curStage, tiles)
		for pos, tile in tiles:
			stage.renderTileToSurface(pos[0], pos[1], tile[0],
											tile[1])
		map.modify(tiles)
		#TODO: disable undo while dragging
		#TODO: commit undo action only when mouseup
		undo = UndoAction(const.UNDO_TILE, oldTiles, tiles)

		stage.undoPos += 1
		stage.undoStack = stage.undoStack[:stage.undoPos]
		stage.undoStack.append(undo)
		
	elif gxEdit.currentEditMode == const.EDIT_ENTITY:
		x = int(mouse.x + (stage.hscroll * const.tileWidth * mag))
		y = int(mouse.y + (stage.scroll * const.tileWidth * mag))
		scale = (const.tileWidth//2 * mag)

		if gxEdit.draggingEntities:
			x = int((mouse.x // scale) + stage.hscroll*2)
			y = int((mouse.y // scale) + stage.scroll*2)

			xe = gxEdit.entDragPos[0]
			ye = gxEdit.entDragPos[1]

			
			for o in stage.selectedEntities:
				if o.x + x-xe < 0: return
				if o.y + y-ye < 0: return
				if o.x + x-xe > (stage.map.width * 2)-1: return
				if o.y + y-ye > (stage.map.height * 2)-1: return
			gxEdit.entDragPos = [x, y]

			ids = [o.id for o in stage.selectedEntities]
			stage.eve.move(ids, x-xe, y-ye)
			return

		x1 = int(gxEdit.selectionBoxStart[0] // scale)
		y1 = int(gxEdit.selectionBoxStart[1] // scale)

		x2 = int(gxEdit.selectionBoxEnd[0] // scale)
		y2 = int(gxEdit.selectionBoxEnd[1] // scale)

		if x1 > x2: x1, x2 = x2, x1
		if y1 > y2: y1, y2 = y2, y1

		#if x1 > map.width*2 or y1 > map.height*2: return
		#if x2 > map.width*2 or y2 > map.height*2: return

		#if x > int(map.width*const.tileWidth*mag)
		gxEdit.selectionBoxEnd = [x, y]
		
		selectedEntities = []
		for o in stage.eve.get():
			#if o.x > x2 or o.y > y2: continue

			if o.x >= x1 and o.y >= y1 \
				and o.x <= x2 and o.y <= y2:
				selectedEntities.append(o)
		stage.selectedEntities = selectedEntities
		if selectedEntities == []:
			gxEdit.elements["entEdit"].visible = False
		else:
			elem = gxEdit.elements["entEdit"]
			if len(selectedEntities) == 1:
				elem.elements["paramEdit"].text = str(selectedEntities[0].type2)
			else:
				elem.elements["paramEdit"].text = ""
				elem.elements["paramEdit"].placeholderText = "\n\n\n\n"
			elem.visible = True
			elem.x = int((selectedEntities[0].x - (stage.hscroll*2))* (const.tileWidth // 2) * mag + const.tileWidth*2)
			elem.y = int((selectedEntities[0].y - (stage.scroll*2))* (const.tileWidth // 2) * mag)
			#gxEdit.focussedElem = elem.elements["paramEdit"]
			
			
				


					
def runMouse2(gxEdit, stage, mouse):
	if (mouse.button != sdl2.SDL_BUTTON_RIGHT): return False

	mag = gxEdit.magnification

	if gxEdit.currentEditMode == const.EDIT_ENTITY:
		x = int(mouse.x / (const.tileWidth/2 * mag)) + stage.hscroll*2
		y = int(mouse.y / (const.tileWidth/2 * mag)) + stage.scroll*2
		x = math.floor(x) 
		y = math.floor(y)

		for o in stage.eve.get():
			if o.x == x and o.y == y:
				stage.eve.remove([o.id])
				return

def runKeyboard(gxEdit, stage, scaleFactor, key):
	sym = key.keysym.sym

	#todo: when focussed elem do not do things you can type
	
	if sym == sdl2.SDLK_j:
		gxEdit.curStage -= 1
	elif sym == sdl2.SDLK_k:
		gxEdit.curStage += 1

	elif sym == sdl2.SDLK_LEFT:
		stage.hscroll -= 1
	elif sym == sdl2.SDLK_RIGHT:
		stage.hscroll += 1
	elif sym == sdl2.SDLK_DOWN:
		stage.scroll += 1
	elif sym == sdl2.SDLK_UP:
		stage.scroll -= 1
	elif sym == sdl2.SDLK_HOME:
		stage.scroll = 0
	elif sym == sdl2.SDLK_END:
		stage.scroll = stage.map.height - scaleFactor
	elif sym == sdl2.SDLK_PAGEDOWN:
		stage.scroll += int(scaleFactor // 1.5)
	elif sym == sdl2.SDLK_PAGEUP:
		stage.scroll -= int(scaleFactor // 1.5)
	elif sym == sdl2.SDLK_MINUS:
		if gxEdit.magnification == 1:
			gxEdit.magnification = 0.5
		else:
			gxEdit.magnification -= 1
	elif sym == sdl2.SDLK_EQUALS:
		if gxEdit.magnification == 0.5:
			gxEdit.magnification = 1
		else:
			gxEdit.magnification += 1

	elif sym == sdl2.SDLK_LEFTBRACKET:
		gxEdit.tilePaletteMag -= 1

	elif sym == sdl2.SDLK_RIGHTBRACKET:
		gxEdit.tilePaletteMag += 1

	elif sym == sdl2.SDLK_QUOTE:
		gxEdit.entityPaletteMag -= 1

	elif sym == sdl2.SDLK_BACKSLASH:
		gxEdit.entityPaletteMag += 1

	elif sym == sdl2.SDLK_BACKSPACE:
		if gxEdit.focussedElem:
			gxEdit.focussedElem.text = gxEdit.focussedElem.text[:-1]
			if gxEdit.focussedElem.onAction:
				gxEdit.focussedElem.onAction(gxEdit.focussedElem, gxEdit)
	elif sym == sdl2.SDLK_i:
		if gxEdit.currentEditMode == const.EDIT_ENTITY:
			#entity place
			mouse = sdl2.SDL_MouseButtonEvent()
			x,y = ctypes.c_int(0), ctypes.c_int(0)
			mouse.button = sdl2.SDL_GetMouseState(x, y)
			mouse.x, mouse.y = x.value, y.value
			mag = gxEdit.magnification

			x = int(mouse.x // (const.tileWidth//2 * mag)) + stage.hscroll*2
			y = int(mouse.y // (const.tileWidth//2 * mag)) + stage.scroll*2
			if x >= stage.map.width*2 or y >= stage.map.height*2:
				return

			stage.eve.add(x, y, gxEdit.currentEntity, 0)
	elif sym == sdl2.SDLK_DELETE:
		if stage.selectedEntities:
			ids = [o.id for o in stage.selectedEntities]
			stage.eve.remove(ids)
			gxEdit.elements["entEdit"].visible = False

	elif key.keysym.mod & sdl2.KMOD_CTRL:
		if sym == sdl2.SDLK_d:
			#scrambleEntities(stage)
			pass
	
		elif sym == sdl2.SDLK_s:
			#TODO: show flash on save (goodly)
			if stage.save():
				gxEdit.saveTimer = 5

		elif sym == sdl2.SDLK_z:
			gxEdit.executeUndo()

		elif sym == sdl2.SDLK_y:
			gxEdit.executeRedo()

		elif sym == sdl2.SDLK_v:
			if gxEdit.focussedElem:
				text = sdl2.SDL_GetClipboardText()
				gxEdit.focussedElem.handleTextInput(text.decode("utf-8"), gxEdit)



	elif sym == sdl2.SDLK_F11:
		gxEdit.fullscreen ^= 1

		if not gxEdit.fullscreen:
			sdl2.SDL_SetWindowFullscreen(interface.gWindow.window, sdl2.SDL_WINDOW_FULLSCREEN_DESKTOP)
		else:
			sdl2.SDL_SetWindowFullscreen(interface.gWindow.window, 0)

	#e = toggle entity palette
	#t = toggle tile palette

	#elif sym == sdl2.SDLK_r:
	#	stage.renderTilesToSurface()
			