import os
os.environ["PYSDL2_DLL_PATH"] = "./"
import sdl2.ext
import ctypes


def inResizeHitbox(mouse, window):
    """Checks if the mouse is in the resize handle area at the bottom of a window."""
    if not getattr(window, 'resizable', False):
        return False
    resize_handle_height = 8
    hitbox_y = window.y + window.h - resize_handle_height
    hitbox_x = window.x
    hitbox_w = window.w
    hitbox_h = resize_handle_height
    return inBoundingBox(mouse.x, mouse.y, hitbox_x, hitbox_y, hitbox_w, hitbox_h)

# --- ADD THIS ---
_path_cache = {}

def find_case_insensitive_path(directory, filename):
    """
    Finds a file in a directory regardless of case, caching the result.
    Returns the full path with the correct casing if found, otherwise the original path.
    """
    if not filename:
        return os.path.join(directory, "")
        
    cache_key = (directory.lower(), filename.lower())
    if cache_key in _path_cache:
        # Return cached path, even if it was None (not found)
        path = _path_cache[cache_key]
        return os.path.join(directory, filename) if path is None else path

    target_lower = filename.lower()
    try:
        for item in os.listdir(directory):
            if item.lower() == target_lower:
                result = os.path.join(directory, item)
                _path_cache[cache_key] = result
                return result
    except FileNotFoundError:
        pass # Directory doesn't exist
        
    _path_cache[cache_key] = None
    # If not found, return the original constructed path to allow for a standard FileNotFoundError
    return os.path.join(directory, filename)
# --- END OF ADDITION ---

def lazybin(intt, places=32):
#converts an int to binary str
	binr = bin(intt)
	binr = binr[2:]
	asdf = len(binr)
	mystr = ""
	for i in range(places-asdf):
		mystr += "0"
	mystr += binr
	return mystr
	bytei = int(mystr[-8:], 2)
	if bytei > 127:
		bytei -= 256
	return bytei


def getMouseState():
	#it just works
	mouse = sdl2.SDL_MouseButtonEvent()
	x,y = ctypes.c_int(0), ctypes.c_int(0)
	mouse.button = sdl2.SDL_GetMouseState(x, y)
	mouse.x, mouse.y = x.value, y.value

	return mouse

def getKeyState():
	keystate = sdl2.SDL_GetKeyboardState(None)
	return keystate

def inBoundingBox(x1, y1, x2, y2, w, h):
	if x1 >= x2 and y1 >= y2 \
		and x1 <= x2 + w and y1 <= y2 + h:
		return True
	return False

def inWindowBoundingBox(mouse, window):
	return inBoundingBox(mouse.x, mouse.y, window.x, window.y, window.w, window.h)

def inWindowElemBoundingBox(mouse, window, elem):
	return inBoundingBox(mouse.x - window.x, mouse.y - window.y, elem.x, elem.y, elem.w, elem.h)	

def inDragHitbox(mouse, window):
	return inBoundingBox(mouse.x, mouse.y, window.x + window.draghitbox[0], window.y + window.draghitbox[1], window.draghitbox[2], window.draghitbox[3] )
