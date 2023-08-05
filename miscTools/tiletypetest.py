import pxMap
import os

def readEntityInfo():
	try:
		with open("../assist/attribute.txt") as f:
			tileinfo = f.read().splitlines()
			
	except(IOError, FileNotFoundError) as e:
		print("Error reading entityInfo! {}".format(e))
		return False
	return tileinfo

tileinfo = readEntityInfo()

memo = []

for file in sorted(os.listdir("../Kero Blaster/Resource/img/")):
	attr = pxMap.PxPackLayer()
	if not file.endswith(".pxattr"): continue
	print(file)
	attr.load("../Kero Blaster/Resource/img/" + file)
	

	for y in range(attr.height):
		for x in range(attr.width):
			memo.append(attr.tiles[y][x])

memo = list(set(memo))

print(memo)
for i in range(256):
	if i not in memo:
		try:
			print(i, tileinfo[i])
		except:
			pass

