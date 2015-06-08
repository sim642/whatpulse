import requests
from lxml import etree
from lxml.builder import E
import datetime

client_version = '2.6.1'
type_os = 'linux' # windows, linux, macos

class Stats(object):
	def __init__(self, keys=0, clicks=0, download=0, upload=0, uptime=0):
		self.keys = keys
		self.clicks = clicks
		self.download = download
		self.upload = upload
		self.uptime = uptime

	def __repr__(self):
		return repr({
			'keys': self.keys,
			'clicks': self.clicks,
			'download': self.download,
			'upload': self.upload,
			'uptime': self.uptime
		})

	@staticmethod
	def parse(tree, name):
		ret = Stats()
		for elem in tree:
			if elem.tag.startswith(name):
				key = elem.tag[len(name):]
				value = int(elem.text)
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

class TokenResetRequest(Request):
	def __init__(self, client_token):
		super().__init__('resettoken')
		self.add_members({
			'client_token': client_token
		})

class StatusRequest(Request):
	def __init__(self, client_token):
		super().__init__('refresh_account_info')
		self.add_members({
			'client_token': client_token
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
		elems = self.tree.xpath(xpath)
		return elems[0] if len(elems) > 0 else None

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

		premium = self.get('./premium_expire/text()')
		if premium is not None:
			self.premium = datetime.datetime.strptime(premium, '%Y-%m-%d').date()
		else:
			self.premium = False

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

class TokenResetResponse(Response):
	def __init__(self, tree):
		super().__init__(tree)
		self.parse_members({
			'token': 'token'
		})

class StatusResponse(Response):
	def __init__(self, tree):
		super().__init__(tree)
		self.parse_members({
			'username': 'username',
			'computer': 'computer',
			'email': 'email'
		})

		self.total = Stats.parse(self.tree, 'total')
		self.rank = Stats.parse(self.tree, 'rank')

		premium = self.get('./premium_expire/text()')
		if premium is not None:
			self.premium = datetime.datetime.strptime(premium, '%Y-%m-%d').date()
		else:
			self.premium = False

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
	'resettoken': TokenResetResponse,
	'refresh_account_info': StatusResponse,
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
		self.computers = None
		self.computer = None

		self.userid = None
		self.computerid = None
		self.token = None

		self.client_token = None

		self.total = None
		self.rank = None

	def try_login(self, email, password):
		self.email = email
		self.password = password

		res = self.s.request(TryLoginRequest(self.email, self.password))
		self.hash = res.hash
		self.computers = res.computers

		return res

	def login(self, computer):
		self.computer = computer

		res = self.s.request(LoginRequest(self.email, self.hash, self.computer))
		self.userid = res.userid
		self.computerid = res.computerid
		self.username = res.username
		self.token = res.token

		self.total = res.total
		self.rank = res.rank
		self.premium = res.premium

		return res

	def client_login(self):
		res = self.s.request(ClientLoginRequest(self.userid, self.computerid, self.hash))
		self.client_token = res.client_token

		return res

	def set_password(self, password):
		self.password = password

		res = self.s.request(PasswordRequest(self.client_token, self.password))
		self.hash = res.hash

		return res

	def reset_token(self):
		res = self.s.request(TokenResetRequest(self.client_token))
		self.token = res.token

		return res

	def refresh(self):
		res = self.s.request(StatusRequest(self.client_token))
		self.username = res.username
		self.computer = res.computer
		self.email = res.email

		self.total = res.total
		self.rank = res.rank
		self.premium = res.premium

		return res

	def pulse(self, stats):
		res = self.s.request(PulseRequest(self.client_token, self.token, stats))
		self.token = res.token

		self.total = res.total
		self.rank = res.rank

		return res
