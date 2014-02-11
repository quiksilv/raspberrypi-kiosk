import os, requests, logging

class Datasource:

	def __init__(self):
		self.url = "http://floating-dawn-7074.herokuapp.com/api/"
		self.username = "mark@squarepotato.com"
		self.password = "1qaz!QAZ"
		self.auth_token = ""
	def token(self):
		url = self.url + "token?username=" + self.username + "&password=" + self.password
		r = self.get(url, {})
		data = r.json()
		self.auth_token = data['token']
	def action(self, action, data):
		url = self.url + action + "?auth_token=" + self.auth_token
		r = self.get(url, data)
		return r.json()
	def get(self, url, data):
		try:
			response = requests.get(url, params=data)
		except requests.ConnectionError:
			response = []
		return response
