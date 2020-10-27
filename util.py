
import sdl2.ext
import ctypes

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
