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

image_base = 0x401200                          #current npc
sheets = ["wallpaper", "/2", "/1", "fuFixNPC", "", "fuFixChar", "fuFixPtcl", "/0", "button", "item", "localize", "item", "kerofont"]
for i in range(767):#787
	print("npc no: " + str(i))
	info = ""
	info2 = ""
	try:
		#print(entityInfo[i][0])
		info = entityInfo[i][0][6:]
		info2 = entityInfo[i][2]
		pass
	except:
		pass
	npcFunc, surf_no, rect1, rect2, rect3, rect4, byteE, byteF, byte10, byte11, byte12, byte13, word14, coin, bonus, name = \
		s.readlist('uintle:32, uintle:16, uintle:16, uintle:16, uintle:16, uintle:16, uintle:8, uintle:8,\
	uintle:8,uintle:8,uintle:8,uintle:8,uintle:16,uintle:16,uintle:32,uintle:32')
	
	namestring = 0
	if name != 0:
		searchbase = name - image_base
		temppos = s.pos
		s.pos = searchbase * 8
		namestring = bytearray.fromhex(str(s.readto("0x00", bytealigned=True))[2:]).decode()[:-1]
		s.pos = temppos

		#print(f'<rollYourOwnSprite name="{namestring}" tileset="{sheets[surf_no]}" x="{rect1//8}" y="{rect2//8}" numXTiles="{rect3//8}" numYTiles="{rect4//8}"/>')
		#continue
	rectdivisor = 8
	tiledivisor = 8
	if surf_no == 5:
		rectdivisor = 8
		tiledivisor = 8
	#print(f'<entity id="{str(i)}" name="{info}" description="{info2}">')
	#print(f'	<tile tileset="{sheets[surf_no]}" x="{rect1//rectdivisor}" y="{rect2//rectdivisor}" numXTiles="{rect3//tiledivisor}" numYTiles="{rect4//tiledivisor}"/>')
	#print(f'</entity>')
	print(f"func {hex(npcFunc)}, surf ?{surf_no}, rect1 {rect1}, rect2 {rect2}, rect3 {rect3}, rect4 {rect4}, {byteE}, {byteF}, {byte10}, {byte11}, {byte12}, \
#{byte13}, {word14}, coin {coin}, bonus {bonus}, nameptr{hex(name)}, namestring {namestring}")
	
#	print("\n")

