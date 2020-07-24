import io, mmap

#Variable-length midi stuff copy pasted from some place. Thank you open source contributors
 
def read_int(stream):
	return struct.unpack('<i', stream.read(4))[0]

# function for reading variable-length quantities from a byte stream
def vlq(stream):
	v = stream.read_byte()
	if v > 0x7f:
		return v + 0x80*(vlq(stream)-1)
	else:
		return v
		
def writeVarLength(i):
	'''Accept an input, and write a MIDI-compatible variable length stream
	
	The MIDI format is a little strange, and makes use of so-called variable
	length quantities. These quantities are a stream of bytes. If the most
	significant bit is 1, then more bytes follow. If it is zero, then the
	byte in question is the last in the stream
	'''
	input = int(i+0.5)
	output = [0,0,0,0]
	reversed = [0,0,0,0]
	count = 0
	result = input & 0x7F
	output[count] = result
	count = count + 1
	input = input >> 7
	while input > 0:
		result = input & 0x7F 
		result = result | 0x80
		output[count] = result
		count = count + 1
		input = input >> 7  

	reversed[0] = output[3]
	reversed[1] = output[2]
	reversed[2] = output[1]
	reversed[3] = output[0]
	return reversed[4-count:4]
				

#unused, unknown
dword0 = []

#x is in tiles, y is in mystery pixel units
x = []
y = []

#Entity ID
type1 = []
#additional info for entity, ex. music for music switcher
type2 = []

#spawned from children?
npcChild = [5, 12, 16, 17, 33, 34, 36, 50, 51, 52, 53, 55, 57, 62, 71, 77, 78, 79, 80, 82, 89, 95, 101, 103, 109, 110, 112, 113]
#total entity ids
num = 121

entityInfoName = "entityInfo.txt"
def readEntityInfo():
	with open(entityInfoName) as f:
		return f.read().splitlines()

entityInfo = readEntityInfo()

while(True):
	input()
	for i in range(6):
		f = open("./data/event"+str(i+1)+".pxeve", 'r+b')
		stream = mmap.mmap(f.fileno(), 0)
		stream.seek(0)
		count = vlq(stream)
		print("Entity count: ", count)
		
		for i in range(count):
			
			#laziness incoming
			#stream[stream.tell()] = 1
			buf = vlq(stream)
			dword0.append(buf)

			buf = vlq(stream)
			x.append(buf)

			buf = vlq(stream)
			y.append(buf)
			
			#replace entity value
			'''
			if i==0:
				stream[stream.tell()] = 19
			elif((num) not in npcChild):
				stream[stream.tell()] = num #// 5
			else:
				stream[stream.tell()] = 0
			#num += 1
			'''

			buf = vlq(stream)
			type1.append(buf)
			
			#replace entity id
			#stream[stream.tell()] = 5

			buf = vlq(stream)
			type2.append(buf)
		
		stream.close()
		f.close()
		#num += 1
	for i in range(len(type1)):
		print("X: {} Y: {} Type1: {} Extra: {}".format(x[i], 
													   y[i],
													   entityInfo[type1[i]],
													   type2[i]))
	num+=1
#type.sort()


		
#testBuffer = ""
#varTime = writeVarLength("127")
#for timeByte in varTime:
#	testBuffer = testBuffer + struct.pack('>B',timeByte)
#
