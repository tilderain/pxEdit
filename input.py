import os
os.environ["PYSDL2_DLL_PATH"] = "./"
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
		gxEdit.tileSelectionUpdate = True
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
	else:
		return
	# pick block
	#TODO: this should eventually be quick copy paste

	xx = map.tiles[y][x] % 16
	yy = map.tiles[y][x] // 16
	stage.selectedTilesStart = [xx, yy]	
	stage.selectedTilesEnd = [xx, yy]
	gxEdit.tileSelectionUpdate = True



def runMouseUp(gxEdit, curStage, mouse):
	if mouse.button != sdl2.SDL_BUTTON_LEFT: return False

	for i, elem in reversed(list(gxEdit.elements.items())):
		if gxEdit.activeElem:
			if(gxEdit.activeElem.handleMouse1Up(mouse, gxEdit)):
				gxEdit.activeElem = None
			return
	if gxEdit.currentEditMode == const.EDIT_ENTITY:
		gxEdit.selectionBoxStart = [-1, -1]
		gxEdit.selectionBoxEnd = [-1, -1]
		if gxEdit.draggingEntities:
			gxEdit.draggingEntities = False

			stage = gxEdit.stages[gxEdit.curStage]
			undo = UndoAction(const.UNDO_ENTITY_MOVE, stage.selectedEntitiesDragStart, stage.selectedEntities)
			stage.addUndo(undo)
	elif gxEdit.currentEditMode == const.EDIT_TILE and gxEdit.rectanglePaintBoxStart != [-1, -1]:
		map = curStage.pack.layers[gxEdit.currentLayer]
		if not len(map.tiles): return

		curStage.lastTileEdit == [-1, -1]

		if gxEdit.tileHighlightAnimate:
			gxEdit.tileHighlightTimer = 120

		start = gxEdit.rectanglePaintBoxStart[:]
		end = gxEdit.rectanglePaintBoxEnd[:]
		start2 = curStage.selectedTilesStart[:]
		end2 = curStage.selectedTilesEnd[:]

		if start[0] > end[0]:
			start[0], end[0] = end[0], start[0]
		if end[1] < start[1]:
			start[1], end[1] = end[1], start[1]
		if start2[0] > end2[0]:
			start2[0], end2[0] = end2[0], start2[0]
		if end2[1] < start2[1]:
			start2[1], end2[1] = end2[1], start2[1]
		startX = curStage.selectedTilesStart[0]
		startY = curStage.selectedTilesStart[1]
		tiles = []
		oldTiles = []

		width = end[0] - start[0] + 1
		height = end[1] - start[1] + 1

		w2 = end2[0] - start2[0] + 1
		for y in range(height):
			for x in range(width):
				tile = curStage.selectedTiles[((x % w2) + (y*w2)) % len(curStage.selectedTiles)]
				xx = x + start[0]
				yy = y + start[1]
				if xx >= map.width or yy >= map.height: 
					continue

				tiles.append([[xx,yy], [tile[0], tile[1]]])

				oldTileX = map.tiles[yy][xx] % 16
				oldTileY = map.tiles[yy][xx] // 16

				oldTiles.append([[xx,yy], [oldTileX, oldTileY]])

		if gxEdit.multiplayerState == const.MULTIPLAYER_CLIENT:
			multi.sendTileEditPacket(gxEdit, gxEdit.curStage, tiles, gxEdit.currentLayer)
			return
		if gxEdit.multiplayerState == const.MULTIPLAYER_HOST:
			multi.serverSendTileEdit(gxEdit, gxEdit.curStage, tiles, gxEdit.currentLayer)
		for pos, tile in tiles:
			curStage.renderTileToSurface(pos[0], pos[1], tile[0],
											tile[1], gxEdit.currentLayer)
		map.modify(tiles)
		#TODO: disable undo while dragging
		#TODO: commit undo action only when mouseup
		undo = UndoAction(const.UNDO_TILE, oldTiles, tiles, gxEdit.currentLayer)
		curStage.addUndo(undo)

		gxEdit.rectanglePaintBoxStart = [-1, -1]
		gxEdit.rectanglePaintBoxEnd = [-1, -1]
	elif gxEdit.currentEditMode == const.EDIT_TILE and gxEdit.currentTilePaintMode == const.PAINT_COPY:
		stage = curStage
		mag = gxEdit.magnification
		x = int(mouse.x // (const.tileWidth * mag) + stage.hscroll)
		y = int(mouse.y // (const.tileWidth * mag) + stage.scroll)
		stage.selectedTilesEnd[0] = x
		stage.selectedTilesEnd[1] = y
	
		tiles = []
		start = stage.selectedTilesStart[:]
		end = stage.selectedTilesEnd[:]

		if end[0] < start[0]:
			start[0], end[0] = end[0], start[0]
		if end[1] < start[1]:
			start[1], end[1] = end[1], start[1]
		for y in range(start[1], end[1]+1):
			if y >= stage.pack.layers[gxEdit.currentLayer].height: continue
			for x in range(start[0], end[0]+1):
				if x >= stage.pack.layers[gxEdit.currentLayer].width: continue
				xx = stage.pack.layers[gxEdit.currentLayer].tiles[y][x] % 16
				yy = stage.pack.layers[gxEdit.currentLayer].tiles[y][x] // 16
				tiles.append([xx, yy])

		if tiles != []: stage.selectedTiles = tiles

		gxEdit.copyingTiles = False

		gxEdit.elements["toolsWindow"].elements["butDraw"].handleMouse1(None, gxEdit)


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
		gxEdit.tileSelectionUpdate = True

	#tiles Paint
	elif gxEdit.currentEditMode == const.EDIT_TILE:
		if not len(map.tiles): return
		x = int(mouse.x // (const.tileWidth * mag) + stage.hscroll)
		y = int(mouse.y // (const.tileWidth * mag) + stage.scroll)

		if x >= map.width or y >= map.height:
			return

		if stage.lastTileEdit == [x, y]:
			return

		startX = stage.selectedTilesStart[0]
		startY = stage.selectedTilesStart[1]
		tiles = []
		oldTiles = []

		if gxEdit.currentTilePaintMode == const.PAINT_COPY:
			if not gxEdit.copyingTiles:
				stage.selectedTilesStart[0] = x
				stage.selectedTilesStart[1] = y
				gxEdit.copyingTiles = True
			stage.selectedTilesEnd = [x, y]
			return
			
		elif gxEdit.currentTilePaintMode == const.PAINT_NORMAL:
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

			if negX: x -= w - 1
			if negY: y -= h - 1
			
			for i, tile in enumerate(stage.selectedTiles):
				xx = (i % w) + x
				yy = (i // w) + y

				if xx >= map.width or yy >= map.height: 
					continue

				tiles.append([[xx,yy], [tile[0], tile[1]]])

				oldTileX = map.tiles[yy][xx] % 16
				oldTileY = map.tiles[yy][xx] // 16

				oldTiles.append([[xx,yy], [oldTileX, oldTileY]])
		elif gxEdit.currentTilePaintMode == const.PAINT_RECTANGLE:

			if gxEdit.rectanglePaintBoxStart == [-1, -1]:
				gxEdit.rectanglePaintBoxStart = [x, y]
			gxEdit.rectanglePaintBoxEnd = [x, y]

			if gxEdit.tileHighlightAnimate and gxEdit.tileHighlightTimer < 40:
				gxEdit.tileHighlightDir = True
			return
		
		if gxEdit.multiplayerState == const.MULTIPLAYER_CLIENT:
			multi.sendTileEditPacket(gxEdit, gxEdit.curStage, tiles, gxEdit.currentLayer)
			return
		if gxEdit.multiplayerState == const.MULTIPLAYER_HOST:
			multi.serverSendTileEdit(gxEdit, gxEdit.curStage, tiles, gxEdit.currentLayer)
		for pos, tile in tiles:
			stage.renderTileToSurface(pos[0], pos[1], tile[0],
											tile[1], gxEdit.currentLayer)
		map.modify(tiles)
		#TODO: disable undo while dragging
		#TODO: commit undo action only when mouseup
		undo = UndoAction(const.UNDO_TILE, oldTiles, tiles, gxEdit.currentLayer)
		stage.addUndo(undo)

		stage.lastTileEdit = [x, y]
		if gxEdit.tileHighlightAnimate:
			gxEdit.tileHighlightTimer = 120
		
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
				elem.elements["stringEdit"].text = str(selectedEntities[0].string)
				elem.elements["stringEdit"].placeholderText = ""

				elem.elements["textHexBitsS"].text = util.lazybin(selectedEntities[0].bits, 8)
				elem.elements["textHexBits"].text = util.lazybin(selectedEntities[0].bits, 8)

				bit = 1
				for i in range(1, 9):
					elem.elements["butCheckBits" + str(i)].state = \
						interface.BUTTON_STATE_ACTIVE if selectedEntities[0].bits & bit else \
						interface.BUTTON_STATE_NORMAL
					bit *= 2

			else:
				for _,e in elem.elements.items():
					if isinstance(e, interface.UITextInput):
						e.text = ""
						e.placeholderText = "\n\n\n\n"
				elem.elements["textHexBitsS"].text = ""
				elem.elements["textHexBits"].text = ""
				bit = 1
				for i in range(1, 9):
					foundCount = 0
					for o in selectedEntities:
						if o.bits & bit:
							foundCount += 1
					if foundCount == len(selectedEntities):
						elem.elements["butCheckBits" + str(i)].state = interface.BUTTON_STATE_ACTIVE
						elem.elements["textHexBitsS"].text += "1"
						elem.elements["textHexBits"].text += "1"
					elif foundCount >= 1:
						elem.elements["butCheckBits" + str(i)].state = interface.BUTTON_STATE_CLICKED
						elem.elements["textHexBitsS"].text += "?"
						elem.elements["textHexBits"].text += "?"
					else:
						elem.elements["butCheckBits" + str(i)].state = interface.BUTTON_STATE_NORMAL
						elem.elements["textHexBitsS"].text += "0"
						elem.elements["textHexBits"].text += "0"
					bit *= 2
				elem.elements["textHexBitsS"].text = elem.elements["textHexBitsS"].text[::-1]
				elem.elements["textHexBits"].text = elem.elements["textHexBits"].text[::-1]

			elem.visible = True
			elem.x = mouse.x - elem.w - 8
			elem.y = mouse.y - elem.h//2

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

toolsOrdered = ("butDraw", "butErase", "butCopy", "butFill", "butReplace", "butRectangle")

def runKeyboard(gxEdit, stage, scaleFactor, key):
	sym = key.keysym.scancode
	#TODO: scancode
	if key.keysym.mod & sdl2.KMOD_CTRL:

		if sym == sdl2.SDL_SCANCODE_S:
			#TODO: show flash on save (goodly)
			if stage.save():
				gxEdit.saveTimer = 5

		elif sym == sdl2.SDL_SCANCODE_Z and not gxEdit.multiplayerState: #todo
			if key.keysym.mod & sdl2.KMOD_SHIFT:
				gxEdit.executeRedo()
			else:
				gxEdit.executeUndo()

		elif sym == sdl2.SDL_SCANCODE_Y and not gxEdit.multiplayerState: #todo
			gxEdit.executeRedo()

		elif sym == sdl2.SDL_SCANCODE_C:
			if stage.selectedEntities:
				gxEdit.copiedEntities = copy.deepcopy(stage.selectedEntities)
				basex = min([o.x for o in gxEdit.copiedEntities])
				basey = min([o.y for o in gxEdit.copiedEntities])

				for o in gxEdit.copiedEntities:
					o.x -= basex
					o.y -= basey
		
		elif sym == sdl2.SDL_SCANCODE_V:
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
		elif sym == sdl2.SDL_SCANCODE_1:
			gxEdit.elements["toolsWindow"].elements["butMap0"].handleMouse1(None, gxEdit)
		elif sym == sdl2.SDL_SCANCODE_2:
			gxEdit.elements["toolsWindow"].elements["butMap1"].handleMouse1(None, gxEdit)
		elif sym == sdl2.SDL_SCANCODE_3:
			gxEdit.elements["toolsWindow"].elements["butMap2"].handleMouse1(None, gxEdit)
		elif sym == sdl2.SDL_SCANCODE_4:
			gxEdit.elements["toolsWindow"].elements["butUnits"].handleMouse1(None, gxEdit)
		elif sym == sdl2.SDL_SCANCODE_5:
			gxEdit.elements["toolsWindow"].elements["butAttr"].handleMouse1(None, gxEdit)


	#TODO: make this better
	elif gxEdit.focussedElem:
		if sym == sdl2.SDL_SCANCODE_BACKSPACE:
			if gxEdit.focussedElem:
				gxEdit.focussedElem.text = gxEdit.focussedElem.text[:-1]
				if gxEdit.focussedElem.onAction:
					gxEdit.focussedElem.onAction(gxEdit.focussedElem, gxEdit)
		return

	#zx change tool
	elif sym == sdl2.SDL_SCANCODE_1:
		gxEdit.elements["toolsWindow"].elements["butDraw"].handleMouse1(None, gxEdit)
	elif sym == sdl2.SDL_SCANCODE_2:
		gxEdit.elements["toolsWindow"].elements["butErase"].handleMouse1(None, gxEdit)
	elif sym == sdl2.SDL_SCANCODE_3:
		gxEdit.elements["toolsWindow"].elements["butCopy"].handleMouse1(None, gxEdit)
	elif sym == sdl2.SDL_SCANCODE_4:
		gxEdit.elements["toolsWindow"].elements["butFill"].handleMouse1(None, gxEdit)
	elif sym == sdl2.SDL_SCANCODE_5:
		gxEdit.elements["toolsWindow"].elements["butReplace"].handleMouse1(None, gxEdit)
	elif sym == sdl2.SDL_SCANCODE_6:
		gxEdit.elements["toolsWindow"].elements["butRectangle"].handleMouse1(None, gxEdit)
	
	#elif sym == sdl2.SDL_SCANCODE_Z:
	#	gxEdit.currentTilePaintMode -= 1
	#	if gxEdit.currentTilePaintMode < 0: gxEdit.currentTilePaintMode = 5
	#	gxEdit.elements["toolsWindow"].elements[toolsOrdered[gxEdit.currentTilePaintMode]].handleMouse1(None, gxEdit)
	#elif sym == sdl2.SDL_SCANCODE_X:
	#	gxEdit.currentTilePaintMode += 1
	#	if gxEdit.currentTilePaintMode > 5: gxEdit.currentTilePaintMode = 0
	#	gxEdit.elements["toolsWindow"].elements[toolsOrdered[gxEdit.currentTilePaintMode]].handleMouse1(None, gxEdit)
	
	elif sym == sdl2.SDL_SCANCODE_J:
		gxEdit.curStage -= 1
	elif sym == sdl2.SDL_SCANCODE_K:
		gxEdit.curStage += 1

	#window shortcuts
	elif sym == sdl2.SDL_SCANCODE_E:
		interface.toggleEntityPalette(0,0,gxEdit)
	elif sym == sdl2.SDL_SCANCODE_R:
		interface.toggleTilePalette(0,0,gxEdit)

	#field shortcut transportation
	elif sym == sdl2.SDL_SCANCODE_T:
		for i in range(len(gxEdit.stages)):
			if gxEdit.stages[i].stageName == stage.pack.up_field:
				gxEdit.curStage = i
				return
		if gxEdit.loadStage(stage.pack.up_field):
			gxEdit.curStage = len(gxEdit.stages)
	elif sym == sdl2.SDL_SCANCODE_F:
		for i in range(len(gxEdit.stages)):
			if gxEdit.stages[i].stageName == stage.pack.left_field:
				gxEdit.curStage = i
				return
		if gxEdit.loadStage(stage.pack.left_field):
			gxEdit.curStage = len(gxEdit.stages)
	elif sym == sdl2.SDL_SCANCODE_G:
		for i in range(len(gxEdit.stages)):
			if gxEdit.stages[i].stageName == stage.pack.down_field:
				gxEdit.curStage = i
				return
		if gxEdit.loadStage(stage.pack.down_field):
			gxEdit.curStage = len(gxEdit.stages)
	elif sym == sdl2.SDL_SCANCODE_H:
		for i in range(len(gxEdit.stages)):
			if gxEdit.stages[i].stageName == stage.pack.right_field:
				gxEdit.curStage = i
				return
		if gxEdit.loadStage(stage.pack.right_field):
			gxEdit.curStage = len(gxEdit.stages)
	
	#keyboard navigation tile selection
	elif sym == sdl2.SDL_SCANCODE_A:
		if not key.keysym.mod & sdl2.KMOD_SHIFT:
			stage.selectedTilesStart[0] -= 1
		if not key.keysym.mod & sdl2.KMOD_ALT:
			stage.selectedTilesEnd[0] -= 1
		stage.lastTileEdit = [None, None]
		gxEdit.tileSelectionUpdate = True
	elif sym == sdl2.SDL_SCANCODE_D:
		if not key.keysym.mod & sdl2.KMOD_SHIFT:
			stage.selectedTilesStart[0] += 1
		if not key.keysym.mod & sdl2.KMOD_ALT:
			stage.selectedTilesEnd[0] += 1
		stage.lastTileEdit = [None, None]
		gxEdit.tileSelectionUpdate = True
	elif sym == sdl2.SDL_SCANCODE_W:
		if not key.keysym.mod & sdl2.KMOD_SHIFT:
			stage.selectedTilesStart[1] -= 1
		if not key.keysym.mod & sdl2.KMOD_ALT:
			stage.selectedTilesEnd[1] -= 1
		stage.lastTileEdit = [None, None]
		gxEdit.tileSelectionUpdate = True
	elif sym == sdl2.SDL_SCANCODE_S and not key.keysym.mod & sdl2.KMOD_CTRL:
		if not key.keysym.mod & sdl2.KMOD_SHIFT:
			stage.selectedTilesStart[1] += 1
		if not key.keysym.mod & sdl2.KMOD_ALT:
			stage.selectedTilesEnd[1] += 1
		stage.lastTileEdit = [None, None]
		gxEdit.tileSelectionUpdate = True
		
	#keyboard navigation mouse movement
	elif sym == sdl2.SDL_SCANCODE_KP_8:
		mouse = util.getMouseState()
		sdl2.SDL_WarpMouseInWindow(None, mouse.x, int(mouse.y-const.tileWidth*gxEdit.magnification))
	elif sym == sdl2.SDL_SCANCODE_KP_4:
		mouse = util.getMouseState()
		sdl2.SDL_WarpMouseInWindow(None,  int(mouse.x-const.tileWidth*gxEdit.magnification), mouse.y)
	elif sym == sdl2.SDL_SCANCODE_KP_5:
		mouse = util.getMouseState()
		sdl2.SDL_WarpMouseInWindow(None, mouse.x,  int(mouse.y+const.tileWidth*gxEdit.magnification))
	elif sym == sdl2.SDL_SCANCODE_KP_6:
		mouse = util.getMouseState()
		sdl2.SDL_WarpMouseInWindow(None,  int(mouse.x+const.tileWidth*gxEdit.magnification), mouse.y)

	#keyboard navigation scroll
	elif sym == sdl2.SDL_SCANCODE_LEFT:
		stage.hscroll -= 2
	elif sym == sdl2.SDL_SCANCODE_RIGHT:
		stage.hscroll += 2
	elif sym == sdl2.SDL_SCANCODE_DOWN:
		stage.scroll += 2
	elif sym == sdl2.SDL_SCANCODE_UP:
		stage.scroll -= 2
	elif sym == sdl2.SDL_SCANCODE_HOME:
		stage.scroll = 0
	elif sym == sdl2.SDL_SCANCODE_END:
		stage.scroll = stage.pack.layers[0].height - scaleFactor
	elif sym == sdl2.SDL_SCANCODE_PAGEDOWN:
		stage.scroll += int(scaleFactor // 1.5)
	elif sym == sdl2.SDL_SCANCODE_PAGEUP:
		stage.scroll -= int(scaleFactor // 1.5)

	#keyboard navigation zoom
	elif sym == sdl2.SDL_SCANCODE_MINUS:
		if gxEdit.magnification == 1:
			gxEdit.magnification = 0.5
		else:
			gxEdit.magnification -= 1
	elif sym == sdl2.SDL_SCANCODE_EQUALS:
		if gxEdit.magnification == 0.5:
			gxEdit.magnification = 1
		else:
			gxEdit.magnification += 1

	elif sym == sdl2.SDL_SCANCODE_LEFTBRACKET:
		gxEdit.tilePaletteMag -= 1

	elif sym == sdl2.SDL_SCANCODE_RIGHTBRACKET:
		gxEdit.tilePaletteMag += 1

	elif sym == sdl2.SDL_SCANCODE_APOSTROPHE:
		gxEdit.entityPaletteMag -= 1

	elif sym == sdl2.SDL_SCANCODE_BACKSLASH:
		gxEdit.entityPaletteMag += 1

	#layer switch
	elif sym == sdl2.SDL_SCANCODE_COMMA:
		gxEdit.currentLayer -= 1
		if gxEdit.currentLayer < 0: gxEdit.currentLayer = 0

	elif sym == sdl2.SDL_SCANCODE_PERIOD:
		gxEdit.currentLayer += 1
		if gxEdit.currentLayer > 2: gxEdit.currentLayer = 2

	#entity manipulation
	elif sym == sdl2.SDL_SCANCODE_I:
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

	elif sym == sdl2.SDL_SCANCODE_DELETE:
		if stage.selectedEntities:
			ids = [o.id for o in stage.selectedEntities]
			stage.pack.eve.remove(ids)
			gxEdit.elements["entEdit"].visible = False

			undo = UndoAction(const.UNDO_ENTITY_REMOVE, 0, stage.selectedEntities)
			stage.addUndo(undo)

			stage.selectedEntities = []


	elif sym == sdl2.SDL_SCANCODE_F11:
		gxEdit.fullscreen ^= 1

		if not gxEdit.fullscreen:
			sdl2.SDL_SetWindowFullscreen(interface.gWindow.window, sdl2.SDL_WINDOW_FULLSCREEN_DESKTOP)
		else:
			sdl2.SDL_SetWindowFullscreen(interface.gWindow.window, 0)