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

#send stage with undostack
PACKET_SENDSTAGE = 4
PACKET_SENDPARTS = 5
PACKET_MOUSEPOSFORCLIENT = 6
PACKET_REQUESTUNDO = 7
PACKET_REQUESTREDO = 8
PACKET_TILESTART = 9
PACKET_TILEEND = 10

PACKET_DISCONNECT_REASON = 11

REASON_KICKED = "You were kicked from the server"
REASON_OUTDATED = "Your version did not match the server's."
REASON_NAME = "You have an invalid name."
REASON_NAME_EXISTS = "That name is already in use."


VERSION_MAGIC = 10

BUFFER_SIZE = 1024

def packetAcceptor(gxEdit, sock):
	while True:
		sock.setblocking(1)
		try:
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
			return None
		data = data.decode("utf-8")
		datas = []

		while data.find("}") != -1:
			datas.append(data[0:data.find("}")+1])
			data = data[data.find("}")+1:]

		datas2 = []
		for data in datas:
			try:
				data = json.loads(data)
				datas2.append(data)
			except:
				print("Got invalid data..", data)
				continue
		return datas2

def packetHandler(gxEdit, sock, playerId, datas):
	for data in datas:
		#########################################
		### --- SERVER RECIEVING PACKETS --- ####
		#########################################

		if data["type"] == PACKET_CONNECT:
			gxEdit.players[playerId]["name"] = ""
			ip = gxEdit.players[playerId]["ip"]

			print(data["name"] + " connected. (" + ip[0] + ":" + str(ip[1]) + ")")

			#TODO: send message to player
			if data["version"] != VERSION_MAGIC:
				print("but their version did not match. ", str(data["version"]))
				return False

			if len(data["name"]) == 0 or len(data["name"]) > 32:
				print("the name was illegal.")
				return False

			for _, player in gxEdit.players.items():
				if player["name"] == data["name"]:
					print("the name already exists.")
					return False
					
			gxEdit.players[playerId]["name"] = data["name"]
			#TODO: broadcast new players to all others

		#########################################
		### --- SERVER RECIEVING PACKETS --- ####
		#########################################

		#TODO: sanitize stage name
		
		elif data["type"] == PACKET_MOUSEPOS:
			gxEdit.players[playerId]["mousepos"] = data["x"], data["y"]
			gxEdit.players[playerId]["curStage"] = data["curStage"]

			if playerId: #i am a server
				for _, player in gxEdit.players.items():
					if player["name"] == gxEdit.players[playerId]["name"]: continue
					serverSendMousePosPacket(gxEdit, data["x"], data["y"], data["curStage"], playerId, gxEdit.players[playerId]["name"])
		elif data["type"] == PACKET_MOUSEPOSFORCLIENT:
			pid = data["playerId"]

			try:
				gxEdit.players[pid]
			except:
				gxEdit.players[pid] = {"name": data["name"]}

			gxEdit.players[pid]["mousepos"] = data["x"], data["y"]
			gxEdit.players[pid]["curStage"] = data["curStage"]


		elif data["type"] == PACKET_TILEEDIT:
			stage = gxEdit.stages[data["stage"]]
			stage.pack.layers[data["layer"]].modify(data["tiles"])
			
			#TODO: UNDO
			gxEdit.tileRenderQueue.append((data["stage"], data["tiles"], data["layer"]))

			if playerId: #i am a server
				for _, player in gxEdit.players.items():
					serverSendPacket(data, player["sock"].request)
		else:
			print("unknown packet")
			print(data)
			return False

	return True
			

class PxEditServerHandler(socketserver.BaseRequestHandler):
	def handle(self):
		gxEdit = self.server.gxEdit
		while True:
			datas = packetAcceptor(gxEdit, self.request)
			if datas == None:
				self.removePlayer()
				return
			if not packetHandler(gxEdit, self.request, self.playerId, datas):
				self.removePlayer()
				return

	def setup(self):
		gxEdit = self.server.gxEdit
		gxEdit.playerId +=1
		self.playerId = gxEdit.playerId
		playerinfo = {}
		playerinfo["ip"] = self.client_address
		playerinfo["sock"] = self
		gxEdit.players[self.playerId] = playerinfo


	def removePlayer(self):
		gxEdit = self.server.gxEdit
		print(gxEdit.players[self.playerId]["name"] + " disconnected.")
		del gxEdit.players[self.playerId]

def clientMethod(gxEdit):
	sock = gxEdit.socket
	while True:
		datas = packetAcceptor(gxEdit, sock)
		if datas == None:
			return
		if not packetHandler(gxEdit, sock, 0, datas):
			return

class PxEditServer(socketserver.ThreadingTCPServer):
	pass

def hostButtonAction(window, elem, gxEdit):
	if gxEdit.socket:
		#TODO: message that you suck
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

	gxEdit.serverPlayerNameTemp = paramName

	print("Now hosting!")
	print("Multiplayer version: " + str(VERSION_MAGIC))

def serverBroadcastAll(gxEdit, packet): #playerid?
	for _, player in gxEdit.players.items():
		serverSendPacket(packet, player["sock"].request)

def serverSendTileEdit(gxEdit, curStage, tiles, layer):
	packet = {"type":PACKET_TILEEDIT, "stage": curStage, "tiles": tiles, "layer": layer}
	serverBroadcastAll(gxEdit, packet)
	
def serverSendMousePosPacket(gxEdit, x, y, curStage, playerId, name):
	packet = {"type":PACKET_MOUSEPOSFORCLIENT, "x": x, "y": y, "curStage": curStage, "playerId": playerId, "name": name}
	serverBroadcastAll(gxEdit, packet)
	

def serverSendPacket(packet, sock):
	#TODO: malformed packet data (extreneous, length?)
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

def sendMousePosPacket(gxEdit, x, y, curStage):
	packet = {"type":PACKET_MOUSEPOS, "x": x, "y": y, "curStage": curStage}
	sendPacket(gxEdit, packet)
	
def sendTileEditPacket(gxEdit, curStage, tiles, layer):
	packet = {"type":PACKET_TILEEDIT, "stage": curStage, "tiles": tiles, "layer": layer}
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
		ip = "127.0.0.1"
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

	