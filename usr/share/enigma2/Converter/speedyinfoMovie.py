# -*- coding: utf-8 -*-
# by digiteng...04.2020
#    <widget source="session.Event_Now" render="Label" position="210,166" size="679,100" font="Regular; 14" backgroundColor="tb" zPosition="2" transparent="1" halign="left" valign="top">
#      <convert type="infoMovie">INFO</convert>
#    </widget>
#    <ePixmap pixmap="LiteHD2/star_b.png" position="0,277" size="200,20" alphatest="blend" zPosition="0" transparent="1" />
#    <widget source="session.Event_Now" render="Progress" pixmap="LiteHD2/star.png" position="0,277" size="200,20" alphatest="blend" zPosition="1" transparent="1">
#      <convert type="infoMovie">STARS</convert>
#    </widget>
# <widget source="session.Event_Now" render="pricon" position="59,471" size="60,60" zPosition="3" alphatest="blend">
# 	<convert type="infoMovie">PARENTAL_RATING</convert>
# </widget>
from Components.Converter.Converter import Converter
from Components.Element import cached
from enigma import eTimer
from urllib2 import urlopen, quote
import json
import re
import os



api = '4d13638a'

class speedyinfoMovie(Converter, object):

	def __init__(self, type):
		Converter.__init__(self, type)
		self.type = type
		self.delay()

	@cached
	def getText(self):
		event = self.source.event
		if event:
			if self.type == 'INFO':
				try:
					evnt = event.getEventName()
					try:
						p = '((.*?))[;=:-].*?(.*?)'
						e1 = re.search(p, evnt)
						ffilm = re.sub('\W+','+', e1.group(1))
					except:
						w = re.sub("([\(\[]).*?([\)\]])", " ", evnt)
						ffilm = re.sub('\W+','+', w)
					url = 'https://www.omdbapi.com/?apikey=%s&t=%s' %(api, ffilm.lower())
					data = json.load(urlopen(url))
					
					title = data['Title']
					rtng = data['imdbRating']
					country = data['Country']
					year = data['Year']
					rate = data['Rated']
					genre = data['Genre']
					award = data['Awards']

					if title:
						open("/tmp/rating","w").write("{}\n{}".format(rtng, rate))
						return "\nTitle : {} \nImdb : {} \nYear : {}, {} \nRate : {} \nGenre : {} \nAwards : {}".format(title, rtng, str(country), str(year.encode('utf-8')), rate, genre, award)
					else:
						if os.path.exists("/tmp/rating"):
							os.remove("/tmp/rating")
				except:
					if os.path.exists("/tmp/rating"):
						os.remove("/tmp/rating")
					return ""

			fd = event.getShortDescription() + "\n" + event.getExtendedDescription()
			if self.type == 'PARENTAL_RATING':
				try:
					ppr = ["[aA]b ((\d+))", "[+]((\d+))"]
					for i in ppr:
						prr = re.search(i, fd)
						if prr:
							return prr.group(1)
					else:
						if os.path.exists("/tmp/rating"):
							with open("/tmp/rating") as f:
								prate = f.readlines()[1]
							if prate == "TV-Y7":
								rate = "6"
							elif prate == "TV-14":
								rate = "12"
							elif prate == "TV-PG":
								rate = "16"
							elif prate == "TV-MA":
								rate = "18"
							elif prate == "PG-13":
								rate = "16"
							elif prate == "R":
								rate = "18"
							else:
								pass
								
							if rate:
								return rate
				except:
					return ""


		else:
			if os.path.exists("/tmp/rating"):
				os.remove("/tmp/rating")
			return ""

	text = property(getText)

	@cached
	def getValue(self):
		try:
			if self.type == 'STARS':
				rating = "/tmp/rating"
				if os.path.exists(rating):
					with open(rating) as f:
						rating = f.readlines()[0]
						if rating != "N/A":
							return int(10*(float(rating)))
				else:
					event = self.source.event
					if event:
						evnt = event.getEventName()
						try:
							p = '((.*?))[;=:-].*?(.*?)'
							e1 = re.search(p, evnt)
							ffilm = re.sub('\W+','+', e1.group(1))
						except:
							w = re.sub("([\(\[]).*?([\)\]])", " ", evnt)
							ffilm = re.sub('\W+','+', w)
						url = 'https://www.omdbapi.com/?apikey=%s&t=%s' %(api, ffilm.lower())
						data = json.load(urlopen(url))
						rating = data['imdbRating']
						if rating != "N/A":
							return int(10*(float(rating)))
						else:
							return 0
						
						
		except:
			return 0

	value = property(getValue)
	range = 100





	def delay(self):
		self.timer = eTimer()
		self.timer.callback.append(self.getText)
		self.timer.callback.append(self.getValue)
		self.timer.start(100, True)
