# -*- coding: utf-8 -*-
#Copyright (C) Ibrahim Hamadeh, released under GPLv2.0
#See the file COPYING for more details.
#This addon is aimed to get meaning of words using almaany.com contextual translation dictionary.
# The default gesture for the addon is: Alt+ Shift+ C.
#Open the addon dialog, write the word you want, tab and choose the dictionary, press enter and the meaning will be displayed in a separate browseable window.

import gui, wx
from gui import guiHelper
from scriptHandler import script
import config
import globalPluginHandler
from .myDialog import MyDialog
from logHandler import log

import addonHandler
addonHandler.initTranslation()

#default configuration 
configspec={
	"windowType": "integer(default=0)",
	"closeDialogAfterRequiringTranslation": "boolean(default= False)"
}
config.conf.spec["contextualTranslator"]= configspec

# Ensure one instance is running.
INSTANCE= None

class GlobalPlugin(globalPluginHandler.GlobalPlugin):
	# Translators: Category in input gestures dialog.
	scriptCategory= _('Contextual Translator')

	def __init__(self, *args, **kwargs):
		super(GlobalPlugin, self).__init__(*args, **kwargs)

		gui.settingsDialogs.NVDASettingsDialog.categoryClasses.append(ContextualTranslator)

	def terminate(self):
		gui.settingsDialogs.NVDASettingsDialog.categoryClasses.remove(ContextualTranslator)

	@script(
		# Translators: Message displayed in input help mode.
		description= _('Opens Contextual Translator dialog to get meaning of words.'),
		gesture= "kb:alt+shift+c"
		)
	def script_showDialog(self, gesture):
		global INSTANCE
		if not INSTANCE:
			d= MyDialog(gui.mainFrame)
#			log.info('after creating object')
			d.postInit()
			d.Raise()
			d.Show()
			INSTANCE= d
		else:
			INSTANCE.Raise()

#make  SettingsPanel  class
class ContextualTranslator(gui.SettingsPanel):
	# Translators: title of the dialog
	title= _("Contextual Translator")

	def makeSettings(self, sizer):
		settingsSizerHelper = guiHelper.BoxSizerHelper(self, sizer=sizer)

		# Translators: Type of windows to display translation result.
		windowTypes= [_("Default full browser"), _("Browser window only"), _("NVDA browseable message box(choose it after testing)")]
		self.resultWindowComboBox= settingsSizerHelper.addLabeledControl(
		# Translators: label of cumbo box to choose type of window to display result.
		_("Choose type of window To Display Result:"), 
		wx.Choice, choices= windowTypes)
		self.resultWindowComboBox.SetSelection(config.conf["contextualTranslator"]["windowType"])

		# Translators: label of the check box 
		self.closeDialogCheckBox=wx.CheckBox(self,label=_("Close Contextual Translator Dialog after requesting translation"))
		self.closeDialogCheckBox.SetValue(config.conf["contextualTranslator"]["closeDialogAfterRequiringTranslation"])
		settingsSizerHelper.addItem(self.closeDialogCheckBox)

	def onSave(self):
		config.conf["contextualTranslator"]["windowType"]= self.resultWindowComboBox.GetSelection()
		config.conf["contextualTranslator"]["closeDialogAfterRequiringTranslation"]= self.closeDialogCheckBox.IsChecked() 
