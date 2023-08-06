#!/usr/bin/env python3

# python library Stealink network

import struct
from asyncio import Queue
from queue import Empty, Full
import socket
import json
import time
import asyncio
import re
import os

import logging
logger = logging.getLogger(__name__)

from .util import phex

from .const import (
    PROJECT_PACKAGE_NAME,
    __version__
)

from .linkage import (
	Item,
	Table,
	DictTable,
	DbTable,
	CSearchKey,
)


MAX_RESEND_COUNT = 25
SL_MAX_MESSAGE_LEN = 255
SL_ACK_WAIT = 3


_MQTT = None
_DB = None
steam_root = None

def Attach(mqtt, db):
	global _MQTT, _DB
	_MQTT = mqtt
	_DB = db
	logger.debug("steamlink: Attached apps '%s, %s'", _MQTT.name, _DB.name)


def set_steam_root(root):
	global steam_root
	steam_root = root

TODO = """
- track routing table from received packets

"""



#
# Exception 
#
class SteamLinkError(Exception):
	def __init__(self, message):

		# Call the base class constructor with the parameters it needs
		super().__init__(message)



SL_RESPONSE_WAIT_SEC = 10
MAX_NODE_LOG_LEN = 1000		# maximum packets stored in per node log



NODEVER = 1
MAXSILENCE = 45

#
# SL_CodeCfgStruct
#
class SL_NodeCfgStruct:
	"""
	Node configuration data, as stored in flash
	defined in SteamLink.h in the steamlink-arduino repo

	struct SL_NodeCfgStruct {
		uint8_t  version;
		uint32_t slid;
		char name[10];
		char description[32];
		float gps_lat;
		float gps_lon;
		short altitude;		// in meters
		uint8_t max_silence; // in seconds
		bool battery_powered;
		uint8_t radio_params; // radio params need to be interpreted by drivers

	"""
	sfmt = '<BL10s32sffhBBB'

	def __init__(self, version = NODEVER, slid = None, name = "*UNK*", description = "*UNK*", gps_lat = 0.0, gps_lon = 0.0, altitude = 0, max_silence = MAXSILENCE, battery_powered = False, radio_params = 0, pkt = None):
		if pkt is None:	 # construct
			self.version = version
			self.slid = slid						# L
			self.name = name						# 10s
			self.description = description			# 32s
			self.gps_lat = gps_lat					# f
			self.gps_lon = gps_lon					# f
			self.altitude = altitude				# h
			self.max_silence = max_silence			# B
			self.battery_powered = battery_powered	# B
			self.radio_params = radio_params		# B

		else:			# deconstruct
			if struct.calcsize(SL_NodeCfgStruct.sfmt) != len(pkt):
				logger.error("NodeCfgStruct: packed messages length incorrect, wanted %s, got %s", struct.calcsize(SL_NodeCfgStruct.sfmt), len(pkt))
				raise SteamLinkError("packed messages length incorrect")
			self.version, self.slid, name, description, self.gps_lat, self.gps_lon, self.altitude, self.max_silence, battery_powered, self.radio_params = struct.unpack(SL_NodeCfgStruct.sfmt, pkt)
			self.name = name.decode().strip('\0')
			self.description = description.decode().strip('\0')
			self.battery_powered = battery_powered == 1

	def pack(self):
		self.pkt = struct.pack(SL_NodeCfgStruct.sfmt, self.version, self.slid, self.name.encode(), self.description.encode(), self.gps_lat, self.gps_lon, self.altitude, self.max_silence, self.battery_powered, self.radio_params)
		return self.pkt


	def __str__(self):
		try:
			return "NodeCFG: %s %s %s" % (self.slid, self.name, self.description)
		except Exception as e:
			return "NodeCFG: undefined: %s" % e

	def save(self):
		d = {
			'slid': self.slid,
			'name': self.name,
			'description': self.description,
			'gps_lat': self.gps_lat,
			'gps_lon': self.gps_lon,
			'altitude': self.altitude,
			'max_silence': self.max_silence,
			'battery_powered': self.battery_powered,
			'radio_params': self.radio_params
		}
		return d

	def update(self, other):
		if self.slid != other.slid:
			logger.info("Node %s changed slid from %s to %s", self.name, self.slid, other.slid)
			self.slid = other.slid
		if self.name != other.name:
			logger.info("Node %s changed name from %s to %s", self.name, self.name, other.name)
			self.name = other.name
		if self.description != other.description:
			logger.info("Node %s changed description from %s to %s", self.name, self.description, other.description)
			self.description = other.description
		if self.max_silence != other.max_silence:
			logger.info("Node %s changed max_silence from %s to %s", self.name, self.gps_lon, other.gps_lon)
			self.max_silence = other.max_silence
		if self.gps_lat != other.gps_lat:
			logger.info("Node %s changed gps_lat from %s to %s", self.name, self.gps_lat, other.gps_lat)
			self.gps_lat = other.gps_lat
		if self.gps_lon != other.gps_lon:
			logger.info("Node %s changed gps_lon from %s to %s", self.name, self.gps_lon, other.gps_lon)
			self.gps_lon = other.gps_lon
		# incomplete

#
# SL_OP op codes
#
class SL_OP:
	'''
	control message types: EVEN, 0 bottom bit
	data message types: ODD, 1 bottom bit
	'''

	DN = 0x30		# data to node, ACK 
	BN = 0x32		# slid precedes payload, bridge forward to node
	GS = 0x34		# get status, reply with SS message
	TD = 0x36		# transmit a test message via radio
	SC = 0x38		# set radio paramter to x, acknowlegde with AK
	BC = 0x3A		# restart node, no reply
	BR = 0x3C		# reset the radio, TBD
	AN = 0x3E		# Ack from store -> node

	DS = 0x31		# data to store
	BS = 0x33		# bridge to store
	ON = 0x35		# go online
	AS = 0x37		# acknowlegde the last control message
	OF = 0x39		# go offline
	TR = 0x3B		# Received Test Data
	SS = 0x3D		# status info and counters
	NC = 0x3F		# No Connection or timeout

	def code(code):
		try:
			return list(SL_OP.__dict__.keys())[list(SL_OP.__dict__.values()).index(code)]
		except:
			pass
		return '??'

	def val(val):
		try:
			return SL_OP.__dict__[val]
		except:
			pass
		return 0x99	

SL_AS_CODE = {0: 'Success', 1: 'Supressed duplicate pkt', 2: 'Unexpected pkt, dropping'}

class WaitForAck:

	def __init__(self, waittime):
		self.waittime = waittime
		self.clear_wait()


	def __str__(self):
		if self.waituntil == 0:
			return "NoWait"
		return "Wait %s %s" % (int(self.waituntil), self.pkt)


	def clear_wait(self):
		self.waituntil = 0
		self.pkt = None
		self.count = 0
		self.do_insert = False


	def stop_wait(self):
		""" N.B. returns original pkt if do_insert was set, for db insert """
		pkt = None
		if self.pkt is None:
			if 'waitack' in logging.DBGK: logger.info("wait: redundant Ack")
		else:
			if 'waitack' in logging.DBGK: logger.debug("wait on %s got Ack", self)
			if self.do_insert:
				pkt = self.pkt
		self.clear_wait()
		return pkt


	def restart_wait(self):
		self.waituntil = time.time() + self.waittime
		return self.pkt		# for resend


	def wait_remaining(self):
		if self.waituntil == 0:
			return 0
		return self.waituntil - time.time()


	def set_wait(self, pkt, do_insert=False):
		self.waituntil = time.time() + self.waittime
		self.pkt = pkt
		self.count = 0
		self.do_insert = do_insert
		if 'waitack' in logging.DBGK: logger.debug("wait on %s for %s sec", self.pkt, self.waittime)


	def inc_resend_count(self):
		self.count += 1
		return self.count


	def is_waiting(self):
		return self.waituntil


#
# Steam
#
class Steam(Item):
	def __init__(self, conf = None):
		self.steam_id = 0
		self.autocreate = False
		if conf:
			self.desc = conf['description']
			self.autocreate = conf['autocreate']
			self.name = conf['name']
			self.steam_id = int(conf['id'])
		super().__init__(self.steam_id)
		self.cpubusy = 0
		self.my_ip_address = socket.gethostbyname(socket.gethostname())
		self.identity = "%s %s (%s)" % (PROJECT_PACKAGE_NAME, __version__, self.my_ip_address)
		self._public_topic_control_re = None

		_MQTT.set_msg_callback(self.on_data_msg)

		self._public_topic_control = _MQTT.get_public_control_topic()
		if self._public_topic_control is not None:
			_MQTT.set_public_control_callback(self.on_public_control_msg)
			self._public_topic_control_re = self._public_topic_control % "(.*)"

		self._mqtt_test_succeeded  = False

		mq_cmd_msg = { "cmd": "selfcheck", "identity": self.identity }
		_MQTT.publish("store", json.dumps(mq_cmd_msg), sub="data")


	def set_loglevel(self, loglevel):
		from .linkage import logger as linkage_logger 
		from .mqtt import logger as mqtt_logger 
		from .db import logger as db_logger 
		from .testdata import logger as testdata_logger 
		from .web import logger as web_logger

		logger.setLevel(loglevel)
		linkage_logger.setLevel(loglevel)
		mqtt_logger.setLevel(loglevel)
		db_logger.setLevel(loglevel)
		testdata_logger.setLevel(loglevel)
		web_logger.setLevel(loglevel)


	def handle_web_command(self, sid, message):
		# dict with: cmd, slid, data
		# cmds are: DN SC
		if message['cmd'] in ["DN", "SC"]:
			node = Node._table.find_one(message["slid"])
			if node is None:
				return {"Success": False, "Error": "Unknown node" }
			to_send = message['data']
			if message['cmd'] == "DN":
				ret = node.send_data_to_node(to_send+'\0') 	

			elif message['cmd'] == "SC":
				try:
					nodecfg = json.loads(to_send)
				except Exception as e:
					return {"Success": False, "Error": "nodecfg problem:  %s" % e }
				node.nodecfg = SL_NodeCfgStruct(node.slid, **nodecfg)
				ret = node.send_set_config() 

		if ret is not "OK":
			return {"Success": False,
					"Error": "packet %s was not send to %s: %s" % (to_send, node.name, ret) }
		return {"Success": True }


	def handle_store_command(self, cmd):
		if type(cmd) != type({}):
			logger.warning("unreadable cmd %s", cmd)
			return
		if cmd['cmd'] == 'selfcheck':
			id = cmd.get('identity')
			if id != self.identity:
				logger.warning("there is another system: %s", id)
			else:
				logger.debug("mqtt test successfull")
				self._mqtt_test_succeeded = True
		elif cmd['cmd'] == 'gelog':
			count = cmd.get('count', 1)
			for i in range(count):
				logger.info("useless log entry, just to take up space, num %s", i)
		elif cmd['cmd'] == 'ping':
			response = "pong '%s'" % self.identity
			_MQTT.publish("store", response, sub="control")
		elif cmd['cmd'] == 'debug':
			dbglvl = cmd.get('dbglvl', None)
			slvl = cmd.get('level', None)
			if slvl is not None:
				loglevel = getattr(logging, slvl.upper())
				self.set_loglevel(loglevel)
				logger.warning("setting loglevel to %s", loglevel)
			if dbglvl is not None:
				logging.DBG = int(dbglvl)
		elif cmd['cmd'] == 'shutdown':
			from .main import GracefulExit, GracefulRestart
			if cmd.get('restart',False):
				raise GracefulRestart
			else:
				raise GracefulExit
		else:
			logger.warning("unknown store command %s", cmd)
				

	def on_public_control_msg(self, client, userdata, msg):
		if self._public_topic_control is None:
			return

		if logging.DBG > 2: logger.debug("on_public_control_msg %s %s", msg.topic, msg.payload)
		match = re.match(self._public_topic_control_re, msg.topic) 
		if match is None:
			logger.warning("topic did not match public control topic: %s %s", topic, self._public_topic_control)
			return
		nodename = match.group(1)
		node = Node._table.find_one(nodename, keyfield = "name")
		if node is None:
			logger.warning("public control: no such node %s: %s", nodename, msg.payload)
			return
		try:
			jmsg = json.loads(msg.payload.decode('utf-8'))
			to_send = jmsg['payload'].encode()
		except Exception as e:
			to_send = str(msg.payload.decode('utf-8'))
#			raise
		ret = node.send_data_to_node(to_send+'\0') 	# XXX should not need the b'\0' but nodes crash w/o
		if ret is not "OK":
			logger.warning("packet %s was not send to %s: %s", to_send, node.name, ret)


	def on_data_msg(self, client, userdata, msg):
		# msg has  topic, payload, retain

		topic_parts = msg.topic.split('/', 2)
		if topic_parts[1] == "store":
			try:
				cmd = json.loads(msg.payload.decode('utf-8'))
			except:
				cmd = msg.payload
			logger.debug("store command %s", cmd)
			self.handle_store_command(cmd)
			return

		if logging.DBG > 2: logger.debug("on_data_msg  %s %s", msg.topic, msg.payload)
		try:
			sl_pkt = Packet(pkt=msg.payload)
		except SteamLinkError as e:
			logger.warning("mqtt: pkt dropped: '%s', steamlink error %s", msg.payload, e)
			return
		except ValueError as e:
			logger.warning("mqtt: pkt dropped: '%s', value error %s", msg.payload, e)
			return
		if sl_pkt.slid is None:
			logger.warning("mqtt: pkt dropped: '%s', no slid %s", msg.payload, sl_pkt)
			return

		node = Node._table.find_one(sl_pkt.slid)
		if node is None:		# Auto-create node
			if self.autocreate and sl_pkt.sl_op == SL_OP.ON:
				node = Node(sl_pkt.slid, sl_pkt.nodecfg)
			else:
				logger.warning("on_data_msg: no node for pkt %s", sl_pkt)
				return
		sl_pkt.set_node(node)
		node.post_data(sl_pkt)


	async def start(self):
		process_time = time.process_time()
		now = time.time()
		delta = 0
		wait = 1
		logger.info("%s starting heartbeat", self.name)
		FLUSHWAIT = 10
		flushwait = FLUSHWAIT
		while True:
			await asyncio.sleep(wait)
			self.heartbeat()
			flushwait -= 1
			if flushwait == 0:
				_DB.flush()		# N.B. expensive
				flushwait = FLUSHWAIT

			n_process_time = time.process_time()
			n_now = time.time()

			delta = n_now - now
			wait = 1 - (n_now % 1)
			self.cpubusy = ((n_process_time - process_time) / delta ) * 100.0
			now = n_now
			process_time = n_process_time
#			if logging.DBG == 0:	# N.B. reduce noise when debuging, i.e. no heartbeat
			self.update(True)


	def heartbeat(self):
		for node in Node._table.find(1, 'mesh_id'):
			node.periodic_check()


	def save(self, withvirtual=False):
		r = {}
		r['steam_id'] = self.steam_id
		r['name'] = self.name
		r['desc'] = self.desc
		if withvirtual:
			r['Name'] = self.name
			r['Description'] = self.desc
			r['Meshes'] = len(Mesh._table)
			r['Time'] = time.asctime()
			r['Load'] = "%3.1f%%" % self.cpubusy
			r['Mesh records'] = len(Mesh._table)
			r['Node records'] = len(Node._table)
			r['Packet records'] = len(Packet._table)
		return r

#
# Mesh
#
class Mesh(Item):
	keyfield = 'mesh_id'

	def __init__(self, mesh_id=None):
		self.mesh_id = mesh_id
		if mesh_id is None:
			self.name = "Mesh??" 
		else:
			self.name = "Mesh%s" % self.mesh_id
		self.desc = "Description for %s" % self.name
		self.steam_id = 0	# XXX
		self.packets_sent = 0
		self.packets_received = 0
		super().__init__(self.mesh_id)
		if self.mesh_id is not None:
			logger.info("Mesh created: %s", self)


	def save(self, withvirtual=False):
		r = {}
		r['mesh_id'] = self.mesh_id
		r['steam_id'] = self.steam_id
		r['name'] = self.name
		r['desc'] = self.desc
		if withvirtual:
			r['Name'] = self.name
			r['Description'] = self.desc
			r["Total Nodes"] = len(Node._table)
			r["Active Nodes"] = len(Node._table)
			r["Packets sent"] = self.packets_sent
			r["Packets received"] = self.packets_received
		return r

#
# Node
#
class Node(Item):
	keyfield = 'slid'
	UPSTATES = ["ONLINE", "OK", "UP", "TRANSMITTING"]
	OPS_need_ack = [SL_OP.DS, SL_OP.ON]

	""" a node in a mesh set """
	def __init__(self, slid=None, nodecfg = None):
		if slid is not None:
			slid = int(slid)
			logger.debug("Node creating : %s" % slid)
			if nodecfg is None:
				self.nodecfg = SL_NodeCfgStruct(slid, "Node%08x" % slid)
				logger.debug("Node config is %s", self.nodecfg)
			elif type(nodecfg) == type({}):
				self.nodecfg = SL_NodeCfgStruct(slid, **nodecfg)
				logger.debug("Node config is %s", self.nodecfg)
			else:
				self.nodecfg = nodecfg
			self.name = nodecfg.name
			self.slid = slid
			self.mesh_id = (slid >> 8)
			self.set_mesh()
		else:
			self.name = ""
			self.slid = None
			self.mesh_id = None
		self._response_q = Queue(maxsize=1)

		self.packets_sent = 0
		self.packets_received = 0
		self.packets_resent = 0
		self.packets_dropped = 0
		self.packets_missed = 0
		self.packets_duplicate = 0
		self.pkt_numbers = {True: 0, False:  0}	# next pkt num for data, control pkts
		self.state = "INITIAL"
		self.last_node_restart_ts = 0
		self.last_packet_rx_ts = 0
		self.last_packet_tx_ts = 0
		self.last_packet_num = 0
		self.last_control_pkt = None
		self.last_data_pkt = None
		self.via = []		# not initiatized
		self.tr = {}		# dict of sending nodes, each holds a list of (pktno, rssi)
		self.wait_for_AS = WaitForAck(SL_ACK_WAIT)
#		self.packet_log = TimeLog(MAX_NODE_LOG_LEN)

		super().__init__(slid)
		if slid is not None:
			logger.info("Node created: %s" % self)


	def set_mesh(self):
		self.mesh = Mesh._table.find_one(self.mesh_id)
		if self.mesh is None:		# Auto-create Mesh
			logger.debug("Node %s: mesh %s autocreated", self.slid, self.mesh_id)
			self.mesh = Mesh(self.mesh_id)


	def set_pkt_number(self, pkt):
		dc =  pkt.is_data()
		self.pkt_numbers[dc] += 1
		if self.pkt_numbers[dc] == 0:
			self.pkt_numbers[dc] += 1	# skip 0
		return self.pkt_numbers[dc]


	def load(self, data):	#N.B.
		if 'nodecfg' in data:
			data['nodecfg'] = SL_NodeCfgStruct(**data['nodecfg'])
		super().load(data)
		self.set_mesh()


	def save(self, withvirtual=False):
		r = {}
		r['name'] = self.name
		r[Node.keyfield] = self.slid
		r[Mesh.keyfield] = self.mesh_id
		r['via'] = self.via
		r['nodecfg'] = self.nodecfg.save()
		if withvirtual:
			r['State'] = self.state
			r['Name'] = self.nodecfg.name
			r['Description'] = self.nodecfg.description
			r['Last Pkt received'] = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(int(self.last_packet_rx_ts)))
			r['Last Pkt sent'] = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(int(self.last_packet_tx_ts)))
			r['Last Node restart'] = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(int(self.last_node_restart_ts)))
			r['Packets sent'] = self.packets_sent
			r['Packets received'] = self.packets_received
			r['Packets resent'] = self.packets_resent
			r['Packets dropped'] = self.packets_dropped
			r['Packets missed'] = self.packets_missed
			r['Packets duplicate'] = self.packets_duplicate
			r['wait_for_AS'] = str(self.wait_for_AS)
			r['gps_lat'] = self.nodecfg.gps_lat
			r['gps_lon'] = self.nodecfg.gps_lon
			if self.last_data_pkt is None:
				r['last_data_pkt'] = {}
			else:
				r['last_data_pkt'] = self.last_data_pkt.save(True)
			if self.last_control_pkt is None:
				r['last_control_pkt'] = {}
			else:
				r['last_control_pkt'] = self.last_control_pkt.save(True)
		return r


	def get_firsthop(self):
		if len(self.via) == 0:
			firsthop = self.slid
		else:
			firsthop = self.via[0]
		return firsthop


	def set_state(self, new_state):
		was_up = self.is_state_up()
		old_state = self.state
		self.state = new_state
		is_state_up = self.is_state_up()

		if not was_up and is_state_up:
			logger.info("node %s now online: %s -> %s", self, old_state, new_state)
		elif was_up and not is_state_up:
			logger.info("node %s now offline: %s -> %s", self, old_state, new_state)
		if was_up != is_state_up:
			# publish node state on some mqtt
			pass

		if new_state == "TRANSMITTING":		#XXX check if node is sleeping or offline
			self.send_get_status()
		self.update()


	def is_offline(self):
		return self.state == "OFFLINE"


	def is_state_up(self):
		return self.state in Node.UPSTATES


	def is_overdue(self):
		if self.state == "OFFLINE":
			return False
		return (self.last_packet_rx_ts + self.nodecfg.max_silence) <= time.time()


	def publish_pkt(self, sl_pkt=None, resend=False, sub="control"):
		if resend:
			logger.debug("resending pkt: %s", sl_pkt)
			self.packets_resent += 1
		else:
			if self.wait_for_AS.is_waiting() and sl_pkt.sl_op != SL_OP.AN:
				logger.error("attempt to send pkt while waiting for AS, ignored: %s", sl_pkt)
				self.packets_dropped += 1
				return
		if len(sl_pkt.pkt) > SL_MAX_MESSAGE_LEN:
			logger.error("publish pkt to long(%s): %s", len(sl_pkt.pkt), sl_pkt)
			return
#		self.log_pkt(sl_pkt)
		self.packets_sent += 1
		self.mesh.packets_sent += 1
		if logging.DBG > 1: logger.debug("publish_pkt %s to node %s", sl_pkt, self.get_firsthop())
		_MQTT.publish(self.get_firsthop(), sl_pkt.pkt, sub=sub)
		self.last_packet_tx_ts = time.time()
		self.update()
		self.mesh.update(True)


	def send_ack_to_node(self, code):
		sl_pkt = Packet(slnode=self, sl_op=SL_OP.AN, payload=chr(code))	
		self.publish_pkt(sl_pkt)
		return


	def send_boot_cold(self):
		sl_pkt = Packet(slnode=self, sl_op=SL_OP.BC)
		self.publish_pkt(sl_pkt)
		return


	def send_get_status(self):
		sl_pkt = Packet(slnode=self, sl_op=SL_OP.GS)
		self.publish_pkt(sl_pkt)
		return


	def send_data_to_node(self, data): 
		if not self.is_state_up():
			self.packets_dropped += 1
			return "NodeDown"

		if self.wait_for_AS.is_waiting():
			self.packets_dropped += 1
			return "AckWait"

		bpayload = data
		logger.debug("send_data_to_node:: len %s, pkt %s", len(bpayload), bpayload)
		sl_pkt = Packet(slnode=self, sl_op=SL_OP.DN, payload=bpayload)
		self.last_control_pkt = sl_pkt
		self.publish_pkt(sl_pkt)
		self.wait_for_AS.set_wait(sl_pkt, do_insert=True)
		sl_pkt.insert()
		return "OK"


	def send_set_config(self): 
		if not self.is_state_up():
			self.packets_dropped += 1
			return "NodeDown"

		if self.wait_for_AS.is_waiting():
			self.packets_dropped += 1
			return "AckWait"

		bpayload = self.nodecfg.pack()
		logger.debug("send_set_config: len %s, pkt %s", len(bpayload), self.nodecfg)
		sl_pkt = Packet(slnode=self, sl_op=SL_OP.SC, payload=bpayload)
		self.publish_pkt(sl_pkt)
		self.wait_for_AS.set_wait(sl_pkt)
		return "OK"


	def send_testpacket(self, pkt):
		if not self.is_state_up():
			self.packets_dropped += 1
			return SL_OP.NC
		sl_pkt = Packet(slnode=self, sl_op=SL_OP.TD, payload=pkt)
		self.publish_pkt(sl_pkt)
		rc = self.get_response(timeout=SL_RESPONSE_WAIT_SEC) # No!
		logger.debug("send_packet %s got %s", sl_pkt, SL_OP.code(rc))
		return rc


	def check_duplicate_pkt_num(self, sl_pkt):
		pkt_num = sl_pkt.pkt_num
		last_packet_num = self.last_packet_num
		self.last_packet_num = pkt_num
		if last_packet_num == 0:			# we did not see packets from this node before
			return False
		if pkt_num == 0xFFFF:				# wrap
			self.last_packet_num = 0		# remote will skip 0
		if pkt_num == last_packet_num + 1:	# proper sequence
			return False
		if pkt_num == last_packet_num:		# duplicate
			logger.info("%s: received duplicate pkt %s", self, sl_pkt)
			return True
		if pkt_num != 1:					# remote restarted
			missed = pkt_num-(last_packet_num+1)
			self.packets_missed += missed
			logger.error("%s: %s pkts missed before %s", self, missed, sl_pkt)
		return False


	def store_data(self, sl_pkt):
		if sl_pkt.sl_op != SL_OP.DS:		# actual data
			logger.warning("store_data NOT storing non-DS data: %s", sl_pkt.sl_op)
			return
		if logging.DBG >= 1: logger.debug("store_data inserting into db")

		sl_pkt.insert()
		self.send_ack_to_node(0)
		try:
			payload = json.dumps(sl_pkt.payload)
		except:
			payload = sl_pkt.payload
		_MQTT.public_publish(self.name, payload)
		

	def post_data(self, sl_pkt):
		""" handle incoming messages on the ../data topic """
		if sl_pkt.is_data():
			if self.check_duplicate_pkt_num(sl_pkt):	# duplicate packet
				if sl_pkt.sl_op in Node.OPS_need_ack:
					logger.debug("post_data send AN on duplicate %s", SL_OP.code(sl_pkt.sl_op))
					self.send_ack_to_node(0)
				self.packets_duplicate += 1
				self.packets_dropped += 1
				return	# duplicate
		else:
			logger.error("%s got control pkt %s", self, sl_pkt)
			self.packets_dropped += 1
			return # NotForUs

		# set ts for all nodes on the via route
		for slid in sl_pkt.via:
			node = Node._table.find_one(slid)
			if node:
				node.last_packet_rx_ts = sl_pkt.ts
				if not node.is_state_up():
					node.set_state('TRANSMITTING')
				node.update()
			else:
				self.packets_dropped += 1
				logger.error("post_data: via node %s not on file", slid)

		# check for routing changes
		if self.via == []:
			self.via = sl_pkt.via
		elif self.via != sl_pkt.via:
			logger.warning("node %s routing changed, was %s is now %s", \
					self, self.via, sl_pkt.via)
			self.via = sl_pkt.via

		self.packets_received += 1
		self.mesh.packets_received += 1

		# logger.info("%s: received %s", self, sl_pkt)

		self.tr[sl_pkt.slid] = sl_pkt.rssi

		sl_op = sl_pkt.sl_op

		if sl_op == SL_OP.ON: # autocreate did set nodecfg
			self.wait_for_AS.clear_wait()		# give up 
			logger.debug('post_data: slid %d ONLINE', int(self.slid))

			new_nodecfg = SL_NodeCfgStruct(pkt=sl_pkt.bpayload)
			self.nodecfg.update(new_nodecfg)			
			self.send_set_config()
			self.set_state("ONLINE")
			self.last_node_restart_ts = time.time()
			logger.info('%s signed on', self)
		elif sl_op == SL_OP.OF:
			self.set_state("OFFLINE")

		elif sl_op == SL_OP.DS:
#			logger.debug('post_data: slid %d status %s', int(self.slid),sl_pkt.payload)
			self.last_data_pkt = sl_pkt
			self.store_data(sl_pkt)

		elif sl_op == SL_OP.SS:
#			logger.debug("post_data: slid %d status '%s'", int(self.slid),sl_pkt.payload)
			self.set_state(sl_pkt.payload)

		elif sl_op == SL_OP.AS:
			logger.debug('post_data: slid %d ACK:  %s', int(self.slid), 
						SL_AS_CODE[int(sl_pkt.bpayload[0])])
			pkt = self.wait_for_AS.stop_wait()		# done waiting, discard stashed packet
			if pkt is not None:
				pkt.insert()					# store pkt

		elif sl_op == SL_OP.TR:
			logger.debug('post_data: node %s test msg', sl_pkt.payload)

			try:
				test_pkt = TestPkt(pkt=sl_pkt.payload)
			except ValueError as e:
				logger.warning("post_incoming: cannot identify test data in %s", sl_pkt.payload)
				self.packets_dropped += 1
				return

			test_pkt.set_receiver_slid(sl_pkt.via)
			test_pkt.set_rssi(sl_pkt.rssi)
			if not test_pkt.pkt['slid'] in self.tr:
				self.tr[test_pkt.pkt['slid']] = []
			self.tr[test_pkt.pkt['slid']].append((test_pkt.pkt['pktno'], test_pkt.pkt['rssi']))
#			sl_log.post_incoming(test_pkt)

		self.last_packet_rx_ts = sl_pkt.ts

		# any pkt from node indicates it's up
		if not self.is_offline() and not self.is_state_up():
			self.set_state('TRANSMITTING')

		self.update()
		self.mesh.update(True)


	def periodic_check_for_AS(self):
		if self.wait_for_AS.is_waiting():
			rwait = self.wait_for_AS.wait_remaining()
			logger.debug("periodic_check: %s wait %s sec for AS ", self.name, rwait)
			if rwait <= 0:
				if self.wait_for_AS.inc_resend_count() > MAX_RESEND_COUNT:
					logger.info("resend limit reached for %s, giving up", self.wait_for_AS)
					self.wait_for_AS.clear_wait()
				else:
					pkt = self.wait_for_AS.restart_wait()
					self.publish_pkt(pkt, resend=True)


	def periodic_check(self):
		self.periodic_check_for_AS()
		if self.is_overdue() and self.is_state_up():
			self.set_state("OVERDUE")
		if not self.is_offline() and not self.is_state_up():	#XXX not offline or sleeping
			if self.last_packet_tx_ts != 0 and self.last_packet_tx_ts + MAXSILENCE < time.time():
				self.send_get_status()

	def get_response(self, timeout):
		try:
			data = self._response_q.get(timeout=timeout)
		except Empty:
			data = SL_OP.NC
		return data



#
# Packet
#
class BasePacket:
	keyfield = 'ts'
	data_header_fmt = '<BLHB%is'		# op, slid, pkt_num, rssi, payload"
	control_header_fmt = '<BLH%is'		# op, slid, pkt_num, payload"

	def __init__(self, slnode, sl_op = None, rssi = 0, payload = None, pkt = None):

		self.slid = None
		self.rssi = 0
		self.via = []
		self.pkt_num = None
		self.payload = None
		self.ts = time.time()
		self.nodecfg = None
		if pkt is None and sl_op is None:
			return	# needs a load() to complete
		self.is_outgoing = pkt is None

		if self.is_outgoing:				# construct pkt
			self.slid = slnode.slid
			self.construct(slnode, sl_op, rssi, payload)
		else:								# deconstruct pkt
			if not self.deconstruct(pkt):
				logger.error("deconstruct pkt to short: %s, %s", len(pkt), pkt)
				raise SteamLinkError("deconstruct pkt to short");


	def __str__(self):
		ULOn = "[4m"
		BOn = "[7m"
		BOff = "[0m"
		try:
			return "Packet N%s(%s)%s" % ( self.slid, self.pkt_num, BOn+SL_OP.code(self.sl_op)+BOff)
		except Exception as e:
			return "Packet NXXX(%s)??" % e


	def is_data(self, sl_op = None):
		if sl_op is None:
			sl_op = self.sl_op
		if sl_op is None:
			logger.error("packet op not yet known")
			raise SteamLinkError("packet op not yet known");
		return (sl_op & 0x1) == 1


	def construct(self, slnode, sl_op, rssi, payload):
		self.slid = slnode.slid
		self.sl_op = sl_op
		self.rssi = rssi + 256
		if self.sl_op == SL_OP.ON:
			self.payload = payload.pack()	# payload is a nodecfg 
		else:
			self.payload = payload
		if logging.DBG > 2: logger.debug("SteamLinkPacket payload = %s", payload);
		if self.payload is not None:
			if type(self.payload) == type(b''):
				self.bpayload = self.payload
			else:
				self.bpayload = self.payload.encode('utf8')
		else:
			self.bpayload = b''

		self.pkt_num = slnode.set_pkt_number(self)
		if self.is_data():	# N.B. store never sends data
			sfmt = Packet.data_header_fmt % len(self.bpayload)
			if logging.DBG > 0: logger.debug("pack: %s %s %s %s %s", SL_OP.code(self.sl_op), \
					self.slid, self.pkt_num, self.rssi, self.bpayload)
			self.pkt = struct.pack(sfmt,
					self.sl_op, self.slid, self.pkt_num, 256 - self.rssi, self.bpayload)
		else:
			sfmt = Packet.control_header_fmt % len(self.bpayload)
			self.pkt = struct.pack(sfmt,
					self.sl_op, self.slid, self.pkt_num, self.bpayload)
			if len(slnode.via) > 0:
				for via in slnode.via[::-1]:
					self.bpayload = self.pkt
					sfmt = Packet.control_header_fmt % len(self.bpayload)
					self.pkt = struct.pack(sfmt, SL_OP.BN, via, 0, self.bpayload)
			if logging.DBG > 1:
				for l in phex(self.pkt, 4):
					logger.debug("pkt c:  %s", l)



	def deconstruct(self, pkt):
		self.pkt = pkt
		if logging.DBG > 1:
			for l in phex(pkt, 4):
				logger.debug("pkt:  %s", l)

		if pkt[0] == SL_OP.BS:		# un-ecap all
			while pkt[0] == SL_OP.BS:
				payload_len = len(pkt) - struct.calcsize(Packet.data_header_fmt % 0)
				sfmt = Packet.data_header_fmt % payload_len
				self.sl_op, slid, self.pkt_num, self.rssi, self.bpayload \
						= struct.unpack(sfmt, pkt)

				self.via.append(slid)
				pkt = self.bpayload
				if logging.DBG > 1: logger.debug("pkt un-ecap BS from P%s(%s)BS, len %s rssi %s", slid, self.pkt_num,  len(pkt), 256-self.rssi)
			self.rssi = self.rssi - 256

		if self.is_data(pkt[0]):
			if len(pkt) < struct.calcsize(Packet.data_header_fmt % 0):
				logger.error("deconstruct data pkt to short: %s", len(pkt))
				return False;
			payload_len = len(pkt) - struct.calcsize(Packet.data_header_fmt % 0)
			sfmt = Packet.data_header_fmt % payload_len
			self.sl_op, self.slid, self.pkt_num, rssi, self.bpayload \
						= struct.unpack(sfmt, pkt)
		else:
			if len(pkt) < struct.calcsize(Packet.control_header_fmt % 0):
				logger.error("deconstruct control pkt to short: %s", len(pkt))
				return False;
			payload_len = len(pkt) - struct.calcsize(Packet.control_header_fmt % 0)
			sfmt = Packet.control_header_fmt % payload_len
			self.sl_op, self.slid, self.pkt_num, self.bpayload \
						= struct.unpack(sfmt, pkt)
		self.payload = None

		if self.sl_op == SL_OP.ON:
			try:
				self.nodecfg = SL_NodeCfgStruct(pkt=self.bpayload)
			except SteamLinkError as e:
				logger.error("deconstruct: %s", e)
				return False
			logger.debug("Node config is %s", self.nodecfg)

		if len(self.bpayload) > 0:
			try:
				self.payload = self.bpayload.decode('utf8').strip('\0')
			except Exception as e:
				pass

		if self.sl_op in [ SL_OP.DN, SL_OP.DS]:
			try:
				jpayload = json.loads(self.payload)
				self.payload = jpayload
			except:
				pass

		return True


#
# Packet
#
class Packet(BasePacket, Item):
	def __init__(self, slnode = None, sl_op = None, rssi = 0, payload = None, pkt = None, _load=None):

		BasePacket.__init__(self, slnode, sl_op, rssi, payload, pkt)
		if pkt is None and slnode is None:
			return	# needs a load() to complete
		self.is_outgoing = pkt is None

		if self.is_outgoing:				# construct pkt
			self.set_node(slnode)
		(Item).__init__(self, None, _load)


	def set_node(self, node):
		if logging.console:
			ULOn = "[4m"
			BOn = "[7m"
			BOff = "[0m"
		else:
			ULOn = ""
			BOn = ""
			BOff = ""

		self.node = node
		if self.is_outgoing:
			direction = "send"
			via = "direct" if self.node.via == [] else "via %s" % self.node.via
		else:
			direction = "received"
			via = "direct" if self.via == [] else "via %s" % self.via

		logger.debug("pkt: %s %s %s: %s", ULOn+ direction, via+BOff,  self, self.payload)


	def load(self, data):
		super().load(data)
		self.sl_op = SL_OP.val(self.sl_op)	# xlate from 2-letter-code to val


	def save(self, withvirtual=False):
		r = {}
		r['sl_op'] = SL_OP.code(self.sl_op)
		r['pkt_num'] = self.pkt_num
		r['slid'] = self.slid
		r[Packet.keyfield] = self.ts
		r['rssi'] = self.rssi
		r['ts'] = self.ts
		r['via'] = self.via
		if type(self.payload) == type(b''):
			r['payload'] = repr(self.payload)
		else:
			r['payload'] = self.payload
		if withvirtual:
			r["Time"] = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(self.ts))
			r["op"] = SL_OP.code(self.sl_op)
		return r


#
# TestPkt
#
class TestPkt:
	packet_counter = 1
	def __init__(self, gps=None, text=None, from_slid=None, pkt=None):
		self.pkt = {}
		if text != None and from_slid != None:	# construct pkt
#			self.pkt['lat'] = gps['lat']
#			self.pkt['lon'] = gps['lon']
			self.pkt['slid'] = from_slid
			self.pkt['pktno'] = TestPkt.packet_counter
			self.pkt['text'] = text
			self.pkt['directon'] = 'send'
			TestPkt.packet_counter += 1
		else:									# deconstruct string
			r = pkt.split('|',4)
			self.pkt['lat'] = float(r[0])
			self.pkt['lon'] = float(r[1])
			self.pkt['slid'] = int(r[2])
			self.pkt['pktno'] = int(r[3])
			self.pkt['directon'] = 'recv'
			self.pkt['text'] = r[4]
		ts = time.strftime("%Y-%m-%d_%H:%M:%S", time.localtime())
		self.pkt[Packet.keyfield] = ts


	def get_pktno(self):
		return self.pkt['pktno']


	def set_receiver_slid(self, recslid):
		self.pkt['recslid'] = recslid


	def set_rssi(self, rssi):
		self.pkt['rssi'] = rssi


	def pkt_string(self):
		return "%(lat)0.4f|%(lon)0.4f|%(slid)s|%(pktno)s|%(text)s" % self.pkt


	def json(self):
		return json.dumps(self.pkt)


	def __str__(self):
		return "TESTP(%s)" % str(self.pkt)


#
# NodeRoutes
#
class NodeRoutes:
	def __init__(self, dest, via):
		self.dest = dest
		self.via = via


	def __str__(self):
		svia = ""
		for v in self.via:
			svia += "->0x%02x" % v
		return "VIA(%d: %s" % (self.dest, svia)


#
# LogData
#
class LogData:
	""" Handle incoming pkts on the ../data topic """
	def __init__(self, conf):
		self.conf = conf
		self.logfile = open(conf["file"],"a+")
		self.pkt_inq = Queue()
		self.nodes_online = 0


	def log_state(self, slid, new_state):
		logger.debug("logdata node %d %s", slid, new_state)
		self.nodes_online += 1 if new_state == "ONLINE" else -1


	def post_incoming(self, pkt):
		""" a pkt arrives """

		self.log_pkt(pkt, "receive")
		self.pkt_inq.put(pkt, "recv")


	def post_outgoing(self, pkt):
		""" a pkt is sent """
		self.log_pkt(pkt, "send")


	def log_pkt(self, pkt, direction):
		self.logfile.write(pkt.json()+"\n")
		self.logfile.flush()


	def wait_pkt_number(self, pktnumber, timeout, num_packets):
		""" wait for pkt with number pktnumber for a max of timeout seconds """
		lwait = timeout
		packets_seen = 0
		while True:
			now = time.time()
			try:
				test_pkt = self.pkt_inq.get(block=True, timeout=lwait)
				packets_seen += 1
			except Empty:
				test_pkt = None
			logger.debug("wait_pkt_number pkt %s", test_pkt)
			waited = time.time() - now
			if test_pkt and test_pkt.pkt['pktno'] == pktnumber and packets_seen == num_packets:
				return pktnumber
			if waited >= lwait or test_pkt.pkt['pktno'] > pktnumber:	# our pkt will never arrive
				return None
			lwait -= waited

"""
 message = {
     'table_name':
	 'key_field':
	 'restrict_by': 
	 'start_key':
	 'start_item_number':
	 'end_key':
	 'count':
	 'stream_tag':
  }
"""


def add_csearch(webnamespace, sid, message):

	table_name = message['table_name']
	try:
		table = Table.tables[table_name]
	except KeyError as e:
		return { 'error': 'Table %s not found. Availabe are %s' % (str(e), list(Table.tables.keys())) }

	csearchkey = CSearchKey(**message)

	try:
		csearchkey = table.add_csearch(webnamespace, csearchkey, sid)
	except KeyError as e:
		msg = 'could not add search %s' % (str(e))
		logger.info('add_search fail: %s', msg)
		return { 'error': msg }

	#  force update
	for cs in table.csearches:
		table.csearches[cs].force_update(sid)

	if logging.DBG > 1: logger.debug("add_csearch sid %s csearchkey %s", sid, csearchkey)
	res = {
			'start_key': csearchkey.start_key,
			'end_key': csearchkey.end_key,
			'count': csearchkey.count,
			'start_item_number': csearchkey.start_item_number,
			'total_item_count':  csearchkey.total_item_count,
			'at_start':  csearchkey.at_start,
			'at_end':  csearchkey.at_end,
		}
	return res


def drop_csearch(webnamespace, sid, message):

	table_name = message.get('table_name', None)
	if table_name == None:		# all all tables, i.e. disconnect
		table_list = list(Table.tables.values())
	else:
		try:
			table = Table.tables[table_name]
		except KeyError as e:
			return { 'error': 'Table %s not found' % str(e) }
		table_list = [table]

	for tab in table_list:
		tab.drop_sid_from_csearch(sid)

	return { 'Success': True }


def run_cmd(webnamespace, sid, message):
	res = steam_root.handle_web_command(sid, message)
	return res


# tables = {}
def SteamSetup():
	Steam._table = DbTable(Steam, keyfield="steam_id", tablename="Steam")
	Mesh._table = DbTable(Mesh, keyfield="mesh_id", tablename="Mesh")
	Node._table = DbTable(Node, keyfield="slid", tablename="Node")
	Packet._table = DbTable(Packet, keyfield="ts", tablename="Packet")

