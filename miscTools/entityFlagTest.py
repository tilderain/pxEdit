import pxMap
import os

def readEntityInfo():
	try:
		with open("../entityInfo.txt") as f:
			entityInfo = [line.split("@") for line in f.read().splitlines()]
			
	except(IOError, FileNotFoundError) as e:
		print("Error reading entityInfo! {}".format(e))
		return False
	return entityInfo

entityInfo = readEntityInfo()

for file in sorted(os.listdir("../Kero Blaster/rsc_k/field/")):
	pack = pxMap.PxPack()
	print(file)
	pack.load("../Kero Blaster/rsc_k/field/" + file)
	

	for o in pack.eve.units:
		if not o.bits & 1:
			print("1")
			print(entityInfo[o.type1][0])
