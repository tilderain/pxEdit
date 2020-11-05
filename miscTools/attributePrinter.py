import os
from bitstring import ConstBitStream

s = ConstBitStream(filename="../Kero Blaster/KeroBlaster orig.exe")
s.pos = s.find(bytearray.fromhex("0000000005000000000000000000000000000000000000000000000000000000"))[0]

def readEntityInfo():
	try:
		with open("../entityInfo.txt") as f:
			entityInfo = [line.split("@") for line in f.read().splitlines()]
			
	except(IOError, FileNotFoundError) as e:
		print("Error reading entityInfo! {}".format(e))
		return False
	return entityInfo

entityInfo = readEntityInfo()

for i in range(787):
	print("npc no: " + str(i))
	try:
		print(entityInfo[i][0])
	except:
		pass
	npcFunc, surf_no, rect1, rect2, rect3, rect4, byteE, byteF, byte10, byte11, byte12, byte13, word14, health, bonus, name = \
		s.readlist('uintle:32, uintle:16, uintle:16, uintle:16, uintle:16, uintle:16, uintle:8, uintle:8,\
	uintle:8,uintle:8,uintle:8,uintle:8,uintle:16,uintle:16,uintle:32,uintle:32')

	print(f"func {hex(npcFunc)}, surf ?{surf_no}, rect1 {rect1}, rect2 {rect2}, rect3 {rect3}, rect4{rect4}, {byteE}, {byteF}, {byte10}, {byte11}, {byte12}, \
{byte13}, {word14}, flags?{bin(health)}, bonus {bonus}, nameptr{hex(name)}")

	print("\n")