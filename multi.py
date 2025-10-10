import socketserver
import socket
import threading
import const
import sys
import json
import struct

import interface

# In multi.py
import pickle
import zlib
import base64
from editor import gxEdit # Ensure gxEdit is available

import sdl2
import sdl2.ext
from sdl2.sdlttf import *

from sdl2 import sdlimage

import os

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

# New sync packets
PACKET_SYNC_GAME = 12
PACKET_SYNC_STAGETBL = 13
PACKET_SYNC_TILESET_DATA = 14
PACKET_SYNC_OPEN_STAGES = 15
PACKET_SYNC_STAGE_DATA = 16
PACKET_SYNC_COMPLETE = 17

PACKET_OPEN_STAGE = 18
PACKET_CLOSE_STAGE = 19
PACKET_SWITCH_STAGE = 20


PACKET_PLACE_ENTITY = 21
PACKET_MOVE_ENTITY = 22
PACKET_DELETE_ENTITY = 23
PACKET_MODIFY_ENTITY = 24

class PacketError(Exception):
    """Custom exception for errors during packet processing."""
    pass

def broadcast_action(gxEdit, packet):
	"""Sends a packet to the server if a client, or broadcasts to all clients if a host."""
	if gxEdit.multiplayerState == const.MULTIPLAYER_CLIENT:
		sendPacket(gxEdit, packet)
	elif gxEdit.multiplayerState == const.MULTIPLAYER_HOST:
		serverBroadcastAll(gxEdit, packet)

# In multi.py, add a new server broadcast function for opening a stage
def server_broadcast_open_stage(gxEdit, stage_prj, stage_index):
	"""Broadcasts a newly opened stage and its dependencies to all clients."""
	print(f"Broadcasting OPEN_STAGE for '{stage_prj.stageName}' at index {stage_index}")

	# 1. First, ensure any new tilesets are sent.
	new_tilesets = {}
	for i, part in enumerate(stage_prj.parts):
		if part:
			tileset_name = stage_prj.pack.layers[i].partsName
			# A simple way to check if it's new is if clients haven't seen it.
			# A more robust system would track this, but this is a good proxy.
			try:
				with open(part.path, 'rb') as f:
					new_tilesets[tileset_name] = f.read()
			except Exception as e:
				print(f"Could not read new tileset for broadcast: {e}")

	for name, data in new_tilesets.items():
		packet_tileset = {"type": PACKET_SYNC_TILESET_DATA, "name": name, "data": data}
		serverBroadcastAll(gxEdit, packet_tileset)

	# 2. Then, send the stage data itself.
	stage_data_to_send = {
		"stageName": stage_prj.stageName,
		"pack": stage_prj.pack,
		"is_attribute_stage": stage_prj.is_attribute_stage,
		"original_path": stage_prj.original_path,
		"index": stage_index,
	}
	packet_stage = {"type": PACKET_OPEN_STAGE, "data": stage_data_to_send}
	serverBroadcastAll(gxEdit, packet_stage)

REASON_KICKED = "You were kicked from the server"
REASON_OUTDATED = "Your version did not match the server's."
REASON_NAME = "You have an invalid name."
REASON_NAME_EXISTS = "That name is already in use."


VERSION_MAGIC = 14

# Increase buffer size for larger packets
BUFFER_SIZE = 8192

# Helper function for reliable sending

# Helper function for reliable sending

def send_large_packet(sock, data):
    # --- THIS IS THE FIX: Handle disconnections during send ---
    try:
        compressed_data = zlib.compress(pickle.dumps(data))
        size = len(compressed_data)
        sock.sendall(struct.pack('>I', size))
        sock.sendall(compressed_data)
        return True # Indicate success
    except (BrokenPipeError, ConnectionResetError) as e:
        print(f"Send error: Client disconnected. {e}")
        return False # Indicate failure
    # --- END OF FIX ---

# Helper function for reliable receiving

MAX_PACKET_SIZE = 10 * 1024 * 1024 # 10 MB limit, generous but sane
def server_send_disconnect_reason(sock, reason):
    """Sends a disconnect packet to a client and prepares to close the connection."""
    print(f"Sending disconnect reason: {reason}")
    try:
        packet = {"type": PACKET_DISCONNECT_REASON, "reason": reason}
        send_large_packet(sock, packet)
    except (OSError, BrokenPipeError) as e:
        print(f"Could not send disconnect reason, client may have already disconnected: {e}")
def recv_large_packet(sock):
    # 1. Read the 4-byte message length first, handling short reads.
    raw_msglen = b''
    try:
        while len(raw_msglen) < 4:
            chunk = sock.recv(4 - len(raw_msglen))
            if not chunk:
                return None
            raw_msglen += chunk
    except ConnectionResetError:
        return None

    msglen = struct.unpack('>I', raw_msglen)[0]

    # --- THIS IS THE FIX: If size is invalid, DRAIN the bad data from the socket ---
    if msglen > MAX_PACKET_SIZE:
        print(f"Error: Received packet size {msglen} exceeds limit of {MAX_PACKET_SIZE}. Draining and discarding.")
        # We must now read and discard 'msglen' bytes to clear the socket buffer.
        # This prevents the cascade of errors.
        bytes_to_drain = msglen
        while bytes_to_drain > 0:
            chunk_size = min(bytes_to_drain, 8192) # Read in reasonable chunks
            drain_chunk = sock.recv(chunk_size)
            if not drain_chunk:
                # Connection broke while we were draining, that's fine.
                return None
            bytes_to_drain -= len(drain_chunk)
        
        raise PacketError("Packet size exceeds limit.")
    # --- END OF FIX ---
    
    # 2. Read the exact number of bytes for the message data.
    data = b''
    try:
        while len(data) < msglen:
            packet = sock.recv(msglen - len(data))
            if not packet:
                return None
            data += packet
    except ConnectionResetError:
        return None

    # 3. Decompress and deserialize the data.
    try:
        decompressed_data = zlib.decompress(data)
        return pickle.loads(decompressed_data)
    except (zlib.error, pickle.UnpicklingError) as e:
        # Here, the data has already been read from the socket, so just raising is correct.
        raise PacketError(f"Decompression/unpickling failed: {e}")

def server_send_full_sync(gxEdit, client_sock):
	"""The host's function to send all necessary data to a new client."""
	print(f"--- Starting full sync for new client ---")

	# 1. Sync current game
	current_game_name = gxEdit.game_manager.get_current_game().name
	print(f"  -> Syncing game: {current_game_name}")
	packet_game = {"type": PACKET_SYNC_GAME, "game_name": current_game_name}
	send_large_packet(client_sock, packet_game)

	# 2. Sync stage.tbl if it exists
	if gxEdit.stage_table:
		print("  -> Syncing stage.tbl...")
		packet_tbl = {"type": PACKET_SYNC_STAGETBL, "table_data": gxEdit.stage_table}
		send_large_packet(client_sock, packet_tbl)

	# 3. Sync all unique, required tilesets
	unique_tilesets = {}
	for stage_prj in gxEdit.stages:
		for i, part in enumerate(stage_prj.parts):
			if part:
				tileset_name = stage_prj.pack.layers[i].partsName
				if tileset_name and tileset_name not in unique_tilesets:
					# To send an SDL surface, we must save it to a buffer
					# For simplicity, we'll re-read the original file path. A more robust
					# solution might involve saving the surface to an in-memory PNG.
					# This implementation re-reads the file, which is simpler.
					# NOTE: This assumes the host has the original files.
					try:
						with open(part.path, 'rb') as f:
							image_data = f.read()
							unique_tilesets[tileset_name] = image_data
							print(f"  -> Preparing tileset '{tileset_name}' for sync...")
					except Exception as e:
						print(f"Warning: Could not read tileset file for sync: {e}")
	
	for name, data in unique_tilesets.items():
		packet_tileset = {"type": PACKET_SYNC_TILESET_DATA, "name": name, "data": data}
		send_large_packet(client_sock, packet_tileset)

	# 4. Sync list of open stages
	open_stages_info = {
		"names": [s.stageName for s in gxEdit.stages],
		"active_index": gxEdit.curStage
	}
	print(f"  -> Syncing open stages: {open_stages_info['names']}")
	packet_open_stages = {"type": PACKET_SYNC_OPEN_STAGES, "info": open_stages_info}
	send_large_packet(client_sock, packet_open_stages)

	# 5. Sync each stage's full data
	for stage_prj in gxEdit.stages:
		print(f"  -> Syncing data for stage '{stage_prj.stageName}'...")
		# We can't pickle SDL textures, so we send the core data
		stage_data_to_send = {
			"stageName": stage_prj.stageName,
			"pack": stage_prj.pack,
			"is_attribute_stage": stage_prj.is_attribute_stage,
			"original_path": stage_prj.original_path,
			# We can't send undo stack easily, client starts fresh
		}
		packet_stage = {"type": PACKET_SYNC_STAGE_DATA, "data": stage_data_to_send}
		send_large_packet(client_sock, packet_stage)

	# 6. Signal completion
	print("--- Full sync complete ---")
	packet_complete = {"type": PACKET_SYNC_COMPLETE}
	send_large_packet(client_sock, packet_complete)

def packetAcceptor(gxEdit, sock):
    # --- THIS IS THE FIX: Loop and handle exceptions gracefully ---
    while True:
        try:
            # Try to receive a single valid packet
            data = recv_large_packet(sock)
            if data is None:
                # A 'None' return still means a clean disconnect.
                return None
            # If successful, return it as a list for the handler
            return [data]
        except PacketError as e:
            # An invalid packet was received. Log it and continue listening.
            print(f"Warning: Discarding invalid packet. {e}")
            continue # Loop again to wait for the next packet.
        except (OSError, EOFError) as e:
            # A more serious socket-level error occurred.
            print(f"Socket error in packetAcceptor: {e}")
            return None
    # --- END OF FIX ---


def packetHandler(gxEdit, sock, playerId, datas):
	for data in datas:
		# --- THIS IS THE FIX ---
		# The server-side guard should only run on the server (when playerId is not 0).
		if playerId != 0:
			if data["type"] != PACKET_CONNECT and "name" not in gxEdit.players[playerId]:
				print(f"Ignoring packet (type {data['type']}) from un-named player {playerId}. Waiting for CONNECT.")
				continue
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
				server_send_disconnect_reason(sock, REASON_OUTDATED)
				return False # This correctly stops execution for this client

			if len(data["name"]) == 0 or len(data["name"]) > 32:
				print("the name was illegal.")
				server_send_disconnect_reason(sock, REASON_NAME)
				return False # This correctly stops execution for this client

			for p_id, player in gxEdit.players.items():
				if p_id == playerId:
					continue
				
				if player.get("name") == data["name"]:
					print("the name already exists.")
					server_send_disconnect_reason(sock, REASON_NAME_EXISTS)
					return False # This correctly stops execution for this client
					
			gxEdit.players[playerId]["name"] = data["name"]
			
			# !!! INITIATE SYNC !!!
			# This is now only reached if all validation passes.
			server_send_full_sync(gxEdit, sock)
		#########################################
		### --- SERVER RECIEVING PACKETS --- ####
		#########################################

		#TODO: sanitize stage name
		
		elif data["type"] == PACKET_MOUSEPOS:
			gxEdit.players[playerId]["mousepos"] = data["x"], data["y"]
			gxEdit.players[playerId]["curStage"] = data["curStage"]

			if playerId: # i am a server
				# --- THIS IS THE FIX (Cleaner Version) ---
				# Get the sender's name safely. If it doesn't exist, we can't broadcast.
				sender_name = gxEdit.players[playerId].get("name")
				if not sender_name:
					print(f"Ignoring MOUSEPOS from player {playerId} who has no name yet.")
					return True # Not a critical error, just too early to process

				# Prepare one packet and broadcast it to everyone *except* the sender.
				packet_to_broadcast = {
					"type": PACKET_MOUSEPOSFORCLIENT, 
					"x": data["x"], 
					"y": data["y"], 
					"curStage": data["curStage"], 
					"playerId": playerId, 
					"name": sender_name
				}
				serverBroadcastAll(gxEdit, packet_to_broadcast, exclude_id=playerId)
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

		
		elif data["type"] == PACKET_PLACE_ENTITY:
			stage_index = data["stage_index"]
			entity = data["entity"]
			print(f"<- Received PLACE_ENTITY for stage {stage_index}")

			# Host must re-broadcast to other clients
			if playerId != 0: # playerId 0 is the client's self-view, non-zero is a client on the host
				serverBroadcastAll(gxEdit, data, exclude_id=playerId)

			# Apply the change locally
			if 0 <= stage_index < len(gxEdit.stages):
				stage = gxEdit.stages[stage_index]
				# Ensure no ID collision
				if any(e.id == entity.id for e in stage.pack.eve.units):
					print(f"  -> Entity ID {entity.id} collision, re-assigning.")
					entity.id = stage.pack.eve._count
				stage.pack.eve.units.append(entity)
				stage.pack.eve._count = max(stage.pack.eve._count, entity.id) + 1

		elif data["type"] == PACKET_MOVE_ENTITY:
			stage_index = data["stage_index"]
			moved_entities = data["entities"]
			print(f"<- Received MOVE_ENTITY for stage {stage_index}")

			if playerId != 0:
				serverBroadcastAll(gxEdit, data, exclude_id=playerId)

			if 0 <= stage_index < len(gxEdit.stages):
				stage = gxEdit.stages[stage_index]
				stage.pack.eve.replace(moved_entities) # replace is efficient for this

		elif data["type"] == PACKET_DELETE_ENTITY:
			stage_index = data["stage_index"]
			entity_ids = data["ids"]
			print(f"<- Received DELETE_ENTITY for stage {stage_index}")

			if playerId != 0:
				serverBroadcastAll(gxEdit, data, exclude_id=playerId)

			if 0 <= stage_index < len(gxEdit.stages):
				stage = gxEdit.stages[stage_index]
				stage.pack.eve.remove(entity_ids)
				
		elif data["type"] == PACKET_MODIFY_ENTITY:
			stage_index = data["stage_index"]
			modified_entities = data["entities"]
			print(f"<- Received MODIFY_ENTITY for stage {stage_index}")

			if playerId != 0:
				serverBroadcastAll(gxEdit, data, exclude_id=playerId)
			
			if 0 <= stage_index < len(gxEdit.stages):
				stage = gxEdit.stages[stage_index]
				stage.pack.eve.replace(modified_entities)
		elif data["type"] == PACKET_DISCONNECT_REASON:
			reason = data.get("reason", "No reason given.")
			print(f"Disconnected from server: {reason}")
			gxEdit.add_popup(f"Disconnected: {reason}")
			# The client thread will naturally exit after this as the server closes the socket.
			# We can also signal the main thread to clean up.
			gxEdit.multiplayerState = const.MULTIPLAYER_NONE
			# Returning False will cause the client loop to terminate.
			return False

		elif data["type"] == PACKET_SYNC_GAME:
			print(f"<- Received sync game: {data['game_name']}")
			gxEdit.is_syncing = True # SET FLAG
			
			# --- THIS IS THE FIX: Post a task to the main thread instead of doing the work here ---
			gxEdit.main_thread_queue.append(('SWITCH_GAME_FOR_SYNC', data['game_name']))
			# --- END OF FIX ---

		elif data["type"] == PACKET_SYNC_STAGETBL:
			print("<- Received stage.tbl sync.")
			gxEdit.stage_table = data["table_data"]
		elif data["type"] == PACKET_OPEN_STAGE:
			s_data = data['data']
			print(f"<- Received OPEN_STAGE for '{s_data['stageName']}'")
			# Post this complex task to the main thread to avoid race conditions and thread-safety issues.
			gxEdit.main_thread_queue.append(('LOAD_SYNCED_STAGE', s_data))
		
		elif data["type"] == PACKET_CLOSE_STAGE:
			stage_index = data["index"]
			print(f"<- Received CLOSE_STAGE for index {stage_index}")
			if 0 <= stage_index < len(gxEdit.stages):
				gxEdit.stages.pop(stage_index)
				# Adjust current stage index if necessary
				if gxEdit.curStage >= stage_index:
					gxEdit.curStage = max(0, gxEdit.curStage - 1)

		elif data["type"] == PACKET_SWITCH_STAGE:
			stage_index = data["index"]
			print(f"<- Received SWITCH_STAGE to index {stage_index}")
			gxEdit.curStage = stage_index

# In multi.py, inside packetHandler

		
		elif data["type"] == PACKET_SYNC_TILESET_DATA:
			# --- THIS IS THE FIX: Just cache the raw bytes, do not create a sprite ---
			print(f"<- Caching RAW tileset data for '{data['name']}'")
			gxEdit.synced_tileset_data_raw[data['name']] = data['data']

		elif data["type"] == PACKET_SYNC_OPEN_STAGES:
			print(f"<- Caching open stages list: {data['info']['names']}")
			gxEdit.open_stages_info_from_sync = data['info']
			gxEdit.stages.clear()
			gxEdit.synced_stage_data.clear()

		elif data["type"] == PACKET_SYNC_STAGE_DATA:
			s_data = data['data']
			print(f"<- Caching stage data for '{s_data['stageName']}'")
			# Store the raw data, don't process it yet
			gxEdit.synced_stage_data[s_data['stageName']] = s_data


		
		elif data["type"] == PACKET_SYNC_COMPLETE:
			# --- THIS IS THE FIX: Post a task to the main thread instead of doing the work here ---
			print("<- Sync data received. Posting assembly task to main thread.")
			gxEdit.main_thread_queue.append(('FINISH_SYNC', None))
			# Note: We do NOT set is_syncing to False here. The main thread will do that.

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
			if datas is None:
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
		# --- THIS IS THE FIX ---
		# Safely get the player's name for the disconnect message.
		# Fallback to the player ID if the name was never assigned.
		player_name = gxEdit.players[self.playerId].get("name", f"Player {self.playerId}")
		print(f"{player_name} disconnected.")
		
		# Now it's safe to delete the player entry.
		del gxEdit.players[self.playerId]
		# --- END OF FIX ---
def clientMethod(gxEdit):
	sock = gxEdit.socket
	try:
		while gxEdit.multiplayerState == const.MULTIPLAYER_CLIENT: # Loop only while connected
			datas = packetAcceptor(gxEdit, sock)
			if datas is None:
				# Handle abrupt disconnection from server
				print("Disconnected from server.")
				if gxEdit.multiplayerState == const.MULTIPLAYER_CLIENT:
					gxEdit.add_popup("Connection to server lost.")
				break # Exit the loop

			if packetHandler(gxEdit, sock, 0, datas) is False:
				# packetHandler returned False, signaling a clean disconnect
				break # Exit the loop
	finally:
		# --- THIS IS THE FIX: Ensure cleanup happens no matter how the loop exits ---
		print("Multiplayer client thread terminating and cleaning up.")
		gxEdit.multiplayerState = const.MULTIPLAYER_NONE
		gxEdit.synced_tilesets.clear()
		gxEdit.synced_stage_data.clear()
		gxEdit.open_stages_info_from_sync = None
		gxEdit.is_syncing = False # <-- UNSET FLAG
		if gxEdit.socket:
			try:
				gxEdit.socket.shutdown(socket.SHUT_RDWR)
				gxEdit.socket.close()
			except OSError:
				pass # Socket may already be closed
			gxEdit.socket = None
		gxEdit.socket_thread = None # Clear the reference to this thread
		gxEdit.players = {} # Clear the list of other players

class PxEditServer(socketserver.ThreadingTCPServer):
	pass

def hostButtonAction(window, elem, gxEdit):
	if gxEdit.socket:
		#TODO: message that you suck
		return
	paramName = window.elements["paramName"].text
	#TODO:
	if paramName == "":
		paramName = "I forgot my name and i suck"

	paramIP = window.elements["paramIP"].text
	paramPort = window.elements["paramPort"].text
	try:
		port = int(paramPort)
	except:
		port = DEFAULT_PORT

	try:

		socketserver.TCPServer.allow_reuse_address = True
		# --- END OF FIX ---
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


def serverBroadcastAll(gxEdit, packet, exclude_id=None):
    # --- THIS IS THE FIX: Handle failed sends during broadcast ---
    disconnected_players = []
    for pid, player in gxEdit.players.items():
        if pid == exclude_id:
            continue
        
        # serverSendPacket now returns False if the pipe is broken
        if not serverSendPacket(packet, player["sock"].request):
            # Don't modify the dictionary while iterating over it.
            # Just collect the IDs of disconnected players.
            disconnected_players.append(pid)
    
    # Now, safely remove all players that were found to be disconnected.
    for pid in disconnected_players:
        # PxEditServerHandler doesn't have a direct 'removePlayer' we can call,
        # so we'll replicate the logic here.
        player_name = gxEdit.players[pid].get("name", f"Player {pid}")
        print(f"{player_name} disconnected (detected during broadcast).")
        if pid in gxEdit.players:
            del gxEdit.players[pid]

def serverSendTileEdit(gxEdit, curStage, tiles, layer):
	packet = {"type":PACKET_TILEEDIT, "stage": curStage, "tiles": tiles, "layer": layer}
	serverBroadcastAll(gxEdit, packet)
	
def serverSendMousePosPacket(gxEdit, x, y, curStage, playerId, name):
	packet = {"type":PACKET_MOUSEPOSFORCLIENT, "x": x, "y": y, "curStage": curStage, "playerId": playerId, "name": name}
	serverBroadcastAll(gxEdit, packet)
	

def serverSendPacket(packet, sock):
	try:
		return send_large_packet(sock, packet)
	except OSError as e:
		print(e)
		return False

def sendPacket(gxEdit, packet):
	try:
		send_large_packet(gxEdit.socket, packet)
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

	