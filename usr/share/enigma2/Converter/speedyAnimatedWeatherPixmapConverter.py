# -*- coding: UTF-8 -*-
from Tools.Directories import fileExists, pathExists
from Components.Converter.Converter import Converter
from Components.Element import cached
from Components.config import config, configfile
from Components.Console import Console as iConsole
from Components.Language import language
from Poll import Poll
import os
import gettext
import time
from xml.dom.minidom import parseString

weather_city = config.plugins.weathermsn.city.value
degreetype = config.plugins.weathermsn.degreetype.value
windtype = config.plugins.weathermsn.windtype.value
weather_location = config.osd.language.value.replace('_', '-')
if weather_location == 'en-EN':
	weather_location = 'en-US'

time_update = 20
time_update_ms = 3000

class speedyAnimatedWeatherPixmapConverter(Poll, Converter, object):

	def __init__(self, type):
		Converter.__init__(self, type)
		Poll.__init__(self)
		self.iConsole = iConsole()
		self.poll_interval = time_update_ms
		self.poll_enabled = True		

	@cached
	def getText(self):
                info = "none"
                Picontuday = ""
                Piconprow = ""
                Piconnow = ""
                Piconday2 = ""
                Piconday3 = ""
                Piconday4 = ""
		if not fileExists("/tmp/weathermsn2.xml"):
			self.iConsole.ePopen("wget -P /tmp -T2 'http://weather.service.msn.com/data.aspx?weadegreetype=%s&culture=%s&weasearchstr=%s&src=outlook' -O /tmp/weathermsn2.xml" % (degreetype, weather_location, weather_city))
		elif fileExists("/tmp/weathermsn2.xml"):
			if int((time.time() - os.stat("/tmp/weathermsn2.xml").st_mtime)/60) >= time_update:
				self.iConsole.ePopen("wget -P /tmp -T2 'http://weather.service.msn.com/data.aspx?weadegreetype=%s&culture=%s&weasearchstr=%s&src=outlook' -O /tmp/weathermsn2.xml" % (degreetype, weather_location, weather_city))
                if fileExists("/tmp/weathermsn2.xml"):
		      handler = open('/tmp/weathermsn2.xml')
		      xml_response = handler.read()
		      handler.close()
		      if xml_response != "" or xml_response is not None:
			  #try:
                                  dom = parseString(xml_response)
                                  weather = dom.getElementsByTagName("current")[0]
                                  Picontuday = str(weather.getAttributeNode("skycode").nodeValue)

                                  weather = dom.getElementsByTagName("forecast")[0]
                                  Piconprow = str(weather.getAttributeNode("skycodeday").nodeValue)

                                  weather = dom.getElementsByTagName("forecast")[1]
                                  Piconnow = str(weather.getAttributeNode("skycodeday").nodeValue)

                                  weather = dom.getElementsByTagName("forecast")[2]
                                  Piconday2 = str(weather.getAttributeNode("skycodeday").nodeValue)

                                  weather = dom.getElementsByTagName("forecast")[3]
                                  Piconday3 = str(weather.getAttributeNode("skycodeday").nodeValue)                                    

                                  weather = dom.getElementsByTagName("forecast")[4]
                                  Piconday4 = str(weather.getAttributeNode("skycodeday").nodeValue)
                                  info = "%s,%s,%s,%s,%s,%s" % (Picontuday, Piconprow, Piconnow, Piconday2, Piconday3, Piconday4)
			 # except:
				#info = "none"
                return info

	text = property(getText)

	def changed(self, what):
		Converter.changed(self, what)
