import requests
from lxml import etree
from lxml.builder import E
import re

client_version = '2.6.1'
type_os = 'linux'

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
	p = re.compile('(total|rank)(\w+)')

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

		self.total = {}
		self.rank = {}
		for elem in self.tree.xpath('./*'):
			m = self.p.match(elem.tag)
			if m:
				{'total': self.total, 'rank': self.rank}[m.group(1)][m.group(2)] = elem.text # TODO: unuglify code

Response.types = {
	'testproxy': ProxyTestResponse,
	'trylogin': TryLoginResponse,
	'login': LoginResponse
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


