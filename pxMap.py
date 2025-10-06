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
					# Use list.index() to find and replace the object
					try:
						idx = self.units.index(o)
						self.units[idx] = ent
					except ValueError:
						pass # Should not happen if 'o' is from self.units

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
		
	

class PxMapAttr: #use the same class for both
	def __init__(self):
		self.width = 0
		self.height = 0
		self.tiles = []
	
	def load(self, path):
		"""
		Loads tile data from a file, intelligently handling whether a
		'pxMAP01' header is present or not. Also handles the 1-byte
		type field present in Kero Blaster map/attribute formats.
		"""
		try:
			with open(path, 'rb') as f:
				data = f.read()
		except (OSError, IOError) as e:
			print("Error while opening {}: {}".format(path, e))
			return False
		
		offset = 0

		# Check if the file starts with the 8-byte pxMAP01 header.
		# Standalone .pxattr files do not have this header.
		if data.startswith(b"pxMAP01\0"):
			offset = 8
		
		try:
			# Read width and height from the correct starting position.
			self.width = int.from_bytes(data[offset:offset+2], byteorder='little')
			self.height = int.from_bytes(data[offset+2:offset+4], byteorder='little')

			# Ensure dimensions are sane before proceeding
			if self.width <= 0 or self.height <= 0:
				self.tiles = []
				return True

			# --- THE FIX ---
			# Kero Blaster's map/attribute format has a 1-byte 'type' field after the dimensions.
			# We must skip this byte to read the tile data correctly.
			data_start = offset + 5  # Was offset + 4

			self.tiles = [] # Clear any previous tile data
			for i in range(self.height):
				row_start = data_start + (i * self.width)
				row_end = row_start + self.width
				# Ensure we don't read past the end of the file data
				if row_end > len(data):
					print(f"Warning: Truncated data in {path} at row {i}. Padding with zeroes.")
					row_data = list(data[row_start:])
					row_data.extend([0] * (self.width - len(row_data)))
					self.tiles.append(row_data)
					break # Stop processing if data is truncated
				else:
					self.tiles.append(list(data[row_start:row_end]))

		except (struct.error, IndexError) as e:
			print(f"Error parsing data in {path}. File might be corrupt: {e}")
			self.width = 0
			self.height = 0
			self.tiles = []
			return False
			
		return True
		
	def save(self, path):
		"""Saves as a raw .pxattr file (without header)."""
		try:
			with open(path, 'wb') as f:
				f.write(struct.pack("<h", self.width))
				f.write(struct.pack("<h", self.height))
				for y in self.tiles:
					f.write(bytes(y))
		except (OSError, IOError) as e:
			print("Error while saving {}: {}".format(path, e))
			return False
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
		if width < 0 or height < 0: return

		new_tiles = []
		for y in range(height):
			if y >= self.height:
				# Add a new, empty row
				new_tiles.append([0] * width)
			else:
				# Copy and adjust an existing row
				row = self.tiles[y][:width]
				if width > self.width:
					row.extend([0] * (width - self.width))
				new_tiles.append(row)
			
		self.tiles = new_tiles
		self.width = width
		self.height = height

	def shift(self, x, y, wrap):
		pass
		
	def get(self):
		return self.tiles[:]

# This PxMap class is for loading Cave Story .pxm files.
class PxMap:
    def __init__(self):
        self.width = 0
        self.height = 0
        self.tiles = []

    def load(self, path, printError=True):
        try:
            with open(path, 'rb') as f:
                magic = f.read(3)
                if magic != b'PXM':
                    raise ValueError(f"Invalid PXM file format in {path}")
                f.read(1) # Skip one dummy byte
                width_bytes = f.read(2)
                height_bytes = f.read(2)
                self.width = int.from_bytes(width_bytes, byteorder='little')
                self.height = int.from_bytes(height_bytes, byteorder='little')
                data = f.read(self.width * self.height)
                self.tiles = []
                for i in range(self.height):
                    start = i * self.width
                    end = start + self.width
                    self.tiles.append(list(data[start:end]))
        except (OSError, IOError) as e:
            if printError:
                print("Error while opening {}: {}".format(path, e))
            return False
        except (ValueError, struct.error) as e:
            print(f"Error parsing map file {path}: {e}")
            return False
        return True

    def save(self, path):
        """Saves tile data to a Cave Story .pxm file."""
        try:
            with open(path, 'wb') as f:
                # Write the PXM header and version/dummy byte
                f.write(b'PXM\x01')
                
                # Write width and height as 2-byte little-endian integers
                f.write(struct.pack("<h", self.width))
                f.write(struct.pack("<h", self.height))
                
                # Write the tile data row by row
                if self.width * self.height > 0:
                    for row in self.tiles:
                        f.write(bytes(row))
        except (OSError, IOError) as e:
            print(f"Error while saving {path}: {e}")
            return False
        return True