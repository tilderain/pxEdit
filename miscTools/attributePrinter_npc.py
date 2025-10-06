import os
import sys
from bitstring import ConstBitStream
from PIL import Image

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
sheets = ["wallpaper", "Background", "Middleground", "fuFixNPC", "CurrentNPCSheet", "fuFixChar", "fuFixPtcle", "Foreground", "button", "item", "localize", "item", "kerofont"]
styles = ["NULL", "Small (normal)", "Medium (normal)", "Large (normal)", "Small (black)", "Medium (black)", "Large (black)", "Droplet", "Foliage", "Fireball"]
for i in range(0x27A):#787
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
	npcFunc, surf_no, rect1, rect2, rect3, rect4, style, priority, unit_coll_w, unit_coll_h, map_coll_w, map_coll_h, health, coin, bonus, name = \
		s.readlist('uintle:32, uintle:16, uintle:16, uintle:16, uintle:16, uintle:16, uintle:8, uintle:8,\
	uintle:8,uintle:8,uintle:8,uintle:8,uintle:16,uintle:16,uintle:32,uintle:32')
	
	namestring = 0
	if name != 0:
		searchbase = name - image_base
		temppos = s.pos
		s.pos = searchbase * 8
		print(s.pos)
		sys.exit("")
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
	print(f"Function: {hex(npcFunc)}, Sprite surface: ?{sheets[surf_no]}, Rect X: {rect1}, Rect Y: {rect2}, Rect Width: {rect3}, Rect Height: {rect4},\nStyle: {styles[style]}, lkFU priority: {priority}, Unit Hitbox Width: {unit_coll_w}, Unit Hitbox Height: {unit_coll_h},\nMap Hitbox Width: {map_coll_w}, Map Hitbox Height: {map_coll_h}, HP: {health}, Coins: {coin}, Bonus: {bonus},\nName Pointer: {hex(name)}, Namestring: {namestring}")
	
#	print("\n")

	try:
		file = "../Kero Blaster/rsc_k/img/" + sheets[surf_no] + ".png"
		im = Image.open(file)
		width, height = im.size

		im2 = im.crop((rect1//2, rect2//2, rect1//2 + rect3//2, rect2//2 + rect4//2))
		im2.save("./img/" + str(i) + ".png")
	except Exception as e:
		print(e)
		pass
	
