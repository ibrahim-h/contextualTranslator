# -*- coding: utf-8 -*-
# Copyright (C) Ibrahim Hamadeh, released under GPLv2.0
# See the file COPYING for more details.
#This module is responsible for displaying Contextual Translation dialog

import wx
import queueHandler
import config
import sys
import webbrowser
from .fetchtext import MyThread
from .fetchtext import isSelectedText
from .getbrowsers import getBrowsers
from tones import beep
import time
import subprocess
import threading
import tempfile
import ui
import os
import addonHandler
addonHandler.initTranslation()
#browsers as dictionary with label as key, and executable path as value.
browsers= getBrowsers()

def appIsRunning(app):
	'''Checks if specific app is running or not.'''
	processes= subprocess.check_output('tasklist', shell=True).decode('mbcs')
	return app in processes

def openBrowserWindow(label, meaning, directive, default= False):
	html= """
	<!DOCTYPE html>
	<meta charset=utf-8>
	<title>{title}</title>
	<meta name=viewport content='initial-scale=1.0'>
	""".format(title= _('Contextual Translation')) + meaning 
	temp= tempfile.NamedTemporaryFile(delete=False)
	path = temp.name + ".html"
	f = open(path, "w", encoding="utf-8")
	f.write(html)
	f.close()
	if default:
		webbrowser.open(path)
	else:
		subprocess.Popen(browsers[label] + directive + path)
	t=threading.Timer(30.0, os.remove, [f.name])
	t.start()

#dictionaries name and url
dictionaries_nameAndUrl= [
	('إنجليزي ⇔ عربي, عربي ⇔ إنجليزي', 'https://www.almaany.com/en/context/ar-en/'),
	('فرنسي ⇔ عربي, عربي ⇔ فرنسي', 'https://www.almaany.com/fr/context/ar-fr/'),
	('إسباني ⇔ عربي, عربي ⇔ إسباني', 'https://www.almaany.com/es/context/ar-es/'),
	('تركي ⇔ عربي, عربي ⇔ تركي', 'https://www.almaany.com/tr/context/ar-tr/'),
	('ألماني ⇔ عربي, عربي ⇔ ألماني', 'https://www.almaany.com/de/context/ar-de/'),
	('روسي ⇔ عربي, عربي ⇔ روسي', 'https://www.almaany.com/ru/context/ar-ru/'),
	('برتغالي ⇔ عربي, عربي ⇔ برتغالي', 'https://www.almaany.com/pt/context/ar-pt/'),
	('عربي ⇐ فارسي', 'https://www.almaany.com/fa/context/ar-fa/'),
	('فارسي ⇐ عربي', 'https://www.almaany.com/fa/context/fa-ar/'),
	('اندونيسي ⇔ عربي, عربي ⇔ اندونيسي', 'https://www.almaany.com/id/context/ar-id/'),
	('عربي ⇐ اردو', 'https://www.almaany.com/ar/context/ar-ur/'),
	('اردو ⇐ عربي', 'https://www.almaany.com/ur/context/ur-ar/')
]

class MyDialog(wx.Dialog):
	def __init__(self, parent,  word=""):
		# Translators: Title of dialog.
		title= _('Contextual Translator')
		super(MyDialog, self).__init__(parent, title = title, size = (300, 500))
		# Word to be translated.
		self.word= word
		#list of available dictionaries
		self.dictionaries= [name for name, url in dictionaries_nameAndUrl]

		panel = wx.Panel(self, -1)
		# Translators: Label of text control.
		editTextLabel= wx.StaticText(panel, -1, _("Enter a word or a phrase"))
		editBoxSizer =  wx.BoxSizer(wx.HORIZONTAL)
		editBoxSizer.Add(editTextLabel, 0, wx.ALL, 5)
		self.editTextControl= wx.TextCtrl(panel)
		editBoxSizer.Add(self.editTextControl, 1, wx.ALL|wx.EXPAND, 5)

		cumboSizer= wx.BoxSizer(wx.HORIZONTAL)
		# Translators: Label of cumbo box to choose a dictionary.
		cumboLabel= wx.StaticText(panel, -1, _("Choose Dictionary"))
		cumboSizer.Add(cumboLabel, 0, wx.ALL, 5)
		self.cumbo= wx.Choice(panel, -1, choices= self.dictionaries)
		cumboSizer.Add(self.cumbo, 1, wx.EXPAND|wx.ALL, 5)

		buttonSizer = wx.BoxSizer(wx.VERTICAL)
		# Translators: Label of OK button.
		self.ok= wx.Button(panel, -1, _('OK'))
		self.ok.SetDefault()
		self.ok.Bind(wx.EVT_BUTTON, self.onOk)
		buttonSizer.Add(self.ok, 0,wx.ALL, 10)
		# Translators: Label of Cancel button.
		self.cancel = wx.Button(panel, wx.ID_CANCEL, _('cancel'))
		self.cancel.Bind(wx.EVT_BUTTON, self.onCancel)
		buttonSizer.Add(self.cancel, 0, wx.EXPAND|wx.ALL, 10)
		mainSizer = wx.BoxSizer(wx.VERTICAL)
		mainSizer.Add(editBoxSizer, 1, wx.EXPAND|wx.ALL, 10)
		mainSizer.Add(cumboSizer, 1, wx.EXPAND|wx.ALL,10)
		mainSizer.Add(buttonSizer, 0, wx.EXPAND|wx.ALL, 5)
		panel.SetSizer(mainSizer)

	def postInit(self):
		if isSelectedText():
			self.editTextControl.SetValue(isSelectedText())
		self.cumbo.SetSelection(0)
		self.editTextControl.SetFocus()

	def getMeaning(self, text, base_url):
		t= MyThread(text, base_url)
		t.start()
		while not t.meaning and not t.error and t.is_alive():
			beep(500, 100)
			time.sleep(0.5)
		t.join()

		title= u'الترجمة السياقية'
		useDefaultFullBrowser= config.conf["contextualTranslator"]["windowType"]== 0
		useBrowserWindowOnly= config.conf["contextualTranslator"]["windowType"]== 1
		useNvdaMessageBox= config.conf["contextualTranslator"]["windowType"]== 2
		if t.meaning and useDefaultFullBrowser:
			openBrowserWindow('default', t.meaning, directive= '', default= True)
		elif t.meaning and useBrowserWindowOnly:
			if 'Firefox' in browsers and not appIsRunning('firefox.exe'):
				openBrowserWindow('Firefox', t.meaning, directive= ' --kiosk ')
			elif 'Google Chrome' in browsers and not appIsRunning('chrome.exe'):
				openBrowserWindow('Google Chrome', t.meaning, directive= ' -kiosk ')
			elif 'Internet Explorer' in browsers:
				openBrowserWindow('Internet Explorer', t.meaning, directive= ' -k -private ')
		elif t.meaning and useNvdaMessageBox:
			queueHandler.queueFunction(queueHandler.eventQueue, ui.browseableMessage, t.meaning, title=title, isHtml=True)
			return
		elif t.error:
			if t.error== "HTTP Error 410: Gone":
				msg= "No meaning found"
			elif t.error== "<urlopen error [Errno 11001] getaddrinfo failed>":
				msg= "Most likely no internet connection"
			else:
				msg= t.error
			queueHandler.queueFunction(queueHandler.eventQueue, ui.message, _("Sorry, An Error Happened({})".format(msg)))

	def onOk(self, e):
		# word or phrase to be translated.
		word= self.editTextControl.GetValue()
		# stripping white spaces.
		word= word.strip()
		if not word:
			# Return focus to edit control.
			self.editTextControl.SetFocus()
			return
		else:
			# Selecting the dictionary.
			i= self.cumbo.GetSelection()
			# The url is the second item in the tuple.
			dict_url= dictionaries_nameAndUrl[i][1]
			self.getMeaning(word, dict_url)
			closeDialogAfterRequiringTranslation= config.conf["contextualTranslator"]["closeDialogAfterRequiringTranslation"]
			if closeDialogAfterRequiringTranslation:
				wx.CallLater(4000, self.Destroy)

	def onCancel (self, e):
		self.Destroy()
