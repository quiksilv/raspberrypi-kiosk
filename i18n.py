# -*- coding: utf-8 -*-
 
import os, sys
import locale
import gettext

APP_NAME = "default"
class i18n:
	def __init__(self): 
		# Change this variable to your app name!
		#  The translation files will be under
		#  @LOCALE_DIR@/@LANGUAGE@/LC_MESSAGES/@APP_NAME@.mo
		 
		# This is ok for maemo. Not sure in a regular desktop:
		APP_DIR = os.path.dirname(os.path.abspath(__file__) )
		LOCALE_DIR = os.path.join(APP_DIR, 'locale') # .mo files will then be located in APP_Dir/i18n/LANGUAGECODE/LC_MESSAGES/
		 
		# Now we need to choose the language. We will provide a list, and gettext
		# will use the first translation available in the list
		#
		#  In maemo it is in the LANG environment variable
		#  (on desktop is usually LANGUAGES)
		DEFAULT_LANGUAGES = os.environ.get('LANG', '').split(':')
		DEFAULT_LANGUAGES += ['en_US']
		 
		lc, encoding = locale.getdefaultlocale()
		if lc:
		    loc = [lc]
		 
		# Concat all languages (env + default locale),
		#  and here we have the languages and location of the translations
		loc += DEFAULT_LANGUAGES
		self.mo_location = LOCALE_DIR
		# Lets tell those details to gettext
		#  (nothing to change here for you)
		gettext.install(True, localedir=None, unicode=1)
		 
		gettext.find(APP_NAME, self.mo_location)
		 
		gettext.textdomain (APP_NAME)
		 
		gettext.bind_textdomain_codeset(APP_NAME, "UTF-8")
		self.language = gettext.translation(APP_NAME, self.mo_location, languages=loc, fallback=True)
	def set_language(self, language):
		if language == 'id_ID':
			loc = ['id_ID', 'id_ID.utf8', 'id_ID']
		elif language == 'zh_CN':
			loc = ['zh_CN', 'zh_CN.utf8', 'zh.CN']
		elif language == 'bn_BD':
			loc = ['bn_BD', 'bn_BD.utf8', 'bn.DB']
		elif language == 'tl_PH':
			loc = ['tl_PH', 'tl_PH.utf8', 'tl_PH']
		elif language == 'en_US':
			loc = ['en_US', 'en_US.utf8', 'en_US']
		self.language = gettext.translation(APP_NAME, self.mo_location, languages=loc, fallback=True)
	def get_language(self):
		return self.language
	def install(self):
		self.language.install()
