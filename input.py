import sdl2.ext
import const
import ctypes
import math
import interface
import util
import multi

import copy

#TODO: find a better place for this
class UndoAction:
	def __init__(self, action, reverse, forward, param=None):
		self.action = action
		self.reverse = copy.deepcopy(reverse)
		self.forward = copy.deepcopy(forward)
		self.param = param

def runMouseWheel(stage, wheel):
	stage.scroll -= wheel.y


def runMouse1(gxEdit, stage, mouse):
	if mouse.button != sdl2.SDL_BUTTON_LEFT: return False

	map = stage.pack.layers[gxEdit.currentLayer]
	eve = stage.pack.eve.units

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
		
		if x >= stage.attrs[gxEdit.currentLayer].width:
			return
		if y >= stage.attrs[gxEdit.currentLayer].height:
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
		x = (mouse.x - tilePalette.x - tilePalette.elements["picker"].x) // const.tileWidth2
		y = (mouse.y - tilePalette.y - tilePalette.elements["picker"].y) // const.tileWidth2

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
			xe = int(mouse.x // (const.tileWidth2//2 * mag)) + stage.hscroll*const.ENTITY_SCALE
			ye = int(mouse.y // (const.tileWidth2//2 * mag)) + stage.scroll*const.ENTITY_SCALE
			for o in stage.selectedEntities:
				if o.x == xe and o.y == ye:
					gxEdit.draggingEntities = True
					gxEdit.entDragPos = [xe, ye]

					stage.selectedEntitiesDragStart = copy.deepcopy(stage.selectedEntities)
					return
		gxEdit.selectionBoxStart = [x, y]
		gxEdit.selectionBoxEnd = [x, y]

def runMouse3(gxEdit, stage, mouse):
	if mouse.button != sdl2.SDL_BUTTON_MIDDLE: return False

	map = stage.pack.layers[gxEdit.currentLayer]
	eve = stage.pack.eve.units

	mag = gxEdit.magnification

	if gxEdit.currentEditMode == const.EDIT_TILE:
		if not len(map.tiles): return
		x = int(mouse.x // (const.tileWidth * mag) + stage.hscroll)
		y = int(mouse.y // (const.tileWidth * mag) + stage.scroll)

		if x >= map.width or y >= map.height:
			return
	# pick block
	#TODO: this should eventually be quick copy paste

	xx = map.tiles[y][x] % 16
	yy = map.tiles[y][x] // 16
	stage.selectedTilesStart = [xx, yy]	
	stage.selectedTilesEnd = [xx, yy]



def runMouseUp(gxEdit, curStage, mouse):
	if mouse.button != sdl2.SDL_BUTTON_LEFT: return False

	if gxEdit.currentEditMode == const.EDIT_ENTITY:
		gxEdit.selectionBoxStart = [-1, -1]
		gxEdit.selectionBoxEnd = [-1, -1]
		if gxEdit.draggingEntities:
			gxEdit.draggingEntities = False

			stage = gxEdit.stages[gxEdit.curStage]
			undo = UndoAction(const.UNDO_ENTITY_MOVE, stage.selectedEntitiesDragStart, stage.selectedEntities)
			stage.addUndo(undo)

	for i, elem in reversed(list(gxEdit.elements.items())):
		if gxEdit.activeElem:
			if(gxEdit.activeElem.handleMouse1Up(mouse, gxEdit)):
				gxEdit.activeElem = None
			return


def runMouseDrag(gxEdit, stage):			
	mouse = util.getMouseState()

	for i, elem in reversed(list(gxEdit.elements.items())):
		if not elem.visible: continue

		if util.inWindowBoundingBox(mouse, elem):
			if elem.handleMouseOver(mouse, gxEdit):
				break
	else:
		gxEdit.tooltipText = []
	
	keystate = util.getKeyState()
	if (mouse.button != sdl2.SDL_BUTTON_LEFT and not keystate[sdl2.SDL_SCANCODE_SPACE]): return False

	map = stage.pack.layers[gxEdit.currentLayer]
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
		if x >= stage.attrs[gxEdit.currentLayer].width:
			return
		if y >= stage.attrs[gxEdit.currentLayer].height:
			return
		stage.selectedTilesEnd = [x, y]

	#tiles Paint
	elif gxEdit.currentEditMode == const.EDIT_TILE:
		if not len(map.tiles): return
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
											tile[1], gxEdit.currentLayer)
		map.modify(tiles)
		#TODO: disable undo while dragging
		#TODO: commit undo action only when mouseup
		undo = UndoAction(const.UNDO_TILE, oldTiles, tiles, gxEdit.currentLayer)
		stage.addUndo(undo)
		
	elif gxEdit.currentEditMode == const.EDIT_ENTITY:
		x = int(mouse.x + (stage.hscroll * const.tileWidth * mag))
		y = int(mouse.y + (stage.scroll * const.tileWidth * mag))
		scale = (const.tileWidth2//2 * mag)

		if gxEdit.draggingEntities:
			x = int((mouse.x // scale) + stage.hscroll*const.ENTITY_SCALE)
			y = int((mouse.y // scale) + stage.scroll*const.ENTITY_SCALE)

			xe = gxEdit.entDragPos[0]
			ye = gxEdit.entDragPos[1]
			
			for o in stage.selectedEntities:
				if o.x + x-xe < 0: return
				if o.y + y-ye < 0: return
				if o.x + x-xe > (stage.pack.layers[0].width * const.ENTITY_SCALE)-1: return
				if o.y + y-ye > (stage.pack.layers[0].height * const.ENTITY_SCALE)-1: return
			gxEdit.entDragPos = [x, y]

			ids = [o.id for o in stage.selectedEntities]
			stage.pack.eve.move(ids, x-xe, y-ye)
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
		for o in stage.pack.eve.units:
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
				elem.elements["flagEdit"].text = str(selectedEntities[0].flag)
				elem.elements["dirEdit"].text = str(selectedEntities[0].param2)
				elem.elements["bitsEdit"].text = str(selectedEntities[0].bits)
				elem.elements["stringEdit"].text = str(selectedEntities[0].string)
				elem.elements["stringEdit"].placeholderText = ""
				pass
				#elem.elements["paramEdit"].text = str(selectedEntities[0].type2)
			else:
				for _,e in elem.elements.items():
					if isinstance(e, interface.UITextInput):
						e.text = ""
						e.placeholderText = "\n\n\n\n"

			elem.visible = True
			elem.x = int((selectedEntities[0].x - (stage.hscroll*const.ENTITY_SCALE))* (const.tileWidth2 // 2) * mag + const.tileWidth2*2)
			elem.y = int((selectedEntities[0].y - (stage.scroll*const.ENTITY_SCALE))* (const.tileWidth2 // 2) * mag)
			#gxEdit.focussedElem = elem.elements["paramEdit"]

			#TODO: scroll into view for expanded entity list
			gxEdit.currentEntity = selectedEntities[0].type1
			

					
def runMouse2(gxEdit, stage, mouse):
	if (mouse.button != sdl2.SDL_BUTTON_RIGHT): return False

	mag = gxEdit.magnification

	if gxEdit.currentEditMode == const.EDIT_ENTITY:
		x = int(mouse.x / (const.tileWidth2/2 * mag)) + stage.hscroll*const.ENTITY_SCALE
		y = int(mouse.y / (const.tileWidth2/2 * mag)) + stage.scroll*const.ENTITY_SCALE
		x = math.floor(x) 
		y = math.floor(y)

		for o in stage.pack.eve.units:
			if o.x == x and o.y == y:
				stage.pack.eve.remove([o.id])

				undo = UndoAction(const.UNDO_ENTITY_REMOVE, 0, [o])
				stage.addUndo(undo)
				gxEdit.elements["entEdit"].visible = False
				return

def runKeyboard(gxEdit, stage, scaleFactor, key):
	sym = key.keysym.sym
	#todo: when focussed elem do not do things you can type
	
	if sym == sdl2.SDLK_j:
		gxEdit.curStage -= 1
	elif sym == sdl2.SDLK_k:
		gxEdit.curStage += 1

	#window shortcuts
	elif sym == sdl2.SDLK_e:
		interface.toggleEntityPalette(0,0,gxEdit)
	elif sym == sdl2.SDLK_r:
		interface.toggleTilePalette(0,0,gxEdit)

	#field shortcut transportation
	elif sym == sdl2.SDLK_t:
		gxEdit.loadStage(stage.pack.up_field)
		gxEdit.curStage+=1
	elif sym == sdl2.SDLK_f:
		gxEdit.loadStage(stage.pack.left_field)
		gxEdit.curStage+=1
	elif sym == sdl2.SDLK_g:
		gxEdit.loadStage(stage.pack.down_field)
		gxEdit.curStage+=1
	elif sym == sdl2.SDLK_h:
		gxEdit.loadStage(stage.pack.right_field)
		gxEdit.curStage+=1
	
	#keyboard navigation tile selection
	elif sym == sdl2.SDLK_a:
		if not key.keysym.mod & sdl2.KMOD_SHIFT:
			stage.selectedTilesStart[0] -= 1
		if not key.keysym.mod & sdl2.KMOD_ALT:
			stage.selectedTilesEnd[0] -= 1
		stage.lastTileEdit = [None, None]
	elif sym == sdl2.SDLK_d:
		if not key.keysym.mod & sdl2.KMOD_SHIFT:
			stage.selectedTilesStart[0] += 1
		if not key.keysym.mod & sdl2.KMOD_ALT:
			stage.selectedTilesEnd[0] += 1
		stage.lastTileEdit = [None, None]
	elif sym == sdl2.SDLK_w:
		if not key.keysym.mod & sdl2.KMOD_SHIFT:
			stage.selectedTilesStart[1] -= 1
		if not key.keysym.mod & sdl2.KMOD_ALT:
			stage.selectedTilesEnd[1] -= 1
		stage.lastTileEdit = [None, None]
	elif sym == sdl2.SDLK_s:
		if not key.keysym.mod & sdl2.KMOD_SHIFT:
			stage.selectedTilesStart[1] += 1
		if not key.keysym.mod & sdl2.KMOD_ALT:
			stage.selectedTilesEnd[1] += 1
		stage.lastTileEdit = [None, None]

	#keyboard navigation mouse movement
	elif sym == sdl2.SDLK_KP_8:
		mouse = util.getMouseState()
		sdl2.SDL_WarpMouseInWindow(None, mouse.x, int(mouse.y-const.tileWidth*gxEdit.magnification))
	elif sym == sdl2.SDLK_KP_4:
		mouse = util.getMouseState()
		sdl2.SDL_WarpMouseInWindow(None,  int(mouse.x-const.tileWidth*gxEdit.magnification), mouse.y)
	elif sym == sdl2.SDLK_KP_5:
		mouse = util.getMouseState()
		sdl2.SDL_WarpMouseInWindow(None, mouse.x,  int(mouse.y+const.tileWidth*gxEdit.magnification))
	elif sym == sdl2.SDLK_KP_6:
		mouse = util.getMouseState()
		sdl2.SDL_WarpMouseInWindow(None,  int(mouse.x+const.tileWidth*gxEdit.magnification), mouse.y)

	#keyboard navigation scroll
	elif sym == sdl2.SDLK_LEFT:
		stage.hscroll -= 2
	elif sym == sdl2.SDLK_RIGHT:
		stage.hscroll += 2
	elif sym == sdl2.SDLK_DOWN:
		stage.scroll += 2
	elif sym == sdl2.SDLK_UP:
		stage.scroll -= 2
	elif sym == sdl2.SDLK_HOME:
		stage.scroll = 0
	elif sym == sdl2.SDLK_END:
		stage.scroll = stage.pack.layers[0].height - scaleFactor
	elif sym == sdl2.SDLK_PAGEDOWN:
		stage.scroll += int(scaleFactor // 1.5)
	elif sym == sdl2.SDLK_PAGEUP:
		stage.scroll -= int(scaleFactor // 1.5)

	#keyboard navigation zoom
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

	#layer switch
	elif sym == sdl2.SDLK_COMMA:
		gxEdit.currentLayer -= 1
		if gxEdit.currentLayer < 0: gxEdit.currentLayer = 0

	elif sym == sdl2.SDLK_PERIOD:
		gxEdit.currentLayer += 1
		if gxEdit.currentLayer > 2: gxEdit.currentLayer = 2

	elif sym == sdl2.SDLK_BACKSPACE:
		if gxEdit.focussedElem:
			gxEdit.focussedElem.text = gxEdit.focussedElem.text[:-1]
			if gxEdit.focussedElem.onAction:
				gxEdit.focussedElem.onAction(gxEdit.focussedElem, gxEdit)

	#entity manipulation
	elif sym == sdl2.SDLK_i:
		if gxEdit.currentEditMode == const.EDIT_ENTITY:
			mouse = util.getMouseState()
			mag = gxEdit.magnification

			x = int(mouse.x // (const.tileWidth//const.ENTITY_SCALE * mag)) + stage.hscroll* const.ENTITY_SCALE
			y = int(mouse.y // (const.tileWidth//const.ENTITY_SCALE * mag)) + stage.scroll* const.ENTITY_SCALE
			if x >= stage.pack.layers[0].width*const.ENTITY_SCALE or y >= stage.pack.layers[0].height*const.ENTITY_SCALE:
				return

			o = stage.pack.eve.add(x, y, gxEdit.currentEntity)

			undo = UndoAction(const.UNDO_ENTITY_ADD, 0, [o])
			stage.addUndo(undo)

	elif sym == sdl2.SDLK_DELETE:
		if stage.selectedEntities:
			ids = [o.id for o in stage.selectedEntities]
			stage.pack.eve.remove(ids)
			gxEdit.elements["entEdit"].visible = False

			undo = UndoAction(const.UNDO_ENTITY_REMOVE, 0, stage.selectedEntities)
			stage.addUndo(undo)

			stage.selectedEntities = []


	elif key.keysym.mod & sdl2.KMOD_CTRL:

		if sym == sdl2.SDLK_s:
			#TODO: show flash on save (goodly)
			if stage.save():
				gxEdit.saveTimer = 5

		elif sym == sdl2.SDLK_z:
			if key.keysym.mod & sdl2.KMOD_SHIFT:
				gxEdit.executeRedo()
			else:
				gxEdit.executeUndo()

		elif sym == sdl2.SDLK_y:
			gxEdit.executeRedo()

		elif sym == sdl2.SDLK_c:
			if stage.selectedEntities:
				gxEdit.copiedEntities = copy.deepcopy(stage.selectedEntities)
				basex = min([o.x for o in gxEdit.copiedEntities])
				basey = min([o.y for o in gxEdit.copiedEntities])

				for o in gxEdit.copiedEntities:
					o.x -= basex
					o.y -= basey
		
		elif sym == sdl2.SDLK_v:
			if gxEdit.focussedElem:
				text = sdl2.SDL_GetClipboardText()
				gxEdit.focussedElem.handleTextInput(text.decode("utf-8"), gxEdit)
			else:
				mouse = util.getMouseState()

				scale = (const.tileWidth//const.ENTITY_SCALE * gxEdit.magnification)
				x = int((mouse.x // scale) + stage.hscroll*const.ENTITY_SCALE)
				y = int((mouse.y // scale) + stage.scroll*const.ENTITY_SCALE)

				#todo print Paste failed!
				for o in gxEdit.copiedEntities:
					if o.x + x < 0: return
					if o.y + y < 0: return
					if o.x + x > (stage.pack.layers[0].width * const.ENTITY_SCALE)-1: return
					if o.y + y > (stage.pack.layers[0].height * const.ENTITY_SCALE)-1: return

				ents = []
				for o in gxEdit.copiedEntities:
					o2 = copy.deepcopy(o)
					o2.id = stage.pack.eve._count
					o2.x += x
					o2.y += y
					stage.pack.eve._count += 1
					stage.pack.eve.units.append(o2)
					ents.append(o2)

				undo = UndoAction(const.UNDO_ENTITY_ADD, 0, ents)
				stage.addUndo(undo)


	elif sym == sdl2.SDLK_F11:
		gxEdit.fullscreen ^= 1

		if not gxEdit.fullscreen:
			sdl2.SDL_SetWindowFullscreen(interface.gWindow.window, sdl2.SDL_WINDOW_FULLSCREEN_DESKTOP)
		else:
			sdl2.SDL_SetWindowFullscreen(interface.gWindow.window, 0)