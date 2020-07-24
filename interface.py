
import sdl2.ext

def initGraphics():
	window = sdl2.ext.Window("Doctor's Garage", size=(640, 480), flags=sdl2.SDL_WINDOW_RESIZABLE)
	window.show()
	renderer = sdl2.ext.Renderer(window, flags=sdl2.SDL_RENDERER_SOFTWARE)
	sprfactory = sdl2.ext.SpriteFactory(sdl2.ext.TEXTURE, renderer=renderer)
	uifactory = sdl2.ext.UIFactory(sprfactory)

	return window

    scaleFactor = (window.size[1] // tileWidth // gxEdit.magnification)

class Interface:
    def __init__(self):
        self.tileScale = 1
	    self.magnification = 3
	    self.tileWidth = 16 * self.tileScale

    def clampMagnification():
		if gxEdit.magnification <= 0:
			gxEdit.magnification = 1


class UIWindow:
	#Draggable area, relative to the origin.
		
	pass



		def renderTiles(stage):
			map = stage.map
			for i, tile in enumerate(map.tiles):
				
				y = i // map.width
				if y < stage.scroll:
					continue
				if (y - stage.scroll) * tileWidth > window.size[1]:	
					continue
				y -= stage.scroll

				x = i % map.width
				dstx = x * tileWidth
				dsty = y * tileWidth

				x = tile % 16 #the magic number so that each 4 bits in a byte corresponds to the x, y position in the tileset
				y = tile // 16
				srcx = x * tileWidth
				srcy = y * tileWidth

				mag = gxEdit.magnification
				srcrect = (srcx, srcy, tileWidth, tileWidth)
				dstrect = (dstx*mag, dsty*mag, tileWidth*mag, tileWidth*mag)
				#srcrect = 
				renderer.copy(stage.parts, srcrect=srcrect, dstrect=dstrect)

		def renderEntities(stage):
			eve = stage.eve.get()
			for o in eve:
				
				y = o.y
				if y < stage.scroll:
					continue
				if (y - (stage.scroll)) > window.size[1]:	
					continue
				y -= stage.scroll * 2
				x = o.x
				dstx = x * (tileWidth // 2)
				dsty = y * (tileWidth // 2)

				x = o.type1 % 16 #row size in units.bmp
				y = o.type1 // 16
				srcx = x * tileWidth
				srcy = y * tileWidth

				mag = gxEdit.magnification
				srcrect = (srcx, srcy, tileWidth, tileWidth)
				dstrect = (dstx*mag, dsty*mag, tileWidth*mag, tileWidth*mag)

				renderer.copy(gxEdit.units, srcrect=srcrect, dstrect=dstrect)

				#entity borders
				'''
				dstrect = (dstx+tileWidth, dsty, dstx, dsty,
								dstx, dsty, dstx, dsty+tileWidth)
				dstrect2 = (dstx+tileWidth, dsty+tileWidth, dstx+tileWidth, dsty,
								dstx+tileWidth, dsty+tileWidth, dstx, dsty+tileWidth)
				dstrect = [i * mag for i in dstrect]
				dstrect2 = [i * mag for i in dstrect2]

				renderer.draw_line(dstrect, color=colorOrange)
				renderer.draw_line(dstrect2, color=colorOrangeDark)'''