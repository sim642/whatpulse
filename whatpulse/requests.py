from . import config
from lxml import etree
from lxml.builder import E

class Request(object):
	def __init__(self, type):
		self.tree = (
			E.request({'type': type},
				E.type_os(config.type_os),
				E.client_version(config.client_version)
			)
		)
		self.form = {}

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

class ComputerIDRequest(Request):
	def __init__(self, userid, computer):
		super().__init__('get_computer_id')
		self.add_members({
			'userid': userid,
			'computer': computer
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

class PremiumCheckRequest(Request):
	def __init__(self, client_token):
		super().__init__('check_premium')
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

class UploadComputerinfoRequest(Request):
	def __init__(self, client_token, computer_info):
		super().__init__('upload_computerinfo')
		self.add_members({
			'client_token': client_token
		})
		self.form['computer_info'] = computer_info

__all__ = ["Request", "ProxyTestRequest", "TryLoginRequest", "LoginRequest",
		   "ClientLoginRequest", "PasswordRequest", "ComputerIDRequest",
		   "TokenResetRequest", "StatusRequest", "PremiumCheckRequest",
		   "PulseRequest", "UploadComputerinfoRequest"]
