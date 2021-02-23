import pxMap
import struct

asdf = pxMap.PxPackLayer()
pxmapMagic = "pxMAP01\0"


f = open("./test.pxattr", 'wb')
f.write(bytes(pxmapMagic.encode("ascii")))
f.write(struct.pack("<H", 16))
f.write(struct.pack("<H", 16))
f.write(struct.pack("<B", 0))
for i in range(256):
	f.write(struct.pack("<B", i))