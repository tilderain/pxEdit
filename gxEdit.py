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

from sdl2 import sdlimage
from editor import gxEdit, setup_game_environment

import multi
import util

from game import GameManager
from formats import FormatManager

from stage import Stage, Layer, Entity

from editor import gxEdit
from editor import defaultStage


if False:
    import formatKero
    import formatCave
    import formatGuxt

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



#for debugging
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




from editor import gxEdit, setup_game_environment

def main():
	# --- NEW SETUP ---
	GAME_CHOICE = "star_frog_10x" # You can change the starting game here
	setup_game_environment(GAME_CHOICE)
	from editor import defaultStage # Now we can safely import it
	# ---

	sdl2.ext.init()

	try:
		icon_surface = sdlimage.IMG_Load(b"./face.png")
		if not icon_surface:
			print(f"Error loading icon: {sdlimage.IMG_GetError().decode()}")
			icon_surface = None # Ensure it's None on failure
	except Exception as e:
		print(f"Exception while loading icon: {e}")
		icon_surface = None


	sdlimage.IMG_Init(sdlimage.IMG_INIT_JPG)

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

	if icon_surface:
		sdl2.SDL_SetWindowIcon(window.window, icon_surface.contents)
		sdl2.SDL_FreeSurface(icon_surface) # Free the surface after setting the icon

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

	gxEdit.v_scrollbar = interface.UIScrollbar(is_vertical=True)
	gxEdit.h_scrollbar = interface.UIScrollbar(is_vertical=False)

	gxEdit.loadMeta(sprfactory)

	gxEdit.loadStage(defaultStage)

	if gxEdit.game_manager.get_current_game().name == "guxt":
		# Stages are named "1" through "6". Stage "1" is already loaded.
		for i in range(2, 7):
			gxEdit.loadStage(str(i))
			
	introAnimTimer = 0

	running = True
	mouseover = True

	mouseHeld = False


	#gxEdit.elements.append(UIWindow(100, 100, 128, 64))
	#gxEdit.elements.append(interface.UIWindow(22, 22, 256, 256))
	#gxEdit.elements.append(interface.UIWindow(300, 300, 260, 272, const.WINDOW_TILEPALETTE))

	# Make sure stage tabs are added first to be drawn under other windows
	gxEdit.elements["stageTabs"] = interface.StageTabsBar(0, 0, interface.gWindowWidth, 24)

	entity_rows = math.ceil(len(gxEdit.entityInfo) / 16) if gxEdit.entityInfo else 1
	entityinfoheight = (entity_rows * gxEdit.tileWidth2) + 24

	gxEdit.elements["tilePalette"] = interface.TilePaletteWindow(1200, 400, 256, 280, const.WINDOW_TILEPALETTE)
	gxEdit.elements["entityPalette"] = interface.EntityPaletteWindow(1450, 400, 256, entityinfoheight, const.WINDOW_ENTITYPALETTE)

	gxEdit.elements["toolsWindow"] = interface.ToolsWindow(800, 400, 190, 86, const.WINDOW_TOOLS)

	gxEdit.elements["uiTooltip"] = interface.UITooltip(0,0,1,1)

	gxEdit.elements["entEdit"] = interface.EntityEditWindow(20,20,150,250)

	gxEdit.elements["mapSizeDialog"] = interface.MapResizeDialog(20,20,104,88)

	gxEdit.elements["pxPackAttrDialog"] = interface.PxPackAttrDialog(20,20,405,270)

	gxEdit.elements["dialogMultiplayer"] = interface.MultiplayerWindow(0,0,220,80)

	gxEdit.elements["stageSelection"] = interface.StageSelectionWindow(0, 0, 200, 250)

	gxEdit.elements["gameSelection"] = interface.GameSelectionWindow(0, 0, 250, 100, visible=True)
	game_selection_win = gxEdit.elements["gameSelection"]
	game_selection_win.refresh_list(gxEdit) # Populate with games

	# Center it on screen
	game_selection_win.x = (defaultWindowWidth - game_selection_win.w) // 2
	game_selection_win.y = (defaultWindowHeight - game_selection_win.h) // 2

	game_selection_win = gxEdit.elements["dialogMultiplayer"] 
	# Center it on screen
	game_selection_win.x = (defaultWindowWidth - game_selection_win.w) // 4
	game_selection_win.y = (defaultWindowHeight - game_selection_win.h) // 4
	def renderEditor():
		#TODO: placeholder
		gui.renderEditorBg()

		tabs_bar = gxEdit.elements.get("stageTabs")
		if tabs_bar and tabs_bar.visible:
			tabs_bar.render(gxEdit, curStage)

		# --- THIS IS THE FIX: Ensure the viewport height is never negative ---
		viewport_height = max(0, interface.gWindowHeight - gxEdit.content_y_offset - gxEdit.statusBarHeight)
		viewport = sdl2.SDL_Rect(0, gxEdit.content_y_offset, interface.gWindowWidth, viewport_height)
		# --- END OF FIX ---
		sdl2.SDL_RenderSetViewport(renderer.sdlrenderer, ctypes.byref(viewport))

		# --- RENDER LOGIC CHANGE ---
		if curStage.is_attribute_stage:
			# For attribute stages, render Layer 0 (tileset) then Layer 1 (attributes) on top
			gui.renderTiles(gxEdit, curStage, 0) # The visual tileset background
			gui.renderTiles(gxEdit, curStage, 1) # The transparent attribute overlay
		else:
			# For normal stages, render as before
			gui.renderBgColor(gxEdit, curStage)
			for i in reversed(range(3)):
				if gxEdit.visibleLayers[i]:
					gui.renderTiles(gxEdit, curStage, i)
		# ---------------------------

		if not curStage.is_attribute_stage and gxEdit.visibleLayers[4]:
			map_layer = curStage.pack.layers[gxEdit.currentLayer] if len(curStage.pack.layers) > gxEdit.currentLayer else None
			if map_layer:
				gui.renderTileAttr(gxEdit, curStage, map_layer)

		gui.renderEntitySelectionBox(gxEdit, curStage)
		gui.renderPlayers(gxEdit, curStage)
		gui.renderTilePreview(gxEdit, curStage)

		if not curStage.is_attribute_stage and (gxEdit.visibleLayers[3] or gxEdit.currentEditMode == const.EDIT_ENTITY):
			gui.renderEntities(gxEdit, curStage)
		sdl2.SDL_RenderSetViewport(renderer.sdlrenderer, None)

		if gxEdit.v_scrollbar.action_state != interface.SCROLL_ACTION_GRAY:
			gxEdit.v_scrollbar.render(renderer)
		if gxEdit.h_scrollbar.action_state != interface.SCROLL_ACTION_GRAY:
			gxEdit.h_scrollbar.render(renderer)
			
		gui.renderStatusBar(gxEdit, curStage)

		for key, elem in gxEdit.elements.items():
			if key == "stageTabs": continue
			if elem.visible and elem.type != const.WINDOW_TOOLTIP: 
				gui.renderUIWindow(gxEdit, elem)
				elem.render(gxEdit, curStage)

		for _, elem in gxEdit.elements.items():
			if elem.type == const.WINDOW_TOOLTIP and elem.visible:
				elem.render(gxEdit, curStage)

			
		gui.render_popups(gxEdit)
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


		# --- THIS IS THE FIX: Add a queue processing block ---
		while gxEdit.main_thread_queue:
			command, payload = gxEdit.main_thread_queue.popleft()
			print(f"Main thread processing command: {command}")
			if command == 'LOAD_SYNCED_STAGE':
				from editor import StagePrj
				s_data = payload

				# 1. Create sprites for any newly received tilesets
				for name, image_bytes in gxEdit.synced_tileset_data_raw.items():
					try:
						# ... (same sprite creation logic as in FINISH_SYNC)
						rwops = sdl2.SDL_RWFromConstMem(image_bytes, len(image_bytes))
						img_surface = sdlimage.IMG_Load_RW(rwops, 1)
						if not img_surface: continue
						
						sprite = interface.gSprfactory.from_surface(img_surface.contents)
						sdl2.SDL_FreeSurface(img_surface)
						gxEdit.synced_tilesets[name] = sprite
						print(f"  -> Created sprite for new tileset '{name}'")
					except Exception as e:
						print(f"Error creating sprite for new stage: {e}")
				gxEdit.synced_tileset_data_raw.clear() # Clear after processing

				# 2. Assemble the stage
				stage_prj = StagePrj(s_data['stageName'], s_data['pack'], gxEdit.tileWidth)
				stage_prj.is_attribute_stage = s_data['is_attribute_stage']
				stage_prj.original_path = s_data['original_path']

				for i, layer in enumerate(stage_prj.pack.layers):
					if layer.partsName in gxEdit.synced_tilesets:
						stage_prj.parts[i] = gxEdit.synced_tilesets[layer.partsName]
				
				for i in range(len(stage_prj.pack.layers)):
					if stage_prj.parts[i]:
						stage_prj.loadAttrs(i)
					stage_prj.createMapSurface(i)
					stage_prj.renderMapToSurface(i)
				
				# 3. Add to stages list at the correct index
				stage_index = s_data['index']
				if stage_index >= len(gxEdit.stages):
					gxEdit.stages.append(stage_prj)
				else:
					gxEdit.stages.insert(stage_index, stage_prj)
				
				print(f"  -> Assembled and loaded synced stage '{s_data['stageName']}'")
			if command == 'SWITCH_GAME_FOR_SYNC':
				game_name = payload
				
				# All these functions now run safely on the main thread
				setup_game_environment(game_name)
				interface.reload_game_surfaces()
				gxEdit.loadMeta(None)
				gxEdit.update_tile_dimensions()
				gxEdit.stages.clear()
			if command == 'FINISH_SYNC':
				# This block now runs safely in the main thread.
				from editor import StagePrj

				# 1. Create all Sprite objects from raw cached data
				for name, image_bytes in gxEdit.synced_tileset_data_raw.items():
					try:
						rwops = sdl2.SDL_RWFromConstMem(image_bytes, len(image_bytes))
						img_surface = sdlimage.IMG_Load_RW(rwops, 1)
						if not img_surface: continue
						
						sprite = interface.gSprfactory.from_surface(img_surface.contents)
						sdl2.SDL_FreeSurface(img_surface)
						gxEdit.synced_tilesets[name] = sprite
						print(f"  -> Created sprite for '{name}'")
					except Exception as e:
						print(f"Error creating sprite from synced data '{name}': {e}")
				
				# 2. Assemble the stages using the newly created sprites
				if gxEdit.open_stages_info_from_sync:
					stage_names = gxEdit.open_stages_info_from_sync["names"]
					for name in stage_names:
						if name not in gxEdit.synced_stage_data: continue
						s_data = gxEdit.synced_stage_data[name]

						stage_prj = StagePrj(s_data['stageName'], s_data['pack'], gxEdit.tileWidth)
						stage_prj.is_attribute_stage = s_data['is_attribute_stage']
						stage_prj.original_path = s_data['original_path']

						for i, layer in enumerate(stage_prj.pack.layers):
							if layer.partsName in gxEdit.synced_tilesets:
								stage_prj.parts[i] = gxEdit.synced_tilesets[layer.partsName]
						
						# Finalize loading (this is where renderMapToSurface is called)
						for i in range(len(stage_prj.pack.layers)):
							if stage_prj.parts[i]:
								stage_prj.loadAttrs(i)
							stage_prj.createMapSurface(i)
							stage_prj.renderMapToSurface(i)
						
						gxEdit.stages.append(stage_prj)
						print(f"  -> Assembled stage '{name}'")

					gxEdit.curStage = gxEdit.open_stages_info_from_sync["active_index"]
				
				# 3. Clean up and finish syncing state
				gxEdit.synced_tileset_data_raw.clear()
				gxEdit.synced_stage_data.clear()
				gxEdit.open_stages_info_from_sync = None
				gxEdit.is_syncing = False # <-- Unset flag here!
				gxEdit.no_game_loaded = False # A game is now loaded!
				
				game_win = gxEdit.elements.get("gameSelection")
				game_win.visible = False

				print("--- Main thread assembly complete. ---")
		# --- END OF FIX ---
		if gxEdit.no_game_loaded and not gxEdit.is_syncing:
			gui.fill()
			
			# --- RENDER AND INTERACT WITH BOTH WINDOWS ---
			windows_to_process = []
			game_win = gxEdit.elements.get("gameSelection")
			multi_win = gxEdit.elements.get("dialogMultiplayer")
			multi_win.visible = True

			if game_win and game_win.visible: windows_to_process.append(game_win)
			if multi_win and multi_win.visible: windows_to_process.append(multi_win)

			# Render windows
			for win in windows_to_process:
				gui.renderUIWindow(gxEdit, win)
				win.render(gxEdit, None)
			gui.render_popups(gxEdit)

			events = sdl2.ext.get_events()
			for event in events:
				if event.type == sdl2.SDL_QUIT:
					running = False
					break
				
				# Handle window dragging and clicking
				if event.type == sdl2.SDL_MOUSEMOTION:
					if gxEdit.draggedElem:
						gxEdit.draggedElem.x = event.motion.x - gxEdit.dragX
						gxEdit.draggedElem.y = event.motion.y - gxEdit.dragY
				elif event.type == sdl2.SDL_MOUSEBUTTONDOWN:
					# Check windows from top to bottom (reversed order)
					clicked_on_window = False
					for win in reversed(windows_to_process):
						if util.inWindowBoundingBox(event.button, win):
							win.handleMouse1(event.button, gxEdit)
							if util.inDragHitbox(event.button, win):
								gxEdit.draggedElem = win
								gxEdit.dragX = event.button.x - win.x
								gxEdit.dragY = event.button.y - win.y
							
								
							clicked_on_window = True
							break # Stop after handling the topmost window
				elif event.type == sdl2.SDL_MOUSEBUTTONUP:
					gxEdit.draggedElem = None
					if gxEdit.activeElem:
						gxEdit.activeElem.handleMouse1Up(event.button, gxEdit)
						gxEdit.activeElem = None
				elif event.type == sdl2.SDL_TEXTINPUT:
					if gxEdit.focussedElem:
						gxEdit.focussedElem.handleTextInput(event.text.text.decode("utf-8"), gxEdit)
				elif event.type == sdl2.SDL_KEYDOWN:
					if gxEdit.focussedElem and event.key.keysym.scancode == sdl2.SDL_SCANCODE_BACKSPACE:
						gxEdit.focussedElem.text = gxEdit.focussedElem.text[:-1]

			renderer.present()
			sdl2.SDL_Delay(16)
			continue # Skip the rest of the main loop
		# --- END OF FIX ---

		if gxEdit.is_syncing:
			# If syncing, render a simple waiting screen and skip all game logic
			gui.fill()
			sync_text = "Synchronizing with host..."
			text_w, text_h = interface.getTextSize(sync_text, interface.gFont)
			text_x = (interface.gWindowWidth - text_w) // 2
			text_y = (interface.gWindowHeight - text_h) // 2
			interface.renderText(sync_text, interface.sdlColorWhite, sdl2.sdlttf.TTF_STYLE_NORMAL, text_x, text_y)
			renderer.present()
			sdl2.SDL_Delay(16) # Don't burn CPU while waiting
			continue # Skip the rest of the loop
		# --- END OF FIX ---
		
		# If the list of stages is empty for any reason, we can't proceed.
		if not gxEdit.stages:
			# This can happen on initial client startup before sync begins.
			# Render a blank screen and wait.
			gui.fill()
			interface.renderText("Waiting for connection...", interface.sdlColorWhite, sdl2.sdlttf.TTF_STYLE_NORMAL, 10, 10)
			renderer.present()
			# We still need to process events to open the multiplayer menu.
			events = sdl2.ext.get_events()
			for event in events:
				if event.type == sdl2.SDL_QUIT:
					running = False
					break
				# Allow minimal UI interaction to open multiplayer window
				if event.type == sdl2.SDL_MOUSEBUTTONDOWN:
					input.runMouse1(None, event.button)
			# Don't proceed to game logic
			continue
		
		curStage = gxEdit.stages[gxEdit.curStage]
		
		#height of window in tiles
		scaleFactor = (interface.gWindowHeight // gxEdit.stages[gxEdit.curStage].tileWidth // gxEdit.magnification)
		events = sdl2.ext.get_events()
		
		mouse_triggered = False

		multiwindowstring = ""
		if gxEdit.multiplayerState == const.MULTIPLAYER_HOST:
			multiwindowstring = "**Hosting**"
		elif gxEdit.multiplayerState == const.MULTIPLAYER_CLIENT:
			multiwindowstring = "**Connected**"

		#set windowname
		saveAsterisk = ""
		stage = gxEdit.stages[gxEdit.curStage]
		if stage.lastSavePos != stage.undoPos:
			saveAsterisk = "*"
		interface.gWindow.title = windowName + " [" + "" + str(curStage.stageName) + saveAsterisk + "]" + " " + multiwindowstring
		
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
				dropped_file_path = event.drop.file.decode('utf-8')
				
				# Extract filename and extension
				if sys.platform == "win32":
					fName_with_ext = os.path.basename(dropped_file_path)
				else:
					fName_with_ext = os.path.basename(dropped_file_path)
				
				fName, fExt = os.path.splitext(fName_with_ext)
				
				# Get the expected attribute extension for the current game
				current_game_config = gxEdit.game_manager.get_current_game()
				attr_ext = current_game_config.get('attr_ext')

				# Decide which loader to use based on file extension
				if fExt.lower() == attr_ext.lower():
					# It's an attribute file, load it as a stage
					if gxEdit.loadAttributeFileAsStage(fName, dropped_file_path):
						gxEdit.curStage = len(gxEdit.stages) - 1
				else:
					# Assume it's a regular stage file
					if gxEdit.loadStage(fName):
						gxEdit.curStage = len(gxEdit.stages) - 1

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
				handled = False
				mouse = util.getMouseState() # Get the mouse state to find its position
				for key, elem in reversed(list(gxEdit.elements.items())):
					if elem.visible and util.inWindowBoundingBox(mouse, elem):
						if hasattr(elem, 'handleMouseWheel'):
							elem.handleMouseWheel(event.wheel)
							handled = True
							break
				if not handled:
					input.runMouseWheel(curStage, event.wheel)
			elif event.type == sdl2.SDL_MOUSEBUTTONDOWN:
				mouseHeld = True
				mouse_triggered = (event.button.button == sdl2.SDL_BUTTON_LEFT)

				input.runMouse1(curStage, event.button)
				input.runMouse2(gxEdit, curStage, event.button)
				input.runMouse3(gxEdit, curStage, event.button)
				input.runMouseDrag(gxEdit, curStage, event.button)
			elif event.type == sdl2.SDL_MOUSEBUTTONUP:
				input.runMouseUp(gxEdit, curStage, event.button)
				mouseHeld = False
				gxEdit.draggedElem = None
				gxEdit.resizingElem = None
			elif event.type == sdl2.SDL_TEXTINPUT:
				if gxEdit.focussedElem:
					gxEdit.focussedElem.handleTextInput(event.text.text.decode("utf-8"), gxEdit)


		h_scrollbar_h = interface.SCROLL_BUTTON_SIZE if gxEdit.h_scrollbar.action_state != interface.SCROLL_ACTION_GRAY else 0
		view_rect = sdl2.SDL_Rect(
			0, gxEdit.content_y_offset,
			interface.gWindowWidth,
			max(0, interface.gWindowHeight - gxEdit.content_y_offset - gxEdit.statusBarHeight - h_scrollbar_h)
		)

		h_needed = False
		v_needed = False
		if curStage.pack.layers and curStage.pack.layers[0]:
			main_layer = curStage.pack.layers[0]
			unpadded_content_w = main_layer.width * gxEdit.tileWidth * gxEdit.magnification
			unpadded_content_h = main_layer.height * gxEdit.tileWidth * gxEdit.magnification
			
			# Check if horizontal scrollbar is needed
			if unpadded_content_w > interface.gWindowWidth:
				h_needed = True
			# Check if vertical scrollbar is needed (account for horizontal bar's height if it will appear)
			potential_h_bar_h = interface.SCROLL_BUTTON_SIZE if h_needed else 0
			if unpadded_content_h > (interface.gWindowHeight - gxEdit.content_y_offset - gxEdit.statusBarHeight - potential_h_bar_h):
				v_needed = True

		h_scrollbar_h = interface.SCROLL_BUTTON_SIZE if h_needed else 0
		view_rect = sdl2.SDL_Rect(
			0, gxEdit.content_y_offset,
			interface.gWindowWidth,
			max(0, interface.gWindowHeight - gxEdit.content_y_offset - gxEdit.statusBarHeight - h_scrollbar_h)
		)

		if curStage.pack.layers and curStage.pack.layers[0]:
			main_layer = curStage.pack.layers[0]
			
			# Add overscroll padding ONLY if the scrollbar is active
			overscroll_padding_y = view_rect.h / 2 if v_needed else 0
			overscroll_padding_x = view_rect.w / 2 if h_needed else 0

			# Update Vertical Scrollbar with potentially padded content size
			content_h_px = (main_layer.height * gxEdit.tileWidth * gxEdit.magnification) + overscroll_padding_y
			gxEdit.v_scrollbar.set_properties(view_rect, content_h_px, curStage.scroll * gxEdit.tileWidth * gxEdit.magnification)
			
			# Update Horizontal Scrollbar with potentially padded content size
			content_w_px = (main_layer.width * gxEdit.tileWidth * gxEdit.magnification) + overscroll_padding_x
			gxEdit.h_scrollbar.set_properties(view_rect, content_w_px, curStage.hscroll * gxEdit.tileWidth * gxEdit.magnification)
		# --- END OF FIX ---

			# Handle mouse input for scrollbars
			mouse = util.getMouseState()
			new_v_offset_px = gxEdit.v_scrollbar.handle_mouse(mouse, mouseHeld, mouse_triggered)
			new_h_offset_px = gxEdit.h_scrollbar.handle_mouse(mouse, mouseHeld, mouse_triggered)

			# Apply changes back to stage scroll (converting pixels to tiles)
			if gxEdit.tileWidth * gxEdit.magnification > 0:
				curStage.scroll = new_v_offset_px / (gxEdit.tileWidth * gxEdit.magnification)
				curStage.hscroll = new_h_offset_px / (gxEdit.tileWidth * gxEdit.magnification)
		

		#TODO figure out a better way to do this
		def clampCurStage():
			if gxEdit.curStage >= len(gxEdit.stages):
				gxEdit.curStage = len(gxEdit.stages) - 1 
			if gxEdit.curStage < 0:
				gxEdit.curStage = 0
		def clampScroll(stage):
			# --- THIS IS THE FIX: Adjust clamping to allow for overscroll ---
			view_h_tiles = (interface.gWindowHeight - gxEdit.content_y_offset - gxEdit.statusBarHeight) / (gxEdit.tileWidth * gxEdit.magnification)
			view_w_tiles = interface.gWindowWidth / (gxEdit.tileWidth * gxEdit.magnification)

			# Calculate max scroll position with half-screen padding
			max_scroll_y = stage.pack.height - (view_h_tiles / 2)
			max_scroll_x = stage.pack.width - (view_w_tiles / 2)
			
			# Prevent scrolling beyond the map content entirely
			stage.scroll = min(stage.scroll, max_scroll_y)
			stage.hscroll = min(stage.hscroll, max_scroll_x)

			# Prevent scrolling too far back (negative)
			if stage.scroll < 0:
				stage.scroll = 0
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
		interface.update_cursor(gxEdit)

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
				offset_y = mouse.y - gxEdit.content_y_offset
				x = int(mouse.x // gxEdit.magnification) + int(curStage.hscroll * gxEdit.tileWidth)
				y = int(offset_y // gxEdit.magnification) + int(curStage.scroll * gxEdit.tileWidth)
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
