from .session import Session
from .requests import *

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
