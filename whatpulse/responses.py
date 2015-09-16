from .stats import Stats
import datetime

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
		#print(etree.tostring(tree), type)
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

class ComputerIDResponse(Response):
	def __init__(self, tree):
		super().__init__(tree)
		self.parse_members({
			'computerid': 'computerid'
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

		premium = self.get('./premium_expire/text()') # does unlimited premium exist?
		if premium is not None:
			self.premium = datetime.datetime.strptime(premium, '%Y-%m-%d').date()
		else:
			self.premium = False

class PremiumCheckResponse(Response):
	def __init__(self, tree):
		super().__init__(tree)
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
	'get_computer_id': ComputerIDResponse,
	'resettoken': TokenResetResponse,
	'refresh_account_info': StatusResponse,
	'check_premium': PremiumCheckResponse,
	'pulse': PulseResponse
}
