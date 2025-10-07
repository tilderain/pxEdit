import os
import sdl2
from sdl2 import sdlimage, SDL_Rect, surface, render
from collections import deque
import interface
from editor import StagePrj # Import the class definition

def _render_stage_to_renderer(editor, stage, renderer, offset_x=0, offset_y=0):
    """Helper function to render a full stage onto the current render target, clipped to Layer 0's dimensions."""
    if not stage.pack.layers or not stage.pack.layers[0]: return
    
    bounds_width = stage.pack.layers[0].width
    bounds_height = stage.pack.layers[0].height

    for i in reversed(range(len(stage.pack.layers))):
        map_layer = stage.pack.layers[i]
        parts_sprite = stage.parts[i]
        if not map_layer or not parts_sprite or not map_layer.tiles:
            continue

        src_rect = SDL_Rect(0, 0, editor.tileWidth, editor.tileWidth)
        dst_rect = SDL_Rect(0, 0, editor.tileWidth, editor.tileWidth)

        for y in range(bounds_height):
            for x in range(bounds_width):
                if y >= map_layer.height or x >= map_layer.width:
                    continue

                tile_id = map_layer.tiles[y][x]
                if tile_id == 0 and i > 0: continue

                src_rect.x = (tile_id % 16) * editor.tileWidth
                src_rect.y = (tile_id // 16) * editor.tileWidth
                
                dst_rect.x = offset_x + (x * editor.tileWidth)
                dst_rect.y = offset_y + (y * editor.tileWidth)
                
                render.SDL_RenderCopy(renderer, parts_sprite.texture, src_rect, dst_rect)

    units_sprite = interface.gSurfaces[interface.SURF_UNITS]
    if units_sprite and stage.pack.eve:
        current_game_name = editor.game_manager.get_current_game().name
        entity_pos_scale = editor.tileWidth2 // 2 if "kero" in current_game_name or "11x" in current_game_name else editor.tileWidth
        
        src_rect = SDL_Rect(0, 0, editor.tileWidth2, editor.tileWidth2)
        dst_rect = SDL_Rect(0, 0, editor.tileWidth2, editor.tileWidth2)

        for entity in stage.pack.eve.units:
            src_rect.x = (entity.type1 % 16) * editor.tileWidth2
            src_rect.y = (entity.type1 // 16) * editor.tileWidth2
            dst_rect.x = offset_x + (entity.x * entity_pos_scale)
            dst_rect.y = offset_y + (entity.y * entity_pos_scale)
            render.SDL_RenderCopy(renderer, units_sprite.texture, src_rect, dst_rect)

def _load_stage_for_export(editor, stage_name):
    """Loads a stage for the export process without adding it to the main editor list."""
    if not stage_name:
        return None
    try:
        pack = editor.format_manager.load_stage(stage_name, editor.stage_table)
        stage_prj = StagePrj(stage_name, pack, editor.tileWidth)
        if stage_prj.load():
            return stage_prj
        return None
    except (ValueError, FileNotFoundError, NotImplementedError):
        return None

def _run_export_pass(editor, map_names_to_process, output_filename):
    """
    Loads a given list of map names, then traverses and stitches all of them into a single image,
    handling disconnected components.
    """
    if not map_names_to_process:
        print(f"No map names provided for pass '{output_filename}'. Skipping.")
        return
        
    renderer = interface.gRenderer.sdlrenderer
    
    # --- PHASE 1: Pre-load all maps for this pass ---
    print(f"\n--- Starting Export Pass for {output_filename} ---")
    print(f"Pre-loading {len(map_names_to_process)} maps...")
    stage_cache = {}
    for name in map_names_to_process:
        stage = _load_stage_for_export(editor, name)
        if stage:
            stage_cache[name] = stage
        else:
            print(f"  -> Failed to load '{name}'.")

    if not stage_cache:
        print("No maps could be loaded for this pass. Skipping.")
        return

    # --- PHASE 2: Traverse all components and build a collision-free layout ---
    map_positions = {}
    placed_rects = {}
    unplaced_maps = set(stage_cache.keys())

    while unplaced_maps:
        start_stage_name = unplaced_maps.pop()
        
        current_offset_x = 0
        if placed_rects:
            current_offset_x = max(r.x + r.w for r in placed_rects.values())

        primary_queue = deque([(start_stage_name, None, None)])
        left_queue = deque()
        visited_this_component = {start_stage_name}

        print(f"Starting new component traversal from '{start_stage_name}'...")
        
        while primary_queue or left_queue:
            if not primary_queue:
                if left_queue: primary_queue.append(left_queue.popleft())
                else: break

            name, parent_name, direction = primary_queue.popleft()
            
            stage = stage_cache.get(name)
            if not stage: continue
            
            current_w = stage.pack.layers[0].width * editor.tileWidth
            current_h = stage.pack.layers[0].height * editor.tileWidth

            if parent_name is None:
                px, py = current_offset_x, 0
            else:
                parent_w = stage_cache[parent_name].pack.layers[0].width * editor.tileWidth
                parent_h = stage_cache[parent_name].pack.layers[0].height * editor.tileWidth
                parent_x, parent_y = map_positions[parent_name]

                if direction == "right": px, py = parent_x + parent_w, parent_y
                elif direction == "left": px, py = parent_x - current_w, parent_y
                elif direction == "down": px, py = parent_x, parent_y + parent_h
                elif direction == "up": px, py = parent_x, parent_y - current_h
            
            while True:
                collided = False
                proposed_rect = SDL_Rect(px, py, current_w, current_h)
                for existing_rect in placed_rects.values():
                    if sdl2.SDL_HasIntersection(proposed_rect, existing_rect):
                        collided = True
                        if direction in ["right", "left"]: py = existing_rect.y + existing_rect.h
                        else: px = existing_rect.x + existing_rect.w
                        break
                if not collided: break

            map_positions[name] = (px, py)
            placed_rects[name] = SDL_Rect(px, py, current_w, current_h)
            print(f"Placed map '{name}' at pixel coordinates ({px}, {py})")

            connections = { "left": stage.pack.left_field, "right": stage.pack.right_field, "up": stage.pack.up_field, "down": stage.pack.down_field }
            for dir_key, neighbor_name in connections.items():
                if neighbor_name in unplaced_maps and neighbor_name not in visited_this_component:
                    visited_this_component.add(neighbor_name)
                    if dir_key == "left":
                        left_queue.append((neighbor_name, name, dir_key))
                    else:
                        primary_queue.append((neighbor_name, name, dir_key))
        
        unplaced_maps.difference_update(visited_this_component)

    if not map_positions: return

    # --- PHASE 3: Calculate final canvas size ---
    min_x, min_y = min(r.x for r in placed_rects.values()), min(r.y for r in placed_rects.values())
    max_x, max_y = max(r.x + r.w for r in placed_rects.values()), max(r.y + r.h for r in placed_rects.values())
    total_width, total_height = max_x - min_x, max_y - min_y

    if total_width <= 0 or total_height <= 0: return

    # --- PHASE 4: Render the world map ---
    print(f"Creating composite texture of size {total_width}x{total_height}...")
    world_texture = render.SDL_CreateTexture(renderer, sdl2.SDL_PIXELFORMAT_RGBA8888, render.SDL_TEXTUREACCESS_TARGET, total_width, total_height)
    render.SDL_SetRenderTarget(renderer, world_texture)
    render.SDL_SetRenderDrawColor(renderer, 0, 0, 0, 255)
    render.SDL_RenderClear(renderer)

    for name, (px, py) in map_positions.items():
        stage = stage_cache[name]
        render_x, render_y = px - min_x, py - min_y
        map_w, map_h = stage.pack.layers[0].width * editor.tileWidth, stage.pack.layers[0].height * editor.tileWidth

        clip_rect = SDL_Rect(render_x, render_y, map_w, map_h)
        render.SDL_RenderSetClipRect(renderer, clip_rect)
        render.SDL_SetRenderDrawColor(renderer, stage.pack.bg_r, stage.pack.bg_g, stage.pack.bg_b, 255)
        render.SDL_RenderFillRect(renderer, clip_rect)
        _render_stage_to_renderer(editor, stage, renderer, render_x, render_y)
        render.SDL_RenderSetClipRect(renderer, None)
    
    # --- PHASE 5: Save to file ---
    world_surface = surface.SDL_CreateRGBSurfaceWithFormat(0, total_width, total_height, 32, sdl2.SDL_PIXELFORMAT_RGBA8888)
    render.SDL_RenderReadPixels(renderer, None, sdl2.SDL_PIXELFORMAT_RGBA8888, world_surface.contents.pixels, world_surface.contents.pitch)
    sdlimage.IMG_SaveJPG(world_surface, output_filename.encode('utf-8'), 100)
    print(f"Saved connected map as {output_filename}")
    surface.SDL_FreeSurface(world_surface)
    render.SDL_DestroyTexture(world_texture)
    render.SDL_SetRenderTarget(renderer, None)

def _export_separate_maps(editor):
    """Exports each loaded stage as an individual JPG file."""
    renderer = interface.gRenderer.sdlrenderer
    for stage in editor.stages:
        if not stage.pack.layers or not stage.pack.layers[0]: continue
        
        width = stage.pack.layers[0].width * editor.tileWidth
        height = stage.pack.layers[0].height * editor.tileWidth
        if width == 0 or height == 0: continue

        export_texture = render.SDL_CreateTexture(renderer, sdl2.SDL_PIXELFORMAT_RGBA8888, render.SDL_TEXTUREACCESS_TARGET, width, height)
        
        render.SDL_SetRenderTarget(renderer, export_texture)
        render.SDL_SetRenderDrawColor(renderer, stage.pack.bg_r, stage.pack.bg_g, stage.pack.bg_b, 255)
        render.SDL_RenderClear(renderer)
        _render_stage_to_renderer(editor, stage, renderer)
        
        export_surface = surface.SDL_CreateRGBSurfaceWithFormat(0, width, height, 32, sdl2.SDL_PIXELFORMAT_RGBA8888)
        render.SDL_RenderReadPixels(renderer, None, sdl2.SDL_PIXELFORMAT_RGBA8888, export_surface.contents.pixels, export_surface.contents.pitch)
        
        filename = os.path.join("export", f"{stage.stageName}.jpg")
        sdlimage.IMG_SaveJPG(export_surface, filename.encode('utf-8'), 100)
        print(f"Saved {filename}")

        surface.SDL_FreeSurface(export_surface)
        render.SDL_DestroyTexture(export_texture)
    
    render.SDL_SetRenderTarget(renderer, None)

def export_stages(editor):
    """Main entry point for the export feature."""
    print("Starting JPG export...")
    if not os.path.exists("export"):
        os.makedirs("export")
    
    try:
        if editor.export_connected_maps:
            current_game = editor.game_manager.get_current_game()
            stage_dir = os.path.join(current_game.base_path, current_game.get('data_path'), current_game.get('stage_path'))
            stage_ext = current_game.get('stage_ext')
            
            if not os.path.isdir(stage_dir):
                print(f"Error: Stage directory not found at '{stage_dir}'")
                return

            all_map_files = [f for f in os.listdir(stage_dir) if f.endswith(stage_ext)]
            maps_pass_0 = [os.path.splitext(f)[0] for f in all_map_files if f.startswith('0')]
            maps_pass_1 = [os.path.splitext(f)[0] for f in all_map_files if f.startswith('1')]
            
            _run_export_pass(editor, maps_pass_0, os.path.join("export", "connected_map_0.jpg"))
            _run_export_pass(editor, maps_pass_1, os.path.join("export", "connected_map_1.jpg"))
        else:
            _export_separate_maps(editor)
        print("Export finished successfully.")
    except Exception as e:
        print(f"An error occurred during export: {e}")