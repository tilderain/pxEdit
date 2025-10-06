import os

def apply_patch(file_path, patches):
    """Applies a series of find/replace patches to a file."""
    if not os.path.exists(file_path):
        print(f"File not found: {file_path}")
        return

    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()

        original_content = content
        for find_str, replace_str in patches:
            content = content.replace(find_str, replace_str)

        if content != original_content:
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)
            print(f"Patched: {file_path}")
        else:
            print(f"No changes needed for: {file_path}")

    except Exception as e:
        print(f"Error processing {file_path}: {e}")

# --- Patches for saver.py ---
saver_patches = [
    # 1. Define a new PxMapSave class specifically for writing Cave Story .pxm files with the correct header.
    (
"""class PxMapAttr:
    def __init__(self):
        self.width = 0
        self.height = 0
        self.tiles = []""",
"""class PxMapSave:
    def __init__(self):
        self.width = 0
        self.height = 0
        self.tiles = []

    def save(self, path):
        try:
            with open(path, 'wb') as f:
                # Write the required header for .pxm files
                f.write(b'PXM') # 3-byte magic number
                f.write(b'\\x01') # 1-byte dummy data

                # Write dimensions and tile data
                f.write(struct.pack("<h", self.width))
                f.write(struct.pack("<h", self.height))
                for y in self.tiles:
                    f.write(bytes(y))
        except (OSError, IOError) as e:
            print(f"Error while saving {path}: {e}")
            return False
        return True

class PxMapAttr:
    def __init__(self):
        self.width = 0
        self.height = 0
        self.tiles = []"""
    ),
    # 2. In the _save_cave_story_stage method, use the new PxMapSave class instead of PxMapAttr for saving the map.
    (
"""        # Save map data
        if len(stage.layers) > 0 and stage.layers[0]:
            pxm = PxMapAttr()
            pxm.width = stage.layers[0].width
            pxm.height = stage.layers[0].height
            pxm.tiles = stage.layers[0].tiles
            pxm.save(map_path)
            print(f"Saved map to {map_path}")""",
"""        # Save map data
        if len(stage.layers) > 0 and stage.layers[0]:
            pxm = PxMapSave() # Use the correct class for saving .pxm files
            pxm.width = stage.layers[0].width
            pxm.height = stage.layers[0].height
            pxm.tiles = stage.layers[0].tiles
            pxm.save(map_path)
            print(f"Saved map to {map_path}")"""
    )
]

# --- Apply all patches ---
print("--- Correcting Cave Story map saving logic in saver.py ---")
apply_patch("saver.py", saver_patches)
print("--- Patching complete ---")