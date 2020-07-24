import io, mmap
import math, itertools
from dataclasses import dataclass
# function for reading variable-length quantities from a byte stream
# from georgealways/pxtone.py

#TODO: replace tihs with my own function

def vlq(stream):
	v = stream.read_byte()
	if v > 0x7f:
		return v + 0x80*(vlq(stream)-1)
	else:
		return v

def writeVarLength(i):
	output = []
	size = math.ceil(i.bit_length() / 8) + 1 #bytes to encode int plus one addional byte of overhead

	while size > 0:
		if(i >= 0x80):
			output.append((i & 0x7f) | 0x80)
			i = i >> 7
			size -= 1
		else:
			output.append(i)
			break
	return output
				

@dataclass
class PxEveEntity:
#unused, unknown
	unused: int = 1
#x is in halftiles, y is in mystery pixel units
	x: int = 0
	y: int = 0
#Entity ID
	type1: int = 0
#additional info for entity, ex. music for music switcher
	type2: int = 0
#editor exclusive, unique id for distinguishment, ala cave story
	id: int = 0

#EntityInfo2
#specific bgm name

def printEntity(o: PxEveEntity, entityInfo):
	print("X: {} Y: {} Type1: {} Extra: {} ID: {}".format(o.x, 
												   o.y,
												   entityInfo[o.type1],
												   o.type2,
												   o.id))

class PxEve:
	def __init__(self):
		self._entities = []
		self._count = 0

	def save(self, path):
		#vanilla order is y descending, x ascending, but it's not neccesary
		output = []
		output.append(writeVarLength( len( self._entities ) ))
		for o in self._entities:
			output.append(writeVarLength(o.unused))
			output.append(writeVarLength(o.x))
			output.append(writeVarLength(o.y))
			output.append(writeVarLength(o.type1))
			output.append(writeVarLength(o.type2))

		#unwrap the array
		output = list(itertools.chain(*output))

		try:
			f = open(path, 'wb')
		except (OSError, IOError) as e:
			print("Error while opening {}: {}".format(path, e))
			return False
		else:
			f.write(bytes(output))

		return True

	def load(self, path): #readEntities
		try:
			f = open(path, 'rb')
			stream = mmap.mmap(f.fileno(), 0, access=mmap.ACCESS_READ)
		except (OSError, IOError) as e:
			print("Error while opening {}: {}".format(path, e))
			return False

		stream.seek(0)

		entityCount = vlq(stream)
		print("Entity count: ", entityCount)

		entities = []

		for __  in range(entityCount):
			o = PxEveEntity(1, 0, 0, 0, 0, self._count)
			self._count += 1

			o.unused = vlq(stream)
			o.x = vlq(stream)
			o.y = vlq(stream)
			o.type1 = vlq(stream)
			o.type2 = vlq(stream)

			entities.append(o)
		stream.close()
		f.close()
		self._entities = entities
		return True
		
	def add(self, x, y, type1, type2):
		o = PxEveEntity(0, x, y, type1, type2, self._count)
		self._count += 1
		self._entities.append(o)
		
	def remove(self, ids):
		for id in ids:
			for o in self._entities:
				if o.id == id:
					self._entities.remove(o)
					break
	
	def modify(self, ids, x, y, type1, type2):
		for num in ids:
			for o in self._entities:
				if num == o.id:
					self._entities[self._entities.index(o)] = PxEveEntity(1, x, y, type1, type2, num)
					break
		pass

	def move(self, ids, x, y):
		pass

	def get(self):
		return self._entities[:]

