# -*- coding: utf-8 -*-
# by digiteng...04.2020
# <widget render="infoEvent" source="session.Event_Now" position="244,360" size="300,130" font="Regular; 14" halign="left" valign="top" zPosition="1" foregroundColor="foreground" backgroundColor="background" transparent="0" />
from Renderer import Renderer
from Components.VariableText import VariableText
from enigma import eLabel, eTimer
from urllib2 import urlopen, quote

import json
import re
import os
import socket

omdb_api = '4d13638a'

class speedy_infoEvent(Renderer, VariableText):

	def __init__(self):
		Renderer.__init__(self)
		VariableText.__init__(self)

		self.intCheck()

	def intCheck(self):
		try:
			socket.setdefaulttimeout(0.5)
			socket.socket(socket.AF_INET, socket.SOCK_STREAM).connect(("8.8.8.8", 53))
			return True
		except:
			return False

	GUI_WIDGET = eLabel

	def changed(self, what):
		if what[0] == self.CHANGED_CLEAR:
			self.text = ''
		else:
			self.delay()

	def infos(self):
		event = self.source.event
		if event:
			evnt = event.getEventName()
			try:
				evntN = re.sub("([\(\[]).*?([\)\]])|(: odc.\d+)|(\d+: odc.\d+)|(\d+ odc.\d+)|(:)|( -(.*?).*)|(,)", "", evnt)
				evntNm = evntN.replace("Die ", "The ").replace("Das ", "The ").replace("und ", "and ").replace("LOS ", "The ").rstrip()
				if self.intCheck() == True:
					# url_tmdb = "https://api.themoviedb.org/3/search/multi?api_key=87241fc3a18a22a33f8ce28edf4e796a&query={}".format(quote(evntNm))
					# try:
						# original_name = json.load(urlopen(url_tmdb))['results'][0]['original_name']
						# evntNm = original_name
					# except:
						# pass
					url_omdb = 'https://www.omdbapi.com/?apikey=%s&t=%s' %(omdb_api, quote(evntNm))
					data = json.load(urlopen(url_omdb))
					open("/tmp/url_omdb", "w").write(url_omdb)
					Title = data['Title']
					imdbRating = data['imdbRating']
					Country = data['Country']
					Year = data['Year']
					Rated = data['Rated']
					Genre = data['Genre']
					Awards = data['Awards']

					if Title != "N/A" or Title != "":
						open("/tmp/rating", "w").write("%s\n%s"%(imdbRating, Rated))
						self.text = "Title : %s\nYear : %s\nImdb : %s\nCountry: %s\nRate: %s\nGenre : %s\nAwards : %s" %(str(Title),str(Year),str(imdbRating),str(Country),str(Rated),str(Genre),str(Awards))
					else:
						if os.path.exists("/tmp/rating"):
							os.remove("/tmp/rating")
						return ""
				else:
					return ""
			except:
				if os.path.exists("/tmp/rating"):
					os.remove("/tmp/rating")
				return ""
		else:
			return ""

	def delay(self):
		self.timer = eTimer()
		self.timer.callback.append(self.infos)
		self.timer.start(100, True)
