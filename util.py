
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
