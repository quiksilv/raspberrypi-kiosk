import os, requests, logging

class Datasource:

	def __init__(self):
		self.url = "http://localhost:8080"
		#self.login = os.environ['BITCOIN_LOGIN']
		#self.token = os.environ['BITCOIN_PASSWORD']
		self.login = 'testuser'
		self.token = 'testpassword'
	def get_price(self):
		data = {
			'action': 'query_price',
			'dummy_variable' : 1,
			'signature' : 'ASDRGH112321312',
			'login': self.login,
			'token': self.token
		}
		r = self.post(data)
		return r.json()
	def buy_bitcoin(self):
		data = {
			'action':'buy',
			'dummy_variable' : 1,
			'signature' : 'ASDRGH112321312',
			'login': self.login,
			'token': self.token,
			'amount': 5,
		}
		r = self.post(data)
		return r.json()
	def post(self, data):
		url = self.url
		try :
			response = requests.post(url, data)
		except requests.ConnectionError:
			response = []
		return response
