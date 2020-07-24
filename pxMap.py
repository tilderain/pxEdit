import io, os, struct
from ctypes import c_short
class PxMapAttr: #use the same class for both
	def __init__(self):
		self.width = None
		self.height = None
		self.tiles = []
		pass
	def load(self, path):
		try:
			f = open(path, 'rb')
			data = f.read()
		except (OSError, IOError) as e:
			print("Error while opening {}: {}".format(path, e))
			return False
		
		self.width = int.from_bytes(data[0:2], byteorder='little')
		self.height = int.from_bytes(data[2:4], byteorder='little')
		self.tiles = list(data[4:])
		
	def save(self, path):
		try:
			f = open(path, 'wb')
		except (OSError, IOError) as e:
			print("Error while opening {}: {}".format(path, e))
			return False
		else:
			f.write(struct.pack("<h", self.width))
			f.write(struct.pack("<h", self.height))
			f.write(bytes(self.tiles))
		
	def modify(self, tiles):
		#[index, [x, y]]

		for tile in tiles:
			#convert a spritesheet tile index to its representation in the tile array
			if tile[0] >= len(self.tiles): continue
			x = tile[1][0]
			y = tile[1][1] * 16
			
			self.tiles[tile[0]] = x+y
	def resize(self, width, height):
		pass
	def get(self):
		return self.tiles[:]

