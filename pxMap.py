import io, os, struct
import mmap
from ctypes import c_short

def writePixelString(fp, string):
	length = len(string.encode("shift-jis"))
	fp.write(struct.pack("<B", length))
	fp.write(bytes(string.encode("shift-jis")))

def readPixelString(stream):
	length = stream.read_byte()
	if length >= 32: return ""
	string = stream.read(length)
	return string.decode("shift-jis")

def readInt(stream, length):
	return int.from_bytes(stream.read(length), byteorder="little")

pxmapMagic = "pxMAP01\0"

class PxPackUnit:
	def __init__(self, bits, code_char, param2, x, y, flag, string, id):
		self.bits = bits
		self.type1 = code_char
		self.param2 = param2
		self.x = x
		self.y = y
		self.flag = flag
		self.string = string
		self.id = id

class PxEve:
	def __init__(self):
		self.units = []
		self._count = 0

	def replace(self, ents):
		for ent in ents:
			for o in self.units:
				if ent.id == o.id:
					self.units[self.units.index(o)] = ent

	def move(self, ids, xoffset, yoffset):
		for num in ids:
			for o in self.units:
				if num == o.id:
					o.x += xoffset
					o.y += yoffset

	def modify(self, ids, x=None, y=None, code_char=None, bits=None, param2=None, flag=None, string=None):
		#TODO: is this really neccesary?
		for num in ids:
			for o in self.units:
				if num == o.id:
					if x != None: o.x = x
					if y != None: o.y = y
					if code_char != None: o.type1 = code_char
					if bits != None: o.bits = bits
					if param2 != None: o.param2 = param2
					if flag != None: o.flag = flag
					if string != None: o.string = string
					break
	def remove(self, ids):
		for id in ids:
			for o in self.units:
				if o.id == id:
					self.units.remove(o)
					break
			
	def add(self, x, y, code_char, bits=0, param2=0, flag=0, string=""):
		o = PxPackUnit(bits|1, code_char, param2, x, y, flag, string, self._count)
		self._count += 1
		self.units.append(o)
		return o

	def saveToPack(self, stream):
		pass
		
	
class PxPackLayer:
	def __init__(self):

		self.partsName = None
		self.scrolltype = 0
		self.visibility = 0

		#max for an attr is 16*16
		self.width = 16
		self.height = 16
		self.type = 0


		self.tiles = [[0] * self.width] * self.height
	
	def loadFromPack(self, stream):
		self.tiles = []

		#TODO: verify header minus numbers
		stream.read(8) #PXMAP01
		self.width = readInt(stream, 2)
		self.height = readInt(stream, 2)

		if self.width * self.height == 0: return True

		self.type = readInt(stream, 1)
		if self.type == 0:
			for i in range(self.height):
				byt = stream.read(self.width)
				self.tiles.append([tile for tile in byt])
			return True
	
	def load(self, path): #readEntities
		try:
			f = open(path, 'rb')
			stream = mmap.mmap(f.fileno(), 0, access=mmap.ACCESS_READ)
		except (OSError, IOError) as e:
			print("Error while opening {}: {}".format(path, e))
			return False

		return self.loadFromPack(stream)

	def saveToPack(self, f):
		f.write(bytes(pxmapMagic.encode("ascii")))
		f.write(struct.pack("<H", self.width))
		f.write(struct.pack("<H", self.height))

		if self.width * self.height == 0: return

		f.write(struct.pack("<B", self.type))

		if self.type == 0:
			for y in self.tiles:
				f.write(bytes(y))

	def save(self, path):
		try:
			f = open(path, 'wb')
		except (OSError, IOError) as e:
			print("Error while saving {}: {}".format(path, e))
			return False
		else:
			self.saveToPack(f)

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
		if width <= 0: return
		if height <= 0: return

		tiles = []
		for y in range(height):
			if y > self.height-1:
				tiles.append([0] * width)
			else:
				tiles.append( self.tiles[y][:width] + [0]*(width - self.width))
			
		self.tiles = tiles

		self.width = width
		self.height = height
		
pxpackMagic = "PXPACK121127a**\0"

class PxPack:
	def __init__(self):
		self.description = None
		self.left_field = None
		self.right_field = None
		self.up_field = None
		self.down_field = None

		self.spritesheet = None

		self.area_x = None
		self.area_y = None

		self.area_no = None

		self.bg_r = None
		self.bg_g = None 
		self.bg_b = None

		self.layers = []

		self.eve = PxEve()

	def load(self, path): #readEntities
		try:
			f = open(path, 'rb')
			stream = mmap.mmap(f.fileno(), 0, access=mmap.ACCESS_READ)
		except (OSError, IOError) as e:
			print("Error while opening {}: {}".format(path, e))
			return False

		LAYER_COUNT = 3

		#TODO: verify header
		stream.seek(16)

		self.description = readPixelString(stream)
		self.left_field = readPixelString(stream)
		self.right_field = readPixelString(stream)
		self.up_field = readPixelString(stream)
		self.down_field = readPixelString(stream)
		self.spritesheet = readPixelString(stream)

		self.area_x = readInt(stream, 2)
		self.area_y = readInt(stream, 2)
		self.area_no = readInt(stream, 1)

		self.bg_r = readInt(stream, 1)
		self.bg_g = readInt(stream, 1)
		self.bg_b = readInt(stream, 1)

		for i in range(LAYER_COUNT):
			layer = PxPackLayer()

			layer.partsName = readPixelString(stream)
			layer.visibility = readInt(stream, 1)
			layer.scrolltype = readInt(stream, 1)
			self.layers.append(layer)

		for i in range(LAYER_COUNT):
			layer = self.layers[i]
			layer.loadFromPack(stream)
		
		entityCount = readInt(stream, 2)
		for i in range(entityCount):
			bits = readInt(stream, 1)
			code_char = readInt(stream, 1)
			param2 = readInt(stream, 1)

			x = readInt(stream, 2)
			y = readInt(stream, 2)
			flag = readInt(stream, 2)

			string = readPixelString(stream)
			self.eve.units.append(PxPackUnit(bits,code_char,param2,x,y,flag,string, self.eve._count))
			self.eve._count += 1

		stream.close()
		f.close()
		return True
		
	def save(self, path):
		try:
			f = open(path, 'wb')
		except (OSError, IOError) as e:
			print("Error while opening {}: {}".format(path, e))
			return False
		else:
			f.write(bytes(pxpackMagic.encode("ascii")))
			writePixelString(f, self.description)
			writePixelString(f, self.left_field)
			writePixelString(f, self.right_field)
			writePixelString(f, self.up_field)
			writePixelString(f, self.down_field)
			writePixelString(f, self.spritesheet)

			f.write(struct.pack("<H", self.area_x))
			f.write(struct.pack("<H", self.area_y))
			f.write(struct.pack("<B", self.area_no))

			f.write(struct.pack("<B", self.bg_r))
			f.write(struct.pack("<B", self.bg_g))
			f.write(struct.pack("<B", self.bg_b))

			LAYER_COUNT = 3

			for i in range(LAYER_COUNT):
				layer = self.layers[i]

				writePixelString(f, layer.partsName)
				f.write(struct.pack("<B", layer.visibility))
				f.write(struct.pack("<B", layer.scrolltype))
			for i in range(LAYER_COUNT):
				self.layers[i].saveToPack(f)

			f.write(struct.pack("<H", len(self.eve.units)))
			for o in self.eve.units:
				f.write(struct.pack("<B", o.bits))
				f.write(struct.pack("<B", o.type1))
				f.write(struct.pack("<B", o.param2))

				f.write(struct.pack("<h", o.x))
				f.write(struct.pack("<h", o.y))
				f.write(struct.pack("<H", o.flag))
				writePixelString(f, o.string)

			f.close()

			return True
		

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

			f.close()

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
		if width <= 0: return
		if height <= 0: return

		tiles = []
		for y in range(height):
			if y > self.height-1:
				tiles.append([0] * width)
			else:
				tiles.append( self.tiles[y][:width] + [0]*(width - self.width))
			
		self.tiles = tiles

		self.width = width
		self.height = height

	def shift(self, x, y, wrap):
		pass
		
	def get(self):
		return self.tiles[:]

