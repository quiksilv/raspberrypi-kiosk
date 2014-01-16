import os
import requests
import logging
import hashlib
import time
import random

class TShop:

	def __init__(self):
		self.url = "https://fm.transfer-to.com/cgi-bin/shop/topup"
		self.login = os.environ['TSHOP_LOGIN']
		self.token = os.environ['TSHOP_PASSWORD']
	def post(self, data):
		url = self.url
		try :
			response = requests.post(url, data)
		except requests.ConnectionError:
			response = []
		return response
	def calculateMd5(self):
		key = str(time.time() ).replace(".","") + str(random.randint(1,1000) )
		m = hashlib.md5(self.login + self.token + key)
		return {
			'md5' : m.hexdigest(), 
			'key' : key
		}
	"""
		convert text with line breaks to hash
	"""
	def TextToHash(self, text):
		obj = {}
		lines = text.split("\r\n")
		for line in lines:
			if line:
				pair = line.split("=")
				obj[pair[0] ] = pair[1]
		for key in obj.keys():
			if obj[key].find(",") != -1:
				array = self.ListToArray(obj[key])
				obj[key] = array
		return obj
	"""
		convert comma separated list to array
	"""
	def ListToArray(self, slist):
		array = []
		strings = slist.split(",")
		for string in strings:
			if string:
				array.append(string)
		return array
	def ping(self):
		auth = self.calculateMd5()
		data = {
			'action' : 'ping',
			'login' : self.login,
			'md5' : auth['md5'],
			'key' : auth['key']
		}
		r = self.post(data)
		return self.TextToHash(r.text)
	def msisdn_info(self, destination_msisdn):
		auth = self.calculateMd5()
		data = {
			'action' : 'msisdn_info',
			'login' : self.login,
			'md5' : auth['md5'],
			'key' : auth['key'],
			'destination_msisdn' : destination_msisdn,
			'return_service_fee' : 1
		}
		r = self.post(data)
		return self.TextToHash(r.text)
	def pricelist(self, content):
		auth = self.calculateMd5()
		data = {
			'action' : 'pricelist',
			'login': self.login,
			'md5' : auth['md5'],
			'key' : auth['key'],
			'info_type' : 'operator',
			'content' : content #'1310'
		}
		r = self.post(data)
		return self.TextToHash(r.text)
	def topup(self, msisdn, destination_msisdn, product):
		auth = self.calculateMd5()
		data = {
			'action' : 'topup',
			'login': self.login,
			'md5' : auth['md5'],
			'key' : auth['key'],
			'msisdn' : msisdn,
			'destination_msisdn' : destination_msisdn,
			'product' : product,
			'return_timestamp' : 1,
			'return_service_fee' : 1,
			'return_promo' : 1,
			'msisdn' : '6582500361',
			'sender_sms' : 'yes',
			'sender_text' : 'test sms from machine'
		}
		r = self.post(data)
		return self.TextToHash(r.text)
