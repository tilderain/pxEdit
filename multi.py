import socketserver
import socket
import threading
import const
import sys
import json

DEFAULT_PORT = 7777

PACKET_CONNECT = 1
PACKET_MOUSEPOS = 2
PACKET_TILEEDIT = 3
#with undostack
PACKET_SENDSTAGE = 4
PACKET_SENDPARTS = 5

VERSION_MAGIC = 10

BUFFER_SIZE = 1024

class PxEditServerHandler(socketserver.BaseRequestHandler):
	def handle(self):
		gxEdit = self.server.gxEdit
		while True:
			self.request.setblocking(1)
			try:
				data = self.request.recv(BUFFER_SIZE)
				if len(data) == BUFFER_SIZE:
					while True:
						try:
							self.request.setblocking(0)
							data += self.request.recv(BUFFER_SIZE)
						except:
							break
			except OSError as e:
				print(e)
				self.removePlayer()
				return
			data = data.decode("utf-8")
			datas = []

			while data.find("}") != -1:
				datas.append(data[0:data.find("}")+1])
				data = data[data.find("}")+1:]

			for data in datas:
				try:
					data = json.loads(data)
				except:
					print("Got invalid data..", data)
					continue

				if data["type"] == PACKET_CONNECT:
					gxEdit.players[self.playerId]["name"] = data["name"]
					ip = gxEdit.players[self.playerId]["ip"]

					print(data["name"] + " connected. (" + ip[0] + ":" + str(ip[1]) + ")")
					#TODO: send message to player
					if data["version"] != VERSION_MAGIC:
						print("but their version did not match. ", str(data["version"]))
						self.removePlayer()
						return

				elif data["type"] == PACKET_MOUSEPOS:
					gxEdit.players[self.playerId]["mousepos"] = data["x"], data["y"]
				elif data["type"] == PACKET_TILEEDIT:
					stage = gxEdit.stages[data["stage"]]
					stage.map.modify(data["tiles"])
					
					#TODO: UNDO
					gxEdit.tileRenderQueue.append((data["stage"], data["tiles"]))

					for _, player in gxEdit.players.items():
						serverSendPacket(data, player["sock"].request)
				else:
					print("unknown packet")
					print(data)
					self.removePlayer()
					return

	def setup(self):
		gxEdit = self.server.gxEdit
		self.playerId = gxEdit.playerId
		playerinfo = {}
		playerinfo["ip"] = self.client_address
		playerinfo["sock"] = self
		gxEdit.players[self.playerId] = playerinfo
		gxEdit.playerId +=1

	def removePlayer(self):
		gxEdit = self.server.gxEdit
		print(gxEdit.players[self.playerId]["name"] + " disconnected.")
		del gxEdit.players[self.playerId]

def clientMethod(gxEdit):
	sock = gxEdit.socket
	while True:
		try:
			sock.setblocking(1)
			data = sock.recv(BUFFER_SIZE)
			if len(data) == BUFFER_SIZE:
				while True:
					try:
						sock.setblocking(0)
						data += sock.recv(BUFFER_SIZE)
					except:
						break
		except OSError as e:
			print(e)
			return
		data = data.decode("utf-8")
		datas = []

		while data.find("}") != -1:
			datas.append(data[0:data.find("}")+1])
			data = data[data.find("}")+1:]
		for data in datas:
			try:
				data = json.loads(data)
			except:
				print("Got invalid data..", data)
				continue
			if data["type"] == PACKET_TILEEDIT:
				stage = gxEdit.stages[data["stage"]]
				stage.map.modify(data["tiles"])
				
				#TODO: UNDO
				gxEdit.tileRenderQueue.append((data["stage"], data["tiles"]))

		

class PxEditServer(socketserver.ThreadingTCPServer):
	pass

def hostButtonAction(window, elem, gxEdit):
	if gxEdit.socket:
		return
	paramName = window.elements["paramName"].text
	#TODO:
	#if paramName == "":
	#	return

	paramIP = window.elements["paramIP"].text
	paramPort = window.elements["paramPort"].text
	try:
		port = int(paramPort)
	except:
		port = DEFAULT_PORT

	try:
		sock = socketserver.ThreadingTCPServer((paramIP, port), PxEditServerHandler)
	except OSError as e:
		print(e)
		return
	gxEdit.socket = sock
	gxEdit.multiplayerState = const.MULTIPLAYER_HOST

	#TODO: ?!@?!@?!??
	gxEdit.socket.gxEdit = gxEdit

	gxEdit.socket_thread = threading.Thread(target=gxEdit.socket.serve_forever)
	gxEdit.socket_thread.daemon = True
	gxEdit.socket_thread.start()

	window.visible = False

	print("Now hosting!")

def serverSendPacket(packet, sock):
	try:
		data = json.dumps(packet)
		sock.sendall(bytes(data,encoding="utf-8"))
		return True
	except OSError as e:
		print(e)
		return False

def sendPacket(gxEdit, packet):
	try:
		data = json.dumps(packet)
		gxEdit.socket.sendall(bytes(data,encoding="utf-8"))
	except OSError as e:
		print(e)
		gxEdit.multiplayerState = const.MULTIPLAYER_NONE
		gxEdit.socket = None
		gxEdit.socket_thread = None
		return

def sendConnectPacket(gxEdit, name, version):
	packet = {"type":PACKET_CONNECT, "name": name, "version": version}
	sendPacket(gxEdit, packet)

def sendMousePosPacket(gxEdit, x, y):
	packet = {"type":PACKET_MOUSEPOS, "x": x, "y": y}
	sendPacket(gxEdit, packet)
	
def sendTileEditPacket(gxEdit, curStage, tiles):
	packet = {"type":PACKET_TILEEDIT, "stage":curStage, "tiles": tiles}
	sendPacket(gxEdit, packet)

def connectButtonAction(window, elem, gxEdit):
	if gxEdit.socket:
		return
	paramName = window.elements["paramName"].text
	#TODO:
	#if paramName == "":
	#	return

	paramIP = window.elements["paramIP"].text
	paramPort = window.elements["paramPort"].text
	try:
		port = int(paramPort)
	except:
		port = DEFAULT_PORT

	if paramIP == "":
		ip = "localhost"
	else:
		ip = paramIP

	sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	try:
		sock.connect((ip, port))
	except OSError as e:
		print(e)
		return
	gxEdit.socket = sock
	gxEdit.multiplayerState = const.MULTIPLAYER_CLIENT

	sendConnectPacket(gxEdit, paramName, VERSION_MAGIC)

	gxEdit.socket_thread = threading.Thread(target=clientMethod, args=([gxEdit]))
	gxEdit.socket_thread.daemon = True
	gxEdit.socket_thread.start()

	window.visible = False

	print("Connected.")

	