import requests
from lxml import etree
from lxml.builder import E
import re

client_version = '2.6.1'
type_os = 'linux'

class Stats(object):
	def __init__(self, keys=0, clicks=0, download=0, upload=0, uptime=0):
		self.keys = keys
		self.clicks = clicks
		self.download = download
		self.upload = upload
		self.uptime = uptime

	@staticmethod
	def parse(tree, name):
		ret = Stats()
		for elem in tree:
			if elem.tag.startswith(name):
				key = elem.tag[len(name):]
				value = elem.text
				setattr(ret, key, value)
		return ret

	dump_map = {
		'keys': 'keycount',
		'clicks': 'clickcount',
		'download': 'download',
		'upload': 'upload',
		'uptime': 'uptime'
	}

	def dump(self):
		elems = []
		for key, to in self.dump_map.items():
			elem = etree.Element(to)
			elem.text = str(getattr(self, key))
			elems.append(elem)
		return elems

class Request(object):
	def __init__(self, type):
		self.tree = (
			E.request({'type': type},
				E.type_os(type_os),
				E.client_version(client_version)
			)
		)

	def add_members(self, members):
		for key, value in members.items():
			elem = etree.Element(key)
			elem.text = value
			self.tree.append(elem)

class ProxyTestRequest(Request):
	def __init__(self):
		super().__init__('testproxy')

class TryLoginRequest(Request):
	def __init__(self, email, password):
		super().__init__('trylogin')
		self.add_members({
			'email': email,
			'password': password
		})

class LoginRequest(Request):
	def __init__(self, email, hash, computer):
		super().__init__('login')
		self.add_members({
			'email': email,
			'passwordhash': hash,
			'computer': computer
		})

class ClientLoginRequest(Request):
	def __init__(self, userid, computerid, hash):
		super().__init__('client_login')
		self.add_members({
			'userid': userid,
			'computerid': computerid,
			'passwordhash': hash
		})

class PasswordRequest(Request):
	def __init__(self, client_token, password):
		super().__init__('get_password_hash')
		self.add_members({
			'client_token': client_token,
			'real_password': password
		})

class PulseRequest(Request):
	def __init__(self, client_token, token, stats):
		super().__init__('pulse')
		self.add_members({
			'client_token': client_token,
			'token': token
		})
		for elem in stats.dump():
			self.tree.append(elem)

class Response(object):
	def __init__(self, tree):
		self.tree = tree
		self.type = self.tree.get('type')
		self.parse_members({
			'status': 'status' # TODO: eliminate duplication
		})

	def get(self, xpath):
		return self.tree.xpath(xpath)[0]

	def parse_members(self, members):
		for key, value in members.items():
			setattr(self, value, self.get('./' + key + '/text()'))

	@classmethod
	def parse(cls, tree):
		type = tree.get('type')
		print(etree.tostring(tree), type)
		return cls.types.get(type, Response)(tree)


class ProxyTestResponse(Response):
	def __init__(self, tree):
		super().__init__(tree)
		self.parse_members({
			'msg': 'result'
		})

class TryLoginResponse(Response):
	def __init__(self, tree):
		super().__init__(tree)
		self.parse_members({
			'trylogin_result': 'result',
			'passwordhash': 'hash'
		})

		self.computers = self.tree.xpath('./computers/computer/text()')

class LoginResponse(Response):
	def __init__(self, tree):
		super().__init__(tree)
		self.parse_members({
			'email': 'email',
			'computer': 'computer',
			'computerid': 'computerid',
			'userid': 'userid',
			'token': 'token',
			'username': 'username',
			'passwordhash': 'hash'
		})

		self.total = Stats.parse(self.tree, 'total')
		self.rank = Stats.parse(self.tree, 'rank')

class ClientLoginResponse(Response):
	def __init__(self, tree):
		super().__init__(tree)
		self.parse_members({
			'client_token': 'client_token'
		})

class PasswordResponse(Response):
	def __init__(self, tree):
		super().__init__(tree)
		self.parse_members({
			'passwordhash': 'hash'
		})

class PulseResponse(Response):
	def __init__(self, tree):
		super().__init__(tree)
		self.parse_members({
			'token': 'token'
		})

		self.total = Stats.parse(self.tree, 'total')
		self.rank = Stats.parse(self.tree, 'rank')

Response.types = {
	'testproxy': ProxyTestResponse,
	'trylogin': TryLoginResponse,
	'login': LoginResponse,
	'client_login': ClientLoginResponse,
	'get_password_hash': PasswordResponse,
	'pulse': PulseResponse
}

class Session(object):
	def __init__(self):
		self.s = requests.Session()
		self.s.headers.update({'User-Agent': 'WhatPulse Client ' + client_version})

	def requests(self, reqs):
		requests = E.requests()
		for req in reqs:
			requests.append(req.tree)

		tree = (
			E.client(
				requests
			)
		)

		xml = etree.tostring(tree, encoding='UTF-8', xml_declaration=True) # declaration uses ' instead of "

		r = self.s.post('https://client.whatpulse.org/v1.1/', verify='whatpulse.pem', data={'client_version': client_version, 'xml': xml})
		tree = etree.fromstring(r.text)
		ress = tree.xpath('/server/responses/response')

		ret = []
		for res in ress:
			ret.append(Response.parse(res))

		return ret

	def request(self, req):
		return self.requests([req])[0]

class Client(object):
	def __init__(self):
		self.s = Session()

		self.email = None
		self.password = None
		self.hash = None
		self.client_token = None
		self.token = None
