import io, os, struct
from ctypes import c_short
class PxMapAttr: #use the same class for both
	def __init__(self):
		self.width = None
		self.height = None
		self.tiles = []
	def load(self, path):
		try:
			f = open(path, 'rb')
			data = f.read()
		except (OSError, IOError) as e:
			print("Error while opening {}: {}".format(path, e))
			return False
		
		self.width = int.from_bytes(data[0:2], byteorder='little')
		self.height = int.from_bytes(data[2:4], byteorder='little')
		for i in range(self.height):
			self.tiles.append(list( data[4+i*self.width:\
									4+(i*self.width)+self.width] ))
		return True
		
	def save(self, path):
		try:
			f = open(path, 'wb')
		except (OSError, IOError) as e:
			print("Error while opening {}: {}".format(path, e))
			return False
		else:
			f.write(struct.pack("<h", self.width))
			f.write(struct.pack("<h", self.height))
			for y in self.tiles:
				f.write(bytes(y))

			return True
		
	def modify(self, tiles):
		#[[x,y], [x, y]]

		for tile in tiles:
			#convert a spritesheet tile index to its representation in the tile array
			if tile[0][0] >= self.width: continue
			if tile[0][1] >= self.height: continue
			x = tile[1][0]
			y = tile[1][1] * 16
			
			self.tiles[tile[0][1]][tile[0][0]] = x+y
	def resize(self, width, height):
		pass
	def get(self):
		return self.tiles[:]

