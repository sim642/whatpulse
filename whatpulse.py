import requests
from lxml import etree
from lxml.builder import E

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

class ProxyTestRequest(Request):
	def __init__(self):
		super().__init__('testproxy')

class Response(object):
	def __init__(self, tree):
		self.tree = tree
		self.type = self.tree.get('type')

	def get(self, xpath):
		return self.tree.xpath(xpath)[0]

	@classmethod
	def parse(cls, tree):
		type = tree.get('type')
		print(etree.tostring(tree), type)
		return cls.types.get(type, Response)(tree)


class ProxyTestResponse(Response):
	def __init__(self, tree):
		super().__init__(tree)

		self.status = self.get('./status/text()')
		self.msg = self.get('./msg/text()')

Response.types = {
	'testproxy': ProxyTestResponse
}

class Session(object):
	def __init__(self):
		self.s = requests.Session()
		self.s.headers.update({'User-Agent': 'WhatPulse Client ' + client_version})

	def request(self, *reqs):
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
		resps = tree.xpath('/server/responses/response')

		return Response.parse(resps[0])

