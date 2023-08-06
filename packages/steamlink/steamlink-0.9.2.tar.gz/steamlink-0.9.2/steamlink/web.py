import asyncio
import socketio
import io
import re
import ipaddress
import hashlib
import hmac
import os
import json
import socket
import aiohttp_jinja2
import jinja2
import yaml

from zeroconf import ServiceInfo, Zeroconf
from aiohttp import web
from aiohttp.log import access_logger, web_logger


from .steamlink import (
	Mesh,
	Node,
	Steam,
	Packet,
	add_csearch,
	run_cmd,
	drop_csearch
)
from .linkage import (
	Item,
)

from .const import __version__

import logging
logger = logging.getLogger(__name__)

from yarl import URL

class DisplayConfiguration:

	def __init__(self, dir_list, file_name):
		self.data = {}
		for sdir in dir_list:
			file_path = sdir + file_name
			if os.path.exists(file_path):
				f = open(file_path)
				self.data = yaml.load(f)
				f.close()
				break
		if self.data == {}:
			raise FileNotFoundError

	def row_wise(self):
		rows = {}
		for key in self.data:
			item = self.data[key]
			try:
				if item['row'] not in rows:
					logger.debug("web rowise: itemrow %s ", item['row'])
					rows[item['row']] = []
				rows[item['row']].append(item)
			except KeyError:
				logger.error("DisplayConfiguration: No key found")
		return rows

class NavBar:

	def __init__(self, dir_list):
		self.yamls = []
		for sdir in dir_list:
			file_path = sdir + '/navbar.yaml'
			if os.path.exists(file_path):
				f = open(file_path)
				yamls = yaml.load(f)
				f.close()
				self.yamls += yamls

#
# WebNameSpace
#
class WebNamespace(socketio.AsyncNamespace):
	def __init__(self, webapp):
		self.webapp = webapp
		self.namespace = self.webapp.namespace

		super().__init__(self.namespace)
		logger.debug("WebNamespace registered for namespace %s", self.namespace)


	def on_connect(self, sid, environ):
		logger.debug("WebNamespace connect %s",str(environ['REMOTE_ADDR']))


	def on_disconnect(self, sid):
		logger.debug("WebNamespace disconnect")
		res = drop_csearch(self, sid, {})


#	async def on_need_log(self, sid, data):
#		logger.debug("WebNamespace need_log %s", data)
#	#	await self.emit('my_response', {'data': data['data']} ) #, room=sid, namespace=self.namespace)
#		node = data.get('id',None)
#		if  not node in Node.name_idx:
#			return "NAK"
#		try:
#			r = Node.name_idx[node].console_pkt_log(data['key'], int(data['count']))
#		except:
#			return "NAK"
#		return "ACK"


	async def on_startstream(self, sid, message):
		logger.debug("WebNamespace on_startstream --> %s", message)
		try:
			res = add_csearch(self, sid, message)
		except KeyError as e:
			msg = '%s field missing in request' % e
			logger.warning(msg)
			raise
			return {'error': msg }
		except TypeError as e:
			msg = '%s, probably incorrect value for start_key' % e
			logger.warning(msg)
			raise
			return {'error': msg }

		logger.debug("WebNamespace on_startstream <-- %s", res)
		return res


	async def on_leave(self, sid, message):

		logger.debug("WebNamespace on_leave %s", message)

		res = drop_csearch(self, sid, message)
		return { 'success': True }


	# dict with: cmd, node_name, data
	# cmds are: DN SC
	async def on_cmd(self, sid, message):
		logger.debug("WebNamespace on_cmd --> %s", message)
		try:
			ret = run_cmd(self, sid, message)
			res = { "Success": ret }
		except  Exception as e:
			res = { "Success": False, "Error": "cmd failed: %s" % e }

		logger.debug("WebNamespace on_cmd <-- %s", res)
		return res

#
# WebApp
#
class WebApp(object):

	def __init__(self, namespace, sio, conf, loop = None):
		self.name = "WebApp"
		self.conf = conf
		self.minupdinterval = conf['minupdinterval']
		self.sio = sio
		self.namespace = namespace
		self.loop = loop
		self.con_upd_q = asyncio.Queue(loop=self.loop)
		self.app = web.Application()
		self.app._set_loop(self.loop)
		self.sio.attach(self.app)
		self.app['websockets'] = []
		self.app.router.add_get('/config.json', self.config_json)

		self.libdir = os.path.dirname(os.path.abspath(__file__))
		self.working_dir = conf['working_dir']
		self.static_dir = self.libdir+'/html/static'
		self.templates_dir = self.libdir+'/html/templates'
		self.user_templates_dir = self.working_dir+'/html/templates'
		self.app.router.add_route('GET', '/', self.route_handler)
		self.app.router.add_route('GET', '/favicon.ico', self.favicon_handler)
		self.app.router.add_route('GET', '/ghwh', self.ghwh_handler)
		self.app.router.add_route('POST', '/ghwh', self.ghwh_handler)
		self.app.router.add_route('GET', '/{file_name}', self.route_handler)


		self.app.router.add_static('/static', self.static_dir)
		self.app.on_cleanup.append(self.web_on_cleanup)
		self.app.on_shutdown.append(self.web_on_shutdown)
		self.backlog = 128

		aiohttp_jinja2.setup(self.app, loader=jinja2.FileSystemLoader(self.templates_dir))

		self.shutdown_timeout = self.conf['shutdown_timeout']
	#	self.api_password = conf['api_password']
		self.ssl_certificate = conf['ssl_certificate']
		self.ssl_key = conf['ssl_key']
		self.ssl_context = None
		self.access_log_format = 'XXX %a %t "%r" %s %b "%{Referer}i" "%{User-Agent}i"'
		self.access_log = access_logger
		access_logger.setLevel(logging.WARN)	# N.B. set in config

		self.host = conf['host']
		self.port = conf['port']
	#	self._handler = None
	#	self.server = None

	def __getstate__(self):
		return {'MyClass': 'WebApp'}

	async def qstart(self):
		logger.info("%s starting q handler", self.name)
		self.con_upd_res = await self.console_update_loop()


	async def start(self):
		logger.info("%s starting, server %s port %s", self.name, self.host,  self.port)
		self.sio.register_namespace(WebNamespace(self))
		self.runner = web.AppRunner(self.app)
		await self.runner.setup()
		self.site = web.TCPSite(self.runner, 'localhost', self.port)
		await self.site.start()

		logger.debug("%s: app started", self.name)

		scheme = 'https' if self.ssl_context else 'http'


		my_ip_address = socket.gethostbyname(socket.gethostname())
		desc = {'version': __version__}
		self.zeroconf_info = ServiceInfo("_http._tcp.local.",
					"SteamLink Store._http._tcp.local.",
					socket.inet_aton(my_ip_address), self.port, 0, 0,
					desc, "steamlink.local.")
		self.zeroconf = Zeroconf()
		self.zeroconf.register_service(self.zeroconf_info)

		make_handler_kwargs = dict()
		make_handler_kwargs['access_log_format'] = self.access_log_format
		make_handler_kwargs['access_log'] = self.access_log

		self.handler = self.app.make_handler(loop=self.loop, **make_handler_kwargs)

		self.server = await self.loop.create_server(
						self.handler, self.host, self.port,
						ssl=self.ssl_context,
						backlog=self.backlog)

	def stop(self):
		logger.info("%s done running", self.name)
		self.zeroconf.unregister_service(self.zeroconf_info)
		self.server.close()
#		somethong int this list may take 20 seconds to shutdown gracefully
		self.loop.run_until_complete(self.server.wait_closed())
		self.loop.run_until_complete(self.app.shutdown())
#		self.loop.run_until_complete(self.handler.shutdown(self.shutdown_timeout))
#		self.loop.run_until_complete(self.runner.cleanup())


	async def config_json(self, request):
		rj = json.dumps(self.conf)
		return web.Response(text=rj, content_type='application/json')


	def web_on_cleanup(self, app):
		logger.info("web closing down")


	async def web_on_shutdown(self, app):
		for ws in self.app['websockets']:
			await ws.close(code=WSCloseCode.GOING_AWAY, message='Server shutdown')


	def queue_itemlist_update(self, csitems, force):
		if 'webupd' in logging.DBGK: logger.debug("queue_itemlist_update for %s item %s", csitem.csearch.search_id, csitem.item)
		asyncio.ensure_future(self.con_upd_q.put([csitems, force]), loop=self.loop)



	def queue_item_update(self, csitem, force):
		if 'webupd' in logging.DBGK: logger.debug("queue_item_update for %s item %s", csitem.csearch.search_id, csitem.item)
		asyncio.ensure_future(self.con_upd_q.put([csitem, force]), loop=self.loop)


	async def console_update_loop(self):
		logger.info("%s q handler", self.name)
		while True:
			upd_csitem, upd_force =  await self.con_upd_q.get()
			if 'webupd' in logging.DBGK: logger.debug("console_update_loop %s force %s", upd_csitem, upd_force)
			if upd_csitem is None:
				break
			if type(upd_csitem) == type([]):
				data = []
				for cs_item in upd_csitem:
					data.append(cs_item.console_update(upd_force))
				upd_csitem = upd_csitem[0]
			else:
				data = upd_csitem.console_update(upd_force)
			tag = upd_csitem.csearch.csearchkey.stream_tag
			room = upd_csitem.csearch.search_id
			if 'webupd' in logging.DBGK: logger.debug("emit_loop event: %s room:%s data: %s", upd_csitem.csearch.csearchkey.stream_tag,  upd_csitem.csearch.search_id, data)
			await self.sio.emit(tag,
					data = data,
					namespace = self.namespace,
					room = room)
			upd_csitem.update_sent()
			self.con_upd_q.task_done()

		logger.debug("console_update_loop done")


	async def console_alert(self, lvl, smsg):
		if len(smsg) > 110:
			msg = smsg[:110]+"..."
		else:
			msg = smsg
		alert = {'lvl': lvl, 'msg': msg }
		await self.sio.emit('alert', alert, namespace = self.namespace)


	def send_console_alert(self, lvl, msg):
		asyncio.ensure_future(self.console_alert(lvl, msg), loop=self.loop)


	async def favicon_handler(self, request):
		return None


	async def ghwh_handler(self, request):
		""" GitHub WebHook handler """

		if request.method == 'GET':
			return web.Response(text='OK')
		elif request.method == 'POST':
			# Store the IP address of the requester
			request_ip = request.remote

#			# If VALIDATE_SOURCEIP is set to false, do not validate source IP
#			if self.conf.get('repo_validate_sourceip', False):
#
#				# If GHE_ADDRESS is specified, use it as the hook_blocks.
#				if self.conf.get('repo_ghe_address', None):
#					hook_blocks = self.conf.get('repo_ghe_address')
#				# Otherwise get the hook address blocks from the API.
#				else:
#					hook_blocks = requests.get('https://api.github.com/meta').json()['hooks']
#
#				# Check if the POST request is from github.com or GHE
#				for block in hook_blocks:
#					if ipaddress.ip_address(request_ip) in ipaddress.ip_network(block):
#						break  # the remote_addr is within the network range of github.
#				else:
#					if str(request_ip) != '127.0.0.1':
#						return web.Response(text='invalid IP', status=403)

			request_data = await request.text()
			payload = json.loads(request_data)

			if request.headers.get('X-GitHub-Event') == "ping":
				logger.debug("ghwh ping data %s", payload)
				return web.json_response({'msg': 'Hi!'})
			if request.headers.get('X-GitHub-Event') != "push":
				return web.json_response({'msg': "wrong event type"})

			full_name = "%s/%s" % (self.conf['repo_owner'], self.conf['repo_name'])
			if full_name != payload['repository']['full_name']:
				logger.debug("ghwh push repo not ours %s", payload['repository']['full_name'])
			else:
				logger.debug("ghwh push for repo %s", full_name)

				# Check if POST request signature is valid
				key = self.conf.get('repo_key', None)
				if key is None:
					logger.debug("ghwh no key")
				else:
					signature = request.headers.get('X-Hub-Signature')
					if signature[:5] == "sha1=":
						signature = signature[5:]
					logger.debug("sig %s %s %s %s", type(key), key, type(signature), signature)
					if type(key) != type(b''):
						key = key.encode()
					if type(request_data) !=  type(b''):
						request_data = request_data.encode()
					mac = hmac.new(key, msg=request_data, digestmod=hashlib.sha1)
					if not hmac.compare_digest(mac.hexdigest(), signature):
						logger.warning("ghwh auth failed mac %s sig %s", mac.hexdigest(), signature)
						return web.Response(text='auth fail', status=403)

					ci_cmd = self.conf.get("repo_ci_command", None)
					if ci_cmd is not None:
						logger.warning("ghwh upgrading running version")
						os.system(ci_cmd + "&")

			return web.Response(text='OK')



	async def route_handler(self, request):
		content_dirs = [self.templates_dir, self.user_templates_dir] 
		nav = NavBar(content_dirs)

		if request.rel_url.path == '/':
			file_name = 'index'
		else:
			file_name = request.match_info['file_name']
			# file_name = str(request.rel_url.path).rstrip('/')
		logger.debug("web route_handler: filename: %s, request.rel_url %s", file_name, request.rel_url)
		try:
			dc = DisplayConfiguration(content_dirs,  '/' + file_name + '.yaml')
		except FileNotFoundError as e:
			return web.Response(text="No such file: %s" % file_name, status=404)
		for qk in request.query:
			if 'web' in logging.DBGK: logger.debug("web route_handler: Query' : %s =%s", qk, request.query[qk])
			try:
				partial, key = qk.split('.', 1)
			except:
				if 'web' in logging.DBGK: logger.debug("web route_handler: Query key with no '.' : %s", qk)
				continue
			if not partial in dc.data:
				if 'web' in logging.DBGK: logger.debug("web route_handler: partial not in yaml : %s", partial)
				continue
			if 'web' in logging.DBGK: logger.debug("web route_handler: dc.data[partial] : %s", dc.data[partial])
			i = request.query[qk]
			try:
				i = int(i)
			except:
				pass

			if (key == "restrict_by"):
				dc.data[partial][key][0]['value'] = i
			else:
				dc.data[partial][key] = i

		if 'web' in logging.DBGK: logger.debug("webapp handler %s", dc.data)
		context = { 'context' : dc.row_wise(), 'navbar' : nav.yamls }

		if not (os.path.isfile(self.templates_dir + '/'+ file_name + '.html')):
			file_name = 'index'
		response = aiohttp_jinja2.render_template(file_name + '.html', request, context)
#		response.headers['Content-Language'] = 'en'
		return response
