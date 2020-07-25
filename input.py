import sdl2.ext
import const
import ctypes
import math
import interface
import util

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

	for i, elem in reversed(list(enumerate(gxEdit.elements))):
		if not elem.visible: continue

		if util.inWindowBoundingBox(mouse, elem):
			#move to top
			gxEdit.elements.append(gxEdit.elements.pop(i))
			if elem.handleMouse1(mouse, gxEdit):
				return
		if util.inDragHitbox(mouse, elem):
			#move to top
			gxEdit.elements.append(gxEdit.elements.pop(i))
			
			gxEdit.draggedElem = elem
			gxEdit.dragX = mouse.x - elem.x
			gxEdit.dragY = mouse.y - elem.y
			return

	#TODO: placeholder
	tilePalette = None
	for elem in gxEdit.elements:
		if elem.type == const.WINDOW_TILEPALETTE:
			tilePalette = elem
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
	tilePalette = None
	for elem in gxEdit.elements:
		if elem.type == const.WINDOW_ENTITYPALETTE:
			tilePalette = elem
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
		gxEdit.selectedEntity = index

	elif gxEdit.currentEditMode == const.EDIT_ENTITY:
		#entity place
		x = int(mouse.x // (const.tileWidth//2 * mag)) + stage.hscroll*2
		y = int(mouse.y // (const.tileWidth//2 * mag)) + stage.scroll*2

		if x >= map.width*2 or y >= map.height*2:
			return

		eve.add(x, y, gxEdit.selectedEntity, 0)

def runMouseUp(gxEdit, curStage, mouse):
	if mouse.button != sdl2.SDL_BUTTON_LEFT: return False

	for i, elem in reversed(list(enumerate(gxEdit.elements))):
		if elem.activeElem:
			if(elem.activeElem.handleMouse1Up(mouse, gxEdit)):
				elem.activeElem = None
			return

	#for i, elem in reversed(list(enumerate(gxEdit.elements))):
	#	if util.inWindowBoundingBox(mouse, elem):
	#		#move to top
	#		gxEdit.elements.append(gxEdit.elements.pop(i))
	#		if elem.handleMouse1Up(mouse, gxEdit):
	#			return


def runMouseDrag(gxEdit, stage):			
	#it just works
	mouse = sdl2.SDL_MouseButtonEvent()
	x,y = ctypes.c_int(0), ctypes.c_int(0)
	mouse.button = sdl2.SDL_GetMouseState(x, y)
	mouse.x, mouse.y = x.value, y.value

	for i, elem in reversed(list(enumerate(gxEdit.elements))):
		if not elem.visible: continue

		if util.inWindowBoundingBox(mouse, elem):
			#move to top
			gxEdit.elements.append(gxEdit.elements.pop(i))
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
	
	for elem in gxEdit.elements:
		if util.inBoundingBox(mouse.x, mouse.y, elem.x, elem.y, elem.w, elem.h):
			if gxEdit.draggedElem:
				return

	tilePalette = None
	for elem in gxEdit.elements:
		if elem.type == const.WINDOW_TILEPALETTE:
			tilePalette = elem

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

		x = int(mouse.x // (const.tileWidth * mag)) + stage.hscroll
		y = int(mouse.y // (const.tileWidth * mag)) + stage.scroll

		if x >= map.width or y >= map.height:
			return

		#TODO make this obsolete
		if len(stage.selectedTiles) == 1:
			#don't modify if same
			if stage.lastTileEdit == [x, y]:
				return
			stage.lastTileEdit = [x, y]

			index = x + (y * map.width)

			oldTileX = map.tiles[index] % 16
			oldTileY = map.tiles[index] // 16
			oldTiles = [[index, [oldTileX, oldTileY]]] 

			map.modify( [[index, stage.selectedTiles[0]]] )
			stage.renderTileToSurface(x, y, stage.selectedTiles[0][0],
											stage.selectedTiles[0][1])

			undo = UndoAction(const.UNDO_TILE, oldTiles, [[index, stage.selectedTiles[0]]])
		
			stage.undoPos += 1
			stage.undoStack = stage.undoStack[:stage.undoPos]
			stage.undoStack.append(undo)
			
		else:
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

				index = xx + (yy * map.width)
				tiles.append([index, [tile[0], tile[1]]])

				oldTileX = map.tiles[index] % 16
				oldTileY = map.tiles[index] // 16
				oldTiles.append([index, [oldTileX, oldTileY]])

			for index, tile in tiles:
				x = index % map.width
				y = index // map.width
				stage.renderTileToSurface(x, y, tile[0],
												tile[1])
			map.modify(tiles)
			#TODO: disable undo while dragging
			#TODO: commit undo action only when mouseup
			undo = UndoAction(const.UNDO_TILE, oldTiles, tiles)

			stage.undoPos += 1
			stage.undoStack = stage.undoStack[:stage.undoPos]
			stage.undoStack.append(undo)
			

					
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

	elif sym == sdl2.SDLK_F11:
		gxEdit.fullscreen ^= 1

		if not gxEdit.fullscreen:
			sdl2.SDL_SetWindowFullscreen(interface.gWindow.window, sdl2.SDL_WINDOW_FULLSCREEN_DESKTOP)
		else:
			sdl2.SDL_SetWindowFullscreen(interface.gWindow.window, 0)

	#e = toggle entity palette
	#t = toggle tile palette

	elif sym == sdl2.SDLK_r:
		stage.renderTilesToSurface()
			