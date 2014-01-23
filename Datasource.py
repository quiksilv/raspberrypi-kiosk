import os, requests, logging

class Datasource:

	def __init__(self):
		self.url = "http://localhost:8080/"
	def authenticate(self):
		url = self.url + "oauth/authorize"
		data = {
			'application_id' : 'APPLICATION_ID',
			'secret_key' : 'SECRET_KEY'
		}
		response = requests.get(url, data)
		return response.json()
	def action(self, action, data):
		url = self.url + "api/" + action
		r = self.get(url, data)
		return r.json()
	def get(self, url, data):
		headers = {
			'Accept': 'application/bitcoin.atm.v1',
			'Authorization': 'Bearer ' + self.token
		}
		try:
			response = requests.get(url, data, headers)
		except requests.ConnectionError:
			response = []
		return response
	def test(self):
		return requests.get("http://localhost:8080/status.php").json()
