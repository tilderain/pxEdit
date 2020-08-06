import socketserver
import socket
import threading
import const
import sys
import json

DEFAULT_PORT = 7777

PACKET_CONNECT = 1
PACKET_MOUSEPOS = 2

class PxEditServerHandler(socketserver.BaseRequestHandler):
	def handle(self):
		while True:
			data = self.request.recv(32768)
			data = data.decode("utf-8")
			datas = []

			while data.find("}") != -1:
				datas.append(data[0:data.find("}")+1])
				data = data[data.find("}")+1:]

			gxEdit = self.server.gxEdit

			for data in datas:
				try:
					data = json.loads(data)
				except:
					print("Got invalid data..", data)
					continue
				
				if data["type"] == PACKET_CONNECT:
					gxEdit.players[self.playerId]["name"] = data["name"]
				elif data["type"] == PACKET_MOUSEPOS:
					gxEdit.players[self.playerId]["mousepos"] = data["x"], data["y"]

	def setup(self):
		gxEdit = self.server.gxEdit
		self.playerId = gxEdit.playerId
		playerinfo = {}
		playerinfo["ip"] = self.client_address
		playerinfo["sock"] = self
		gxEdit.players[self.playerId] = playerinfo
		gxEdit.playerId +=1

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

def clientMethod(gxEdit):
	pass

def sendMousePosPacket(gxEdit, x, y):
	mousePosPacket = {"type":PACKET_MOUSEPOS, "x": x, "y": y}
	data = json.dumps(mousePosPacket)
	gxEdit.socket.sendall(bytes(data,encoding="utf-8"))
	

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

	connectPacket = {"type":PACKET_CONNECT, "name": paramName}
	data = json.dumps(connectPacket)
	gxEdit.socket.sendall(bytes(data,encoding="utf-8"))

	gxEdit.socket_thread = threading.Thread(target=clientMethod, args=([gxEdit]))
	gxEdit.socket_thread.daemon = True
	gxEdit.socket_thread.start()

	window.visible = False

	