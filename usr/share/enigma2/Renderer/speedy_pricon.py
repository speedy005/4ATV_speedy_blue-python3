# -*- coding: utf-8 -*-
# v1
# by digiteng...04.2020
# <widget source="session.Event_Now" render="pricon" position="59,471" size="60,60" zPosition="1" alphatest="blend">
# 	<convert type="infoMovie">PARENTAL_RATING</convert>
# </widget>
from Renderer import Renderer 
from enigma import ePixmap, loadPNG
from Tools.Directories import resolveFilename, SCOPE_CURRENT_SKIN

class speedy_pricon(Renderer):

	def __init__(self):
		Renderer.__init__(self)
		self.rateNm = ''


	GUI_WIDGET = ePixmap
	def changed(self, what):
		pratePath = resolveFilename(SCOPE_CURRENT_SKIN, 'parental')
		try:
			parentName = self.source.text
			if parentName :
				rateNm = pratePath + "FSK_{}.png".format(parentName)
				self.instance.setPixmap(loadPNG(rateNm))
				self.instance.show()
			else:
				self.instance.hide()
		except:
			return

