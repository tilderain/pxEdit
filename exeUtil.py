#the extra bytes are for integrity
exeDecodeEnabledBytes = 0x6A01A1F4C7440050
exeDecodeDisabledBytes = 0x6A00A1F4C7440050

imageBase = 0x401000
decodeOffset = 0x41D046
spriteExtOffset = 0x43C46C

extPximgBytes = b"%s.pximg"
extBmpBytes = b"%s.bmp\0"

gameName = "pxGame.exe"

class ExeUtils:
	pass

def checkExeDecodePatched(path):
	f = open(gamePath + gameName, 'r+b')
	stream = mmap.mmap(f.fileno(), 0)

	enabled = False
	#An int is passed to InitDirectDraw in WinMain that tells the game whether to decode the images or not.

	
	
	#If we get neither, either the user is running some crazy hacked version of the game or it's not Guxt


	stream.close()
	f.close()
	return enabled
def patchExeDecode():
	pass


'''

import os


hash_a = 0
hash_b = 0
def Decoder(h, a, b):
    global hash_a
    global hash_b
    hash_a = a
    hash_b = b
    img_height = 0
    img_height = h
    line_indexes = []
    for i in range(img_height):
        line_indexes.append(-1)

    current_line = 0
    cycle_count = 0
    for i in range(img_height):
        cycle_count = (shuffle() >> 8) & 0xFF
        if cycle_count == 0:
            cycle_count = 1
        while True:
            current_line = (current_line + 1) % img_height
            if line_indexes[current_line] == -1:
                cycle_count -= 1
            if cycle_count == 0:
                break

        line_indexes[current_line] = i
    
    return line_indexes

def rshift(val, n): return (val % 0x100000000) >> n

def lazybin(intt):
#converts an int to binary
    binr = bin(intt)
    binr = binr[2:]
    asdf = len(binr)
    mystr = ""
    for i in range(32-asdf):
        mystr += "0"
    mystr += binr
    bytei = int(mystr[-8:], 2)
    if bytei > 127:
        bytei -= 256
    return bytei

def shuffle():
    global hash_a
    global hash_b
    tmp = (hash_a + hash_b) & 0xFFFF
    low =  lazybin(tmp)
    high = lazybin((rshift(tmp, 8)))
    result = (low << 8)
    result |= high & 0xFF
    hash_b = hash_a
    hash_a = result
    return result

from PIL import Image
for file in os.listdir("C:/Users/square/Desktop/cave/guxtimgops"):
	print "hi"
	if file.endswith(".bmp"):
		im = Image.open(file)
		width, height = im.size
		indexes = Decoder(height, 0x4444, 0x8888)
		pixels = im.load() # this is not a list
		
		im2 = im.copy()
		pixels2 = im2.load()
		for i in range(len(indexes)):
			for x in range(width):
				pixels2[x, i] = pixels[x, indexes[i]]
		im2.save(file)
'''
	
	
	