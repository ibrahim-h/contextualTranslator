# -*- coding: utf-8 -*-
# Copyright (C) Ibrahim Hamadeh, released under GPLv2.0
# See the file COPYING for more details.
#this module is aimed to get a specific piece in almaany.com page
#that contains the meaning of the selected word in contextual translation.

import textInfos
import urllib
import random
import re
import api, ui
from logHandler import log
import threading
import addonHandler
addonHandler.initTranslation()

#the function that specifies if a certain text is selected or not
#and if it is, returns text selected
def isSelectedText():
	obj=api.getFocusObject()
	treeInterceptor=obj.treeInterceptor
	if hasattr(treeInterceptor,'TextInfo') and not treeInterceptor.passThrough:
		obj=treeInterceptor
	try:
		info=obj.makeTextInfo(textInfos.POSITION_SELECTION)
	#except (RuntimeError, NotImplementedError):
	except:
		info=None
	if not info or info.isCollapsed:
		return False
	else:
		return info.text

#list of fake user agent
userAgentList=['Mozilla/5.0', 'Safari/537.36', 'Chrome/67.0.3396.99', 'iexplore/11.0.9600.19080', 'Trident/7.0', 'SeaMonkey/2.40', 'Wyzo/3.6.4.1', 'OPR/54.0.2952.64']
'''
regex1= '(<h1 class="section">[\s\S]+<h1 class="section">[\s\S]+?)<h[23456]'
regex2= '(<h1 class="section">[\s\S]+?)<h[23456]'
regex3= '(<h1>[\s\S]+?)<h[23456]'
'''

regex= '(<h1>[\s\S]+?</h1>[\s\S]+?)<h[23456]'

class MyThread(threading.Thread):
	def __init__(self, text, base_url):
		# text is the word or phrase to be translated.
		threading.Thread.__init__(self)
		self.text= text
		self.base_url= base_url
		self.meaning= ""
		self.daemon=True
		self.error= False

	def run(self):
		text= self.text
		url= self.base_url + urllib.parse.quote(text)
		request= urllib.request.Request(url)
		request.add_header('User-Agent', random.choice(userAgentList))
		try:
			handle = urllib.request.urlopen(request)
			html= handle.read().decode(handle.headers.get_content_charset())
			handle.close()
#			log.info(html)
		except Exception as e:
			log.info('', exc_info= True)
			self.error= str(e)
		else:
			try:
				content= re.findall(regex, html)
				content= content[0]
			except Exception as e:
				log.info('', exc_info= True)
				self.error= str(e)
			else:
				page= content +"<p> <a href=%s>"%(url) +"Look for the meaning on the web site</a></p>"
				self.meaning= page
