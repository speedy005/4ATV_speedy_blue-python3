#!/usr/bin/env python
# -*- encoding: utf-8 -*-
# Coded by tsiegel (c) 2019
from Renderer import Renderer 
from enigma import ePixmap, eTimer
import os
import glob

class speedyVWeather3AnimatedPicons(Renderer):
	def __init__(self):
		Renderer.__init__(self)
		self.delay = 100
		self.currentPos = 0
		self.filecount = 0
		self.Path = '/usr/share/enigma2/VWeather3/WeatherPicons/'

	def applySkin(self, desktop, parent):
		attribs = [ ]
		for (attrib, value) in self.skinAttributes:
			if attrib == "path":
				if os.path.isdir(value):
					if str(value).endswith('/'):
						self.Path = value
					else:
						self.Path = value + '/'
				else:
					if str(value).endswith('/'):
						self.Path = '/usr/share/enigma2/' + value
					else:
						self.Path = '/usr/share/enigma2/' + value + '/'
				str(self.Path).replace('//','/')
			elif attrib == "delay":
				self.delay = int(value)
			else:
				attribs.append((attrib,value))
		self.skinAttributes = attribs
		return Renderer.applySkin(self, desktop, parent)

	GUI_WIDGET = ePixmap

	def changed(self, what):
		if self.instance:
			if (what[0] != self.CHANGED_CLEAR):
				try:
					if os.path.isdir(self.Path + self.source.text):
						self.animate(self.Path + self.source.text, False)
					elif os.path.isfile(self.Path + self.source.text + '.png') :
						self.animate(self.Path + self.source.text + '.png', True)
					else:
						self.animate('.png', True)
				except Exception as ex:
					print "Fehler in VWeather3AnimatedPicons changed : " + str(ex)

	def animate(self, path, static=True):
		if static:
			self.instance.setScale(1)
			self.instance.setPixmapFromFile(path)
		else:
			self.filecount = len(os.listdir(path))
			if self.filecount > 0:
				self.piclist = glob.glob(path + "/*.png")
			else:
				self.piclist = ['/usr/share/enigma2/skin_default/icons/input_error.png']
			self.picchanger = eTimer()
			self.picchanger.callback.append(self.changepic)
			self.picchanger.start(self.delay, True)

	def changepic(self):
		if self.currentPos == 0:
			self.currentPos = self.filecount
		self.picchanger.stop()
		self.instance.setScale(1)
		try:
			self.instance.setPixmapFromFile(self.piclist[self.currentPos - 1])
		except Exception as ex:
			print "Fehler in VWeather3AnimatedPicons changepic : " + str(ex)
		self.currentPos -= 1
		self.picchanger.start(self.delay, True)
