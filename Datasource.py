import os, requests, logging

class Datasource:

	def __init__(self):
		self.url = "http://floating-dawn-7074.herokuapp.com/api/"
		self.auth_token = "53f1dc609eb798c7d15fcffa2423a4ed56884480617dbc3eb6c270d88d511c46"
	def authenticate(self):
		url = self.url + "oauth/authorize"
		data = {
			'application_id' : 'APPLICATION_ID',
			'secret_key' : 'SECRET_KEY'
		}
		response = requests.get(url, data)
		return response.json()
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
