import socketserver
import socket
import threading
import const
import sys

DEFAULT_PORT = 7777

class PxEditServerHandler(socketserver.BaseRequestHandler):
	def handle(self):

		pass

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
		del sock
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

def connectButtonAction(window, elem, gxEdit):
	if gxEdit.socket:
		return

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
		del sock
		return
	gxEdit.socket = sock
	gxEdit.multiplayerState = const.MULTIPLAYER_CLIENT

	gxEdit.socket_thread = threading.Thread(target=clientMethod, args=([gxEdit]))
	gxEdit.socket_thread.daemon = True
	gxEdit.socket_thread.start()

	window.visible = False

	