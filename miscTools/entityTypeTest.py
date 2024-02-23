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

with open("../npcNames.txt") as f:
	npcNames = f.read().splitlines()


entityInfo = readEntityInfo()
memo = []
memo2 = []

for file in sorted(os.listdir("../Kero Blaster/rsc_k/field/")):
	pack = pxMap.PxPack()

	pack.load("../Kero Blaster/rsc_k/field/" + file)
	

	for o in pack.eve.units:
		memo.append(o.type1)
		if o.type1 == 107:
			print(file)
			print("wassap")
			print(entityInfo[o.type1][0])
		memo2.append(o.string)
'''
for file in sorted(os.listdir("./Pink Hour/rsc_p/field/")):
	pack = pxMap.PxPack()
	print(file)
	pack.load("./Pink Hour/rsc_p/field/" + file)
	

	for o in pack.eve.units:
		memo.append(o.type1)
		memo2.append(o.string)
		

for file in sorted(os.listdir("./Pink Heaven/rsc_p/field/")):
	pack = pxMap.PxPack()
	print(file)
	pack.load("./Pink Heaven/rsc_p/field/" + file)
	

	for o in pack.eve.units:
		memo.append(o.type1)
		memo2.append(o.string)'''

memo = list(set(memo))
memo2 = list(set(memo2))

#print(memo)
for i in range(256):
	if i not in memo:
		try:
#			print(entityInfo[i][0])
			pass
		except:
			pass


#print(memo2)

for name in npcNames:
	if name not in memo2:
		pass
		print(name)
