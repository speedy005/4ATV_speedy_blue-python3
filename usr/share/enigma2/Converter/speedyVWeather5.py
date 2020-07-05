# -*- encoding: utf-8 -*-
####################################################################################################
####################################################################################################
#                                                                                                  #
#	Weatherconverter for VU+                                                                       #
#	Coded by tsiegel (c) 2019                                                                      #
#	THX NaseDC, schomi, Nathanael2316, gordon55, Maggy                                             #
#	Support: www.vuplus-support.com                                                                #
#                                                                  	                               #
#	This converter is licensed under the Creative Commons                                          #
#	Attribution-NonCommercial-ShareAlike 3.0 Unported License.                                     #
#	To view a copy of this license, visit http://creativecommons.org/licenses/by-nc-sa/3.0/        #
#	or send a letter to Creative Commons, 559 Nathan Abbott Way, Stanford, California 94305, USA.  #
#                                                                                                  #
#	This plugin is NOT free software. It is open source, you are allowed to                        #
#	modify it (if you keep the license), but it may not be commercially                            #
#	distributed other than under the conditions noted above.                                       #
#                                                                                                  #
#...........................................R53....................................................#
####################################################################################################
####################################################################################################

from Components.Converter.Converter import Converter
from Components.Element import cached
from Components.Converter.Poll import Poll
from Components.config import getConfigListEntry, ConfigEnableDisable, \
    ConfigYesNo, ConfigText, ConfigClock, ConfigNumber, ConfigSelection, \
    ConfigDateTime, config, NoSave, ConfigSubsection, ConfigInteger, ConfigIP, configfile, fileExists, ConfigNothing, ConfigDescription
from Components.config import config
from Screens.MessageBox import MessageBox
from Tools import Notifications
from twisted.web.client import getPage
from operator import itemgetter
from enigma import eTimer
from time import time, localtime, mktime, strftime, sleep, strptime
from datetime import timedelta, datetime
from tempfile import mkstemp
from os import fdopen
from bs4 import BeautifulSoup
from math import pi, cos
import xml.etree.ElementTree as ET
import datetime
import json
import os
import requests
import shutil
from socket import *
import threading
import re
import string
import ConfigParser
import stat
import glob


####### language settings ######
from Components.Language import language
from Tools.Directories import resolveFilename, SCOPE_LANGUAGE, SCOPE_PLUGINS
import gettext

pluginpath= '/usr/lib/enigma2/python/Plugins/Extensions/VWeather3/'
picturepath = '/usr/share/enigma2/VWeather3/'
PORT = 50010
BUFSIZE = 8182

Wetterregionen = {
	'shh' : 'dwhh',
	'mvp' : 'dwph',
	'nib' : 'dwhg',
	'nrw' : 'dweh',
	'bbb' : 'dwpg',
	'saa' : 'dwlh',
	'thu' : 'dwli',
	'sac' : 'dwlg',
	'hes' : 'dwoh',
	'rps' : 'dwoi',
	'baw' : 'dwsg',
	'bay' : 'dwmg'
	}

Biowetterregionen = {
	'shh' : '0',
	'mvp' : '1',
	'nib' : '3',
	'nrw' : '2',
	'bbb' : '4',
	'saa' : '5',
	'thu' : '5',
	'sac' : '5',
	'hes' : '6',
	'rps' : '6',
	'baw' : '8',
	'bay' : '10'
	}

Pollenflugregionen = {
	'shh' : [('11','Inseln und Marschen'),('12','Geest,Schleswig-Holstein und Hamburg')],
	'mvp' : [('20','Mecklenburg-Vorpommern')],
	'nib' : [('31','Westl. Niedersachsen/Bremen'),('32','Östl. Niedersachsen')],
	'nrw' : [('41','Rhein.-Westfäl. Tiefland'),('42','Ostwestfalen'),('43','Mittelgebirge NRW')],
	'bbb' : [('50','Brandenburg und Berlin')],
	'saa' : [('61','Tiefland Sachsen-Anhalt'),('62','Harz')],
	'thu' : [('71','Tiefland Thüringen'),('72','Mittelgebirge Thüringen')],
	'sac' : [('81','Tiefland Sachsen'),('82','Mittelgebirge Sachsen')],
	'hes' : [('91','Nordhessen und hess. Mittelgebirge'),('92','Rhein-Main')],
	'rps' : [('101','Rhein, Pfalz, Nahe und Mosel'),('102','Mittelgebirgsbereich Rheinland-Pfalz'),('103','Saarland')],
	'baw' : [('111','Oberrhein und unteres Neckartal'),('112','Hohenlohe/mittlerer Neckar/Oberschwaben'),('113','Mittelgebirge Baden-Württemberg')],
	'bay' : [('121','Allgäu/Oberbayern/Bay. Wald'),('122','Donauniederungen'),('123','Bayern nördl. der Donau, o. Bayr. Wald, o. Mainfranken'),('124','Mainfranken')]
	}

Pollengruppen = {
	"-1" : "keine Werte",
	"0" : "keine",
	"0-1" : "keine bis gering",
	"1" : "gering",
	"1-2" : "gering bis mittel",
	"2" : "mittel",
	"2-3" : "mittel bis hoch",
	"3" : "hoch"
	}

Pollenimgidx = {
	"-1" : "0",
	"0" : "1",
	"0-1" : "2",
	"1" : "3",
	"1-2" : "4",
	"2" : "5",
	"2-3" : "6",
	"3" : "7"
	}

Pollenimgs = ['pollen_0_heute.png','pollen_0_morgen.png','pollen_1_heute.png','pollen_1_morgen.png','pollen_2_heute.png','pollen_2_morgen.png','pollen_3_heute.png','pollen_3_morgen.png','pollen_4_heute.png','pollen_4_morgen.png','pollen_5_heute.png','pollen_5_morgen.png','pollen_6_heute.png','pollen_6_morgen.png','pollen_7_heute.png','pollen_7_morgen.png']
Bioimgs = ['bio_allg_heute.png','bio_allg_morgen.png','bio_asthma_heute.png','bio_asthma_morgen.png','bio_kreislauf_heute.png','bio_kreislauf_morgen.png','bio_rheuma_heute.png','bio_rheuma_morgen.png']
Wetterimgs = ['aktuell.jpg','heutenacht.jpg','morgenfrueh.jpg','morgenspaet.jpg','uebermorgenfrueh.jpg','uebermorgenspaet.jpg','tag4frueh.jpg','tag4spaet.jpg','trend.jpg','dwd_radar.jpg']
def write_log(svalue):
	if log:
		t = localtime()
		logtime = '%02d:%02d:%02d' % (t.tm_hour, t.tm_min, t.tm_sec)
		VWeather3_log = open('/tmp/VWeather3.log',"a")
		VWeather3_log.write(str(logtime) + " - " + str(svalue) + "\n")
		VWeather3_log.close()

is_installed = False
if os.path.isfile('/usr/lib/enigma2/python/Plugins/Extensions/VWeather3/VWeather3cfg.py'):
	from Plugins.Extensions.VWeather3.oauth1_auth import get_queryoauth
#	from Plugins.Extensions.VWeather3.yauth import make_request
	from Plugins.Extensions.VWeather3.ImageTools import convertIcon, splitRadarImage, convertOnlinePicture
	from Plugins.Extensions.VWeather3.timezones import get_timezone_delta
	is_installed = True
else:
	config.plugins.VWeather3 = ConfigSubsection()
	config.plugins.VWeather3.StartScreen = ConfigSelection(default = "cfg", choices = [
		("cfg", _("Setup")),
		("dwd", "DWD " + _("Warning")),
		("cst", _("Weather"))
	])
	config.plugins.VWeather3.refreshInterval = ConfigInteger(default = 120, limits = (60, 300))
	config.plugins.VWeather3.Log = ConfigYesNo(default = True)
	config.plugins.VWeather3.Provider = ConfigSelection(default = "Darksky", choices = [ "Darksky", "OpenWeatherMap", "Yahoo" ])
	config.plugins.VWeather3.CountryCode = ConfigSelection(default = "de", choices = [
		("bg", _("Bulgarian")),
		("ca", _("Catalan")),
		("cz", _("Czech")),
		("de", _("German")),
		("el", _("Greek")),
		("en", _("English")),
		("es", _("Spanish")),
		("fi", _("Finnish")),
		("fr", _("French")),
		("hr", _("Croatian")),
		("hu", _("Hungarian")),
		("it", _("Italian")),
		("nl", _("Dutch")),
		("pl", _("Polish")),
		("pt", _("Portuguese")),
		("ro", _("Romanian")),
		("ru", _("Russian")),
		("sk", _("Slovak")),
		("sl", _("Slovenian")),
		("tr", _("Turkish"))
	])# Ländercode nach ISO-3166 Alpha-2
	config.plugins.VWeather3.Units = ConfigSelection(default = "metric", choices = [("metric", _("Celsius")),("imperial", _("Fahrenheit")),("", _("Kelvin"))])      # metric = °Celsius ; imperial = Fahrenheit ; default = Kelvin
	config.plugins.VWeather3.numbers = ConfigInteger(default = 1, limits = (0, 2))
	config.plugins.VWeather3.spaces = ConfigYesNo(default = True)
	config.plugins.VWeather3.DateFormat = ConfigSelection(default = "lang", choices = [("lang", _("long")),("kurz", _("short"))])
	config.plugins.VWeather3.DayFormat = ConfigSelection(default = "lang", choices = [("lang", _("long")),("kurz", _("short"))])

	config.plugins.VWeather3.Darksky_apikey = ConfigText(default = "1234567890")
	config.plugins.VWeather3.Darksky_lat = ConfigText(default = "0.0")
	config.plugins.VWeather3.Darksky_lon = ConfigText(default = "0.0")
	config.plugins.VWeather3.Darksky_place = ConfigText(default = " ")
	config.plugins.VWeather3.Darksky_lat1 = ConfigText(default = "0.0")
	config.plugins.VWeather3.Darksky_lon1 = ConfigText(default = "0.0")
	config.plugins.VWeather3.Darksky_place1 = ConfigText(default = " ")
	config.plugins.VWeather3.Darksky_lat2 = ConfigText(default = "0.0")
	config.plugins.VWeather3.Darksky_lon2 = ConfigText(default = "0.0")
	config.plugins.VWeather3.Darksky_place2 = ConfigText(default = " ")
	config.plugins.VWeather3.Darksky_lat3 = ConfigText(default = "0.0")
	config.plugins.VWeather3.Darksky_lon3 = ConfigText(default = "0.0")
	config.plugins.VWeather3.Darksky_place3 = ConfigText(default = " ")
	config.plugins.VWeather3.Darksky_alerts = ConfigYesNo(default = False)

	config.plugins.VWeather3.OpenWeatherMap_apikey = ConfigText(default = "1234567890")
	config.plugins.VWeather3.OpenWeatherMap_geolocation = ConfigSelection(default = "Ort", choices = [("PLZ", _("ZIP code")),("Ort", _("City name"))])
	config.plugins.VWeather3.OpenWeatherMap_zipcode = ConfigText(default = "01234")
	config.plugins.VWeather3.OpenWeatherMap_zipcode1 = ConfigText(default = "01234")
	config.plugins.VWeather3.OpenWeatherMap_zipcode2 = ConfigText(default = "01234")
	config.plugins.VWeather3.OpenWeatherMap_zipcode3 = ConfigText(default = "01234")
	config.plugins.VWeather3.OpenWeatherMap_place = ConfigText(default = "Mein Ort")
	config.plugins.VWeather3.OpenWeatherMap_place1 = ConfigText(default = "Mein Ort")
	config.plugins.VWeather3.OpenWeatherMap_place2 = ConfigText(default = "Mein Ort")
	config.plugins.VWeather3.OpenWeatherMap_place3 = ConfigText(default = "Mein Ort")

	config.plugins.VWeather3.Yahoo_woeid = ConfigText(default = "00000000")
	config.plugins.VWeather3.Yahoo_woeid1 = ConfigText(default = "00000000")
	config.plugins.VWeather3.Yahoo_woeid2 = ConfigText(default = "00000000")
	config.plugins.VWeather3.Yahoo_woeid3 = ConfigText(default = "00000000")

	config.plugins.VWeather3.DWD = ConfigYesNo(default = True)
	config.plugins.VWeather3.DWD_Pollen = ConfigYesNo(default = True)
	config.plugins.VWeather3.DWD_Wetter = ConfigYesNo(default = True)
	config.plugins.VWeather3.DWD_Bio = ConfigYesNo(default = True)
	config.plugins.VWeather3.DWD_AutoShow = ConfigYesNo(default = True)
	config.plugins.VWeather3.DWD_WeatherCellID = ConfigText(default = "106535000")
	config.plugins.VWeather3.DWD_duration = ConfigInteger(default = 60, limits = (0, 300))
	config.plugins.VWeather3.DWD_BL = ConfigSelection(default = "baw", choices = [
		("baw", _("Baden-Württemberg")),
		("bay", _("Bayern")),
		("bbb", _("Berlin, Brandenburg")),
		("hes", _("Hessen")),
		("mvp", _("Mecklenburg-Vorpommern")),
		("nib", _("Niedersachsen, Bremen")),
		("nrw", _("Nordrhein-Westfalen")),
		("rps", _("Rheinland-Pfalz, Saarland")),
		("sac", _("Sachsen")),
		("saa", _("Sachsen-Anhalt")),
		("shh", _("Schleswig-Holstein, Hamburg")),
		("thu", _("Thüringen")),
	])
	config.plugins.VWeather3.DWD_Pollenflugregion = ConfigSelection(default = Pollenflugregionen[config.plugins.VWeather3.DWD_BL.value][0][0], choices = Pollenflugregionen[config.plugins.VWeather3.DWD_BL.value])
	config.plugins.VWeather3.DWD_Level = ConfigInteger(default = 0, limits = (0, 4))
	config.plugins.VWeather3.DWD_ANIMATED_RADAR = ConfigYesNo(default = False)

	config.plugins.VWeather3.UWW_AT = ConfigYesNo(default = False)
	config.plugins.VWeather3.UWW_AT_BL = ConfigSelection(default = "Burgenland", choices = [
		"Burgenland", "Kärnten", "Niederöstereich", "Oberöstereich", "Osttirol", "Salzburg", "Steiermark", "Tirol", "Voralberg", "Wien" ])

	config.plugins.VWeather3.NetworkMode = ConfigSelection(default = "Single", choices = [("Single", _("Single")),("Server", _("Server")),("Client", _("Client"))])
	config.plugins.VWeather3.ServerIP = ConfigIP(default = [192, 168, 0, 0])
	config.plugins.VWeather3.ImageFolder = ConfigSelection(default = "/usr/share/enigma2/VWeather3/", choices = [ "/usr/share/enigma2/VWeather3/", "/media/hdd/VWeather3/", "/media/usb/VWeather3/" ])
	print "Bitte installiere das Plugin-Vweather3. Wetterdienste sind derzeit nicht Verfügbar!"

weather_data = None
wdays_en = [_("Sunday"),_("Monday"),_("Tuesday"),_("Wednesday"),_("Thursday"),_("Friday"),_("Saturday")]
swdays_en = [_("Sun"),_("Mon"),_("Tue"),_("Wed"),_("Thu"),_("Fri"),_("Sat")]

log = config.plugins.VWeather3.Log.value
numbers = '.' + str(config.plugins.VWeather3.numbers.value) + 'f'
isDWD = config.plugins.VWeather3.DWD.value or config.plugins.VWeather3.DWD.value == 'true'
isDWD_Pollen = config.plugins.VWeather3.DWD_Pollen.value or config.plugins.VWeather3.DWD_Pollen.value == 'true'
isDWD_Wetter = config.plugins.VWeather3.DWD_Wetter.value or config.plugins.VWeather3.DWD_Wetter.value == 'true'
isDWD_Bio = config.plugins.VWeather3.DWD_Bio.value or config.plugins.VWeather3.DWD_Bio.value == 'true'
isUWW_AT = config.plugins.VWeather3.UWW_AT.value or config.plugins.VWeather3.UWW_AT.value == 'true'
isOnePlace = config.plugins.VWeather3.Darksky_lat1.value == "0.0" and config.plugins.VWeather3.OpenWeatherMap_zipcode1.value == "01234" and config.plugins.VWeather3.OpenWeatherMap_place1.value == "Mein Ort" and config.plugins.VWeather3.Yahoo_woeid1.value == "00000000"
picturepath = str(config.plugins.VWeather3.ImageFolder.value)
if not os.path.exists(picturepath):
	os.makedirs(picturepath)

global dsplace
dsplace = config.plugins.VWeather3.Darksky_place.value

srv_ip_list = config.plugins.VWeather3.ServerIP.value
if isinstance(srv_ip_list, list):
	srv_ip = str(srv_ip_list[0]) + '.' + str(srv_ip_list[1]) + '.' + str(srv_ip_list[2]) + '.' + str(srv_ip_list[3])
else:
	srv_ip = config.plugins.VWeather3.ServerIP.value

PluginLanguageDomain = "VWeather3"

lang = language.getLanguage()
os.environ["LANGUAGE"] = lang[:2]
gettext.bindtextdomain("enigma2", resolveFilename(SCOPE_LANGUAGE))
gettext.textdomain("enigma2")
gettext.bindtextdomain(PluginLanguageDomain, "%s%s" % (resolveFilename(SCOPE_PLUGINS), "Extensions/" + PluginLanguageDomain + "/locale/"))

def _(txt):
	if is_installed:
		t = gettext.dgettext(PluginLanguageDomain, txt)
		if t == txt:
			t = gettext.gettext(txt)
		return t
	else:
		return str(txt)

###############################################################################################################

class speedyVWeather5(Poll, Converter, object):

	def __init__(self, type):
		Poll.__init__(self)
		Converter.__init__(self, type)
		global weather_data
		if weather_data is None:
			weather_data = WeatherData()
		self.type = type
		self.params = str(type).split(";")
		self.poll_interval = 920000
		self.poll_enabled = True
		self.lastplace = "N/A"
		self.lastupdate = 0
		if not isOnePlace or config.plugins.VWeather3.NetworkMode.value == "Client":
			self.checker = eTimer()
			self.checker.callback.append(self.GetChange)
			self.checker.start(10000, True)


	@cached
	def getText(self):
		WeatherInfo = weather_data.WeatherInfo
		ret = ''
		try:
			for param in self.params:
				if str(param) in WeatherInfo:
					ret = ret + WeatherInfo[param]
				else:
					ret = ret + str(_(param))
				for x in self.downstream_elements:
					if hasattr(x, 'path') and str(param) == 'currentMoonPicon':
						ret = weather_data.moonphase(x.path)[1]
					elif hasattr(x, 'Path') and str(param) == 'currentMoonPicon':
						ret = weather_data.moonphase(x.Path)[1]
			return ret
		except Exception as ex:
			write_log("Fehler in WeatherInfo : " + str(ex))
			return " "

	text = property(getText)

	@cached
	def getBoolean(self):
		WeatherInfo = weather_data.WeatherInfo
		ret = ''
		try:
			for param in self.params:
				if str(param) in WeatherInfo:
					if WeatherInfo[param] == ' ':
						return True
					else:
						return False
		except Exception as ex:
			write_log("Fehler in WeatherInfo getBoolean : " + str(ex))
			return False

	boolean = property(getBoolean)

	def changed(self, what):
		if what[0] == self.CHANGED_POLL:
			Converter.changed(self, what)

	def GetChange(self):
		if not isOnePlace or config.plugins.VWeather3.NetworkMode.value == "Client":
			self.checker.start(5000, True)
			if mktime(localtime()) > (self.lastupdate + 4):
				self.lastupdate = mktime(localtime())
				WeatherInfo = weather_data.WeatherInfo["currentLocation"]
				if str(WeatherInfo) != str(self.lastplace):
					Converter.changed(self,(self.CHANGED_POLL,))
				self.lastplace = WeatherInfo

	def connectDownstream(self, downstream):
		Converter.connectDownstream(self, downstream)


class WeatherData:
	def __init__(self):
		self.WeatherInfo = WeatherInfo = { 
			"DWD_POLLEN_DATETIME" : " ",
			"DWD_POLLEN_REGION" : " ",
			"DWD_POLLEN_TODAY_HASEL_INTENSITY" : "0",
			"DWD_POLLEN_TODAY_ESCHE_INTENSITY" : "0",
			"DWD_POLLEN_TODAY_ERLE_INTENSITY" : "0",
			"DWD_POLLEN_TODAY_BIRKE_INTENSITY" : "0",
			"DWD_POLLEN_TODAY_GRAESER_INTENSITY" : "0",
			"DWD_POLLEN_TODAY_AMBROSIA_INTENSITY" : "0",
			"DWD_POLLEN_TODAY_ROGGEN_INTENSITY" : "0",
			"DWD_POLLEN_TODAY_BEIFUSS_INTENSITY" : "0",
			"DWD_POLLEN_TODAY_HASEL_LOAD" : "0",
			"DWD_POLLEN_TODAY_ESCHE_LOAD" : "0",
			"DWD_POLLEN_TODAY_ERLE_LOAD" : "0",
			"DWD_POLLEN_TODAY_BIRKE_LOAD" : "0",
			"DWD_POLLEN_TODAY_GRAESER_LOAD" : "0",
			"DWD_POLLEN_TODAY_AMBROSIA_LOAD" : "0",
			"DWD_POLLEN_TODAY_ROGGEN_LOAD" : "0",
			"DWD_POLLEN_TODAY_BEIFUSS_LOAD" : "0",
			"DWD_POLLEN_TOMORROW_HASEL_INTENSITY" : "0",
			"DWD_POLLEN_TOMORROW_ESCHE_INTENSITY" : "0",
			"DWD_POLLEN_TOMORROW_ERLE_INTENSITY" : "0",
			"DWD_POLLEN_TOMORROW_BIRKE_INTENSITY" : "0",
			"DWD_POLLEN_TOMORROW_GRAESER_INTENSITY" : "0",
			"DWD_POLLEN_TOMORROW_AMBROSIA_INTENSITY" : "0",
			"DWD_POLLEN_TOMORROW_ROGGEN_INTENSITY" : "0",
			"DWD_POLLEN_TOMORROW_BEIFUSS_INTENSITY" : "0",
			"DWD_POLLEN_TOMORROW_HASEL_LOAD" : "0",
			"DWD_POLLEN_TOMORROW_ESCHE_LOAD" : "0",
			"DWD_POLLEN_TOMORROW_ERLE_LOAD" : "0",
			"DWD_POLLEN_TOMORROW_BIRKE_LOAD" : "0",
			"DWD_POLLEN_TOMORROW_GRAESER_LOAD" : "0",
			"DWD_POLLEN_TOMORROW_AMBROSIA_LOAD" : "0",
			"DWD_POLLEN_TOMORROW_ROGGEN_LOAD" : "0",
			"DWD_POLLEN_TOMORROW_BEIFUSS_LOAD" : "0",
			"DWD_ALERT_HEAD": " ",
			"DWD_ALERT_TEXT": " ",
			"DWD_ALERT_TEXT_LONG": " ",
			"DWD_ALERT_EVENT": " ",
			"DWD_ALERT_INSTRUCTION": " ",
			"DWD_ALERT_START": " ",
			"DWD_ALERT_END": " ",
			"DWD_REGION": " ",
			"DWD_DATETIME": " ",
			"DWD_WARNLEVEL": "0",
			"DWD_FORECAST_10DAYS" : " ",
			"DWD_ALERT_LIST" : [],
			"DWD_FORECAST_LIST" : [],
			"DWD_BIO_LIST" : [],
			"DWD_POLLEN_LIST" : [],
			"W-Info": " ",
			"provider": "N/A",
			"alerts": "N/A",
			"currentLocation": "N/A",
			"currentCountry": "N/A",
			"currentRegion": "N/A",
			"windChill": "N/A",
			"windDirectionShort": "N/A",
			"windDirectionLong": "N/A",
			"windSpeed": "N/A",
			"atmoHumidity": "N/A",
			"atmoPressure": "N/A",
			"atmoRising": "N/A",
			"atmoVisibility": "N/A",
			"astroSunrise": "N/A",
			"astroSunset": "N/A",
			"geoData": "N/A",
			"geoLat": "N/A",
			"geoLong": "N/A",
			"downloadDate": "N/A",
			"downloadTime": "N/A",
			"currentWeatherCode": "(",
			"currentWeatherText": "N/A",
			"currentWeatherTemp": "0",
			"currentWeatherPicon": "3200",
			"currentMoonPicon": "3200",
			"currentMoonPhase": "N/A",
			"forecastTodayCode": "(",
			"forecastTodayDay": "N/A",
			"forecastTodayDate": "N/A",
			"forecastTodayTempMin": "0",
			"forecastTodayTempMax": "0",
			"forecastTodayText": "N/A",
			"forecastTodayPicon": "3200",
			"forecastTomorrowCode": "(",
			"forecastTomorrowDay": "N/A",
			"forecastTomorrowDate": "N/A",
			"forecastTomorrowTempMin": "0",
			"forecastTomorrowTempMax": "0",
			"forecastTomorrowText": "N/A",
			"forecastTomorrowPicon": "3200",
			"forecastTomorrow1Code": "(",
			"forecastTomorrow1Day": "N/A",
			"forecastTomorrow1Date": "N/A",
			"forecastTomorrow1TempMin": "0",
			"forecastTomorrow1TempMax": "0",
			"forecastTomorrow1Text": "N/A",
			"forecastTomorrow1Picon": "3200",
			"forecastTomorrow2Code": "(",
			"forecastTomorrow2Day": "N/A",
			"forecastTomorrow2Date": "N/A",
			"forecastTomorrow2TempMin": "0",
			"forecastTomorrow2TempMax": "0",
			"forecastTomorrow2Text": "N/A",
			"forecastTomorrow2Picon": "3200",
			"forecastTomorrow3Code": "(",
			"forecastTomorrow3Day": "N/A",
			"forecastTomorrow3Date": "N/A",
			"forecastTomorrow3TempMin": "0",
			"forecastTomorrow3TempMax": "0",
			"forecastTomorrow3Text": "N/A",
			"forecastTomorrow3Picon": "3200",
			"forecastTomorrow4Code": "(",
			"forecastTomorrow4Day": "N/A",
			"forecastTomorrow4Date": "N/A",
			"forecastTomorrow4TempMin": "0",
			"forecastTomorrow4TempMax": "0",
			"forecastTomorrow4Text": "N/A",
			"forecastTomorrow4Picon": "3200",
			"forecastTomorrow5Code": " ",
			"forecastTomorrow5Day": " ",
			"forecastTomorrow5Date": " ",
			"forecastTomorrow5TempMin": " ",
			"forecastTomorrow5TempMax": " ",
			"forecastTomorrow5Text": " ",
			"forecastTomorrow5Picon": " ",
			"forecastTomorrow6Code": " ",
			"forecastTomorrow6Day": " ",
			"forecastTomorrow6Date": " ",
			"forecastTomorrow6TempMin": " ",
			"forecastTomorrow6TempMax": " ",
			"forecastTomorrow6Text": " ",
			"forecastTomorrow6Picon": " ",
			"forecastTomorrow7Code": " ",
			"forecastTomorrow7Day": " ",
			"forecastTomorrow7Date": " ",
			"forecastTomorrow7TempMin": " ",
			"forecastTomorrow7TempMax": " ",
			"forecastTomorrow7Text": " ",
			"forecastTomorrow7Picon": " ",
			"forecastTomorrow8Code": " ",
			"forecastTomorrow8Day": " ",
			"forecastTomorrow8Date": " ",
			"forecastTomorrow8TempMin": " ",
			"forecastTomorrow8TempMax": " ",
			"forecastTomorrow8Text": " ",
			"forecastTomorrow8Picon": " ",
			"t_windChill": _("feels like"),
			"t_windDirection": _("wind direction"),
			"t_windSpeed": _("wind speed"),
			"t_atmoHumidity": _("humidity"),
			"t_atmoPressure": _("pressure"),
			"t_atmoVisibility": _("visibility"),
			"t_astroSunrise": _("sunrise"),
			"t_astroSunset": _("sunset"),
			"t_geoData": _("geo coordinates"),
			"t_downloadDate": _("update date"),
			"t_downloadTime": _("update time")
		}

		self.ChangeCheck = ""

		self.useImageTools = True
		self.ImageBackgroundColor = '#00000000'
		self.ImageRadius = 100
		self.ImageRadiusTransparency = 0
		self.ImageTextColor = '#00dddddd'
		self.defaults = {
		"useimagetools": "True",
		"imagebackgroundcolor": "#e0000000",
		"imageradius": "10",
		"imageradiustransparency": "255",
		"imagetextcolor": "#00dddddd",
		}
		if os.path.isfile(pluginpath + 'ImageTools.cfg'):
			Config = ConfigParser.ConfigParser(self.defaults)
			Config.read(os.path.join(pluginpath, 'ImageTools.cfg'))
			self.useImageTools = Config.getboolean('ImageTools', 'useImageTools')
			self.ImageBackgroundColor = Config.get('ImageTools', 'ImageBackgroundColor')
			self.ImageRadius = Config.getint('ImageTools', 'ImageRadius')
			self.ImageRadiusTransparency = Config.getint('ImageTools', 'ImageRadiusTransparency')
			self.ImageTextColor = Config.get('ImageTools', 'ImageTextColor')
			write_log('Parameter für ImageTools geladen.')

		if config.plugins.VWeather3.NetworkMode.value != "Client":
			d = threading.Thread(name='initServerMode', target=self.initServerMode)
			d.setDaemon(True)
			d.start()
			if config.plugins.VWeather3.refreshInterval.value > 0:
				self.timer = eTimer()
				self.timer.callback.append(self.GetWeather)
				self.GetWeather()
			if isDWD or isUWW_AT:
				self.DWDtimer = eTimer()
				self.DWDtimer.callback.append(self.GetDWDWeather)
				self.GetDWDWeather()
		else:
			write_log("starte Client-Mode ...")
			self.timer = eTimer()
			self.timer.callback.append(self.checkChange)
			self.checkChange()
#			self.GetServerWeather()

	def initServerMode(self):
		try:
			f = os.popen('ifconfig eth0 | grep "inet\ addr" | cut -d: -f2 | cut -d" " -f1')
			my_ip=f.read()
			HOST = str(my_ip).replace("\n","")
			write_log('my IP is ' + str(HOST))
			s = socket(AF_INET, SOCK_STREAM)
			s.bind((HOST, PORT))
			write_log("Wetter-Server gestartet auf " + str(HOST) + ' mit Port ' + str(PORT))
			while 1:
				s.listen(10)
				conn, addr = s.accept()
				data = conn.recv(BUFSIZE)
				write_log('Connected by ' + str(addr) + ' - ' +  str(data))
				if data == "":
					conn.sendall("keine Daten")
				elif data == ".stop":
					conn.sendall("Server beendet") 
					break
				elif data == "checkChange":
					conn.sendall(str(weather_data.WeatherInfo["currentLocation"])+str(weather_data.WeatherInfo["DWD_ALERT_END"])) 
				elif data == "getconfig":
					if config.plugins.VWeather3.Provider.value == "Yahoo":
						cnf = ['Yahoo',config.plugins.VWeather3.Yahoo_woeid.value,config.plugins.VWeather3.Yahoo_woeid1.value,config.plugins.VWeather3.Yahoo_woeid2.value,config.plugins.VWeather3.Yahoo_woeid3.value]
					elif config.plugins.VWeather3.Provider.value == "OpenWeatherMap":
						if config.plugins.VWeather3.OpenWeatherMap_geolocation.value == "PLZ":
							cnf = ['OpenWeatherMap','PLZ',config.plugins.VWeather3.OpenWeatherMap_zipcode.value,config.plugins.VWeather3.OpenWeatherMap_zipcode1.value,config.plugins.VWeather3.OpenWeatherMap_zipcode2.value,config.plugins.VWeather3.OpenWeatherMap_zipcode3.value]
						else:
							cnf = ['OpenWeatherMap','Place',config.plugins.VWeather3.OpenWeatherMap_place.value,config.plugins.VWeather3.OpenWeatherMap_place1.value,config.plugins.VWeather3.OpenWeatherMap_place2.value,config.plugins.VWeather3.OpenWeatherMap_place3.value]
					elif config.plugins.VWeather3.Provider.value == "Darksky":
						cnf = ['Darksky',(config.plugins.VWeather3.Darksky_lat.value,config.plugins.VWeather3.Darksky_lon.value),(config.plugins.VWeather3.Darksky_lat1.value,config.plugins.VWeather3.Darksky_lon1.value),(config.plugins.VWeather3.Darksky_lat2.value,config.plugins.VWeather3.Darksky_lon2.value),(config.plugins.VWeather3.Darksky_lat3.value,config.plugins.VWeather3.Darksky_lon3.value)]
					conn.sendall(str(cnf)) 
				elif data == "getWeather":
					fh, abs_path = mkstemp()
					with fdopen(fh,'w') as f:
						f.write(json.dumps(weather_data.WeatherInfo))
					with open(abs_path,'r') as f:
						while True:
							l = f.read(BUFSIZE)
							write_log(str(l.encode('utf8')))
							while (l):
								sleep(0.02)
								conn.send(l.encode('utf8'))
								l = f.read(BUFSIZE)
								write_log(str(l))
							if not l:
								f.close()
								conn.send('done')
								break
					os.remove(abs_path)
#					conn.sendall(str(weather_data.WeatherInfo)) 
				elif data == "getRadar":
					filename = os.path.join(picturepath, 'dwd_radar.jpg')
					f = open(filename,'rb')
					while True:
						l = f.read(BUFSIZE)
						while (l):
							sleep(0.02)
							conn.send(l)
							l = f.read(BUFSIZE)
						if not l:
							f.close()
							conn.send('done')
							break
				elif data == "getWarning":
					filename = os.path.join(picturepath, 'dwd_alert.png')
					f = open(filename,'rb')
					while True:
						l = f.read(BUFSIZE)
						while (l):
							sleep(0.02)
							conn.send(l)
							l = f.read(BUFSIZE)
						if not l:
							f.close()
							conn.send('done')
							break
				elif 'getfav=' in data:
					write_log('wechsle Favoriten')
					# Berechnung Mondphase
					cphase = self.moonphase()
					self.WeatherInfo["currentMoonPhase"]= cphase[0]
					self.WeatherInfo["currentMoonPicon"] = cphase[1]
					units = config.plugins.VWeather3.Units.value
					countrycode = config.plugins.VWeather3.CountryCode.value
					if config.plugins.VWeather3.Provider.value == "Yahoo":
						if units == "metric":
							yunits = "u=c"
						elif units == "imperial":
							yunits = "u=f"
						else:
							yunits = "u=f"
#						url, oauth = make_request(str(data).replace('getfav=',''),yunits)
#						r = requests.get(url=url, headers={'Authorization' : oauth}, timeout=20)
						geolocation = "woeid=" + str(data).replace('getfav=','')
						query_url = 'https://weather-ydn-yql.media.yahoo.com/forecastrss?' + geolocation + '&format=json&' + yunits
						queryoauth = get_queryoauth()
						write_log("Yahoo URL : " + str(query_url))
						r = requests.get(url=query_url, auth=queryoauth, timeout=20)
						if r.status_code == 200:
								self.GotYahooWeatherData(r.content)
						else:
							write_log("Statuscode : " + str(r.status_code) + " : " + str(r.text))
					elif config.plugins.VWeather3.Provider.value == "OpenWeatherMap":
						apikey = config.plugins.VWeather3.OpenWeatherMap_apikey.value
						zipcode = config.plugins.VWeather3.OpenWeatherMap_zipcode.value
						if config.plugins.VWeather3.OpenWeatherMap_geolocation.value == "PLZ":
							geolocation = "zip=" + str(data).replace('getfav=','')
						else:
							geolocation = "q=" + str(data).replace('getfav=','')
						url = "http://api.openweathermap.org/data/2.5/forecast?" + geolocation + "&APPID=" + apikey + "&units=" + units + "&lang=" + countrycode
						write_log("OWM-URL : " + str(url))
						getPage(url,method = "GET", timeout=20).addCallback(self.GotOpenWeatherMapWeatherData).addErrback(self.downloadError)
						url = "http://api.openweathermap.org/data/2.5/weather?" + geolocation + "&APPID=" + apikey + "&units=" + units + "&lang=" + countrycode
						write_log("COWMURL : " + str(url))
						getPage(url,method = "GET", timeout=20).addCallback(self.GotCurrentOpenWeatherMapWeatherData).addErrback(self.downloadError)
					elif config.plugins.VWeather3.Provider.value == "Darksky":
						if units == "metric":
							dsunits = "si"
						elif units == "imperial":
							dsunits = "us"
						else:
							dsunits = "auto"
						apikey = config.plugins.VWeather3.Darksky_apikey.value
						latlon = str(data).replace('getfav=','').split(',')
						lat = latlon[0]
						lon = latlon[1]
						global dsplace
						dsplace = latlon[2]
						url = "https://api.darksky.net/forecast/" + apikey + "/" + lat + "," + lon + "?exclude=hourly,minutely,flags&lang=" + countrycode + "&units=" + dsunits
						write_log("DARKSKY-URL : " + str(url))
						getPage(url, timeout=20).addCallback(self.GotDarkskyWeatherData).addErrback(self.downloadError)
				else:
					filename = os.path.join(picturepath, str(data))
					f = open(filename,'rb')
					while True:
						l = f.read(BUFSIZE)
						while (l):
							sleep(0.02)
							conn.send(l)
							l = f.read(BUFSIZE)
						if not l:
							f.close()
							conn.send('done')
							break
				conn.close()
				del conn
				write_log('connection closed')
			s.close()
		except Exception as ex:
			write_log("Fehler in initServerMode : " + str(ex))
			del s
#			self.initServerMode()

	def checkChange(self):
		self.timer.start(10000, True)
		pingcheck = os.system("ping -c 2 -W 2 -w 4 " + str(srv_ip))
		if pingcheck == 0:
			try:
				s = socket(AF_INET, SOCK_STREAM)
				s.connect((str(srv_ip), PORT))
				s.settimeout(10.0)
				s.sendall("checkChange")
				data = s.recv(BUFSIZE)
				if self.ChangeCheck != str(data):
					self.GetServerWeather()
				self.ChangeCheck = str(data)
				s.close()
				del s
			except Exception as ex:
				write_log("Fehler in checkChange : " + str(ex))

	def GetServerWeather(self):
		if is_installed:
			pingcheck = os.system("ping -c 2 -W 2 -w 4 " + str(srv_ip))
			if pingcheck == 0:
				try:
					if os.path.isfile("/tmp/VWeather3.log"):
						os.remove("/tmp/VWeather3.log")
					write_log('Verbindungsaufbau zu ' + str(srv_ip))
					s = socket(AF_INET, SOCK_STREAM)
					s.connect((str(srv_ip), PORT))
					s.settimeout(10.0)
					s.sendall("getWeather")
					data = s.recv(BUFSIZE)
					wdict = data
					estop = 0
					while str(data) != 'done':
						data = s.recv(BUFSIZE)
						wdict = wdict + data
						estop += 1
						if 'done' in str(data) or estop > 10:
							break
					wdict2js = str(wdict).replace('done','').replace('\u00b0','°').replace('\\u00e4','ä').replace('\u00c4','Ä').replace('\u00f6','ö').replace('\u00d6','Ö').replace('\u00fc','ü').replace('\u00dc','Ü').decode('utf8')
					self.WeatherInfo = eval(wdict2js)
					write_log(str(self.WeatherInfo))
					s.close()
					del s
					write_log('connection closed')
					if isDWD:
						sleep(0.1)
						if self.WeatherInfo['DWD_ALERT_HEAD'] == " ":
							self.GetServerRadar()
						else:
							self.GetServerWarning()
				except Exception as ex:
					write_log("Fehler in GetServerWeather : " + str(ex))
			else:
				write_log("Server nicht erreichbar " + str(srv_ip))
		else:
			write_log("Konnte keine Installation von VWeather3 finden.")

	def GetServerRadar(self):
		try:
			write_log('Verbindungsaufbau zu ' + str(srv_ip))
			s = socket(AF_INET, SOCK_STREAM)
			s.connect((str(srv_ip), PORT))
			s.settimeout(10.0)
			s.sendall("getRadar")
			rcvb = 0
			estop = 0
			with open(os.path.join(picturepath, 'dwd_radar.jpg'), 'wb') as f:
				data = s.recv(BUFSIZE)
				write_log("Empfange Radarbild")
				while str(data) != 'done':
					datatowrite = (data).replace('done','')
					rcvb += len(datatowrite)
					f.write(datatowrite)
					data = s.recv(BUFSIZE)
					estop += 1
					if estop > 400:
						break
				write_log('Radarbild mit ' + format(float(rcvb/1024), '.1f') + ' kB abgerufen')
			s.close()
			del s
			write_log('connection closed')
			self.GetServerImgs()
		except Exception as ex:
			write_log("Fehler in GetServerRadar : " + str(ex))

	def GetServerWarning(self):
		try:
			write_log('Verbindungsaufbau zu ' + str(srv_ip))
			s = socket(AF_INET, SOCK_STREAM)
			s.connect((str(srv_ip), PORT))
			s.settimeout(10.0)
			s.sendall("getWarning")
			rcvb = 0
			estop = 0
			with open(os.path.join(picturepath, 'dwd_alert.png'), 'wb') as f:
				data = s.recv(BUFSIZE)
				write_log("Empfange Warnbild")
				while str(data) != 'done':
					datatowrite = (data).replace('done','')
					rcvb += len(datatowrite)
					f.write(datatowrite)
					data = s.recv(BUFSIZE)
					estop += 1
					if estop > 400:
						break
				write_log('Warnbild mit ' + format(float(rcvb/1024), '.1f') + ' kB abgerufen')
			s.close()
			del s
			write_log('connection closed')
			self.GetServerImgs()
		except Exception as ex:
			write_log("Fehler in GetServerWarning : " + str(ex))

	def GetServerImgs(self):
		try:
			sleep(0.1)
			if isDWD_Pollen:
				for img in Pollenimgs:
					if ((time.time() - os.stat(os.path.join(picturepath, str(img))[stat.ST_MTIME]) / 60)) > 720:
						write_log('Verbindungsaufbau zu ' + str(srv_ip))
						s = socket(AF_INET, SOCK_STREAM)
						s.connect((str(srv_ip), PORT))
						s.settimeout(10.0)
						s.sendall(str(img))
						rcvb = 0
						estop = 0
						with open(os.path.join(picturepath, str(img)), 'wb') as f:
							data = s.recv(BUFSIZE)
							write_log("Empfange " + str(img))
							while str(data) != 'done':
								datatowrite = (data).replace('done','')
								rcvb += len(datatowrite)
								f.write(datatowrite)
								data = s.recv(BUFSIZE)
								estop += 1
								if estop > 400:
									break
							write_log(str(img) + ' mit ' + format(float(rcvb/1024), '.1f') + ' kB abgerufen')
						s.close()
						del s
						write_log('connection closed')
			if isDWD_Bio:
				for img in Bioimgs:
					if ((time.time() - os.stat(os.path.join(picturepath, str(img))[stat.ST_MTIME]) / 60)) > 720:
						write_log('Verbindungsaufbau zu ' + str(srv_ip))
						s = socket(AF_INET, SOCK_STREAM)
						s.connect((str(srv_ip), PORT))
						s.settimeout(10.0)
						s.sendall(str(img))
						rcvb = 0
						estop = 0
						with open(os.path.join(picturepath, str(img)), 'wb') as f:
							data = s.recv(BUFSIZE)
							write_log("Empfange " + str(img))
							while str(data) != 'done':
								datatowrite = (data).replace('done','')
								rcvb += len(datatowrite)
								f.write(datatowrite)
								data = s.recv(BUFSIZE)
								estop += 1
								if estop > 400:
									break
							write_log(str(img) + ' mit ' + format(float(rcvb/1024), '.1f') + ' kB abgerufen')
						s.close()
						del s
						write_log('connection closed')
			if isDWD_Wetter:
				for img in Wetterimgs:
					if ((time.time() - os.stat(os.path.join(picturepath, str(img))[stat.ST_MTIME]) / 60)) > 300:
						write_log('Verbindungsaufbau zu ' + str(srv_ip))
						s = socket(AF_INET, SOCK_STREAM)
						s.connect((str(srv_ip), PORT))
						s.settimeout(10.0)
						s.sendall(str(img))
						rcvb = 0
						estop = 0
						with open(os.path.join(picturepath, str(img)), 'wb') as f:
							data = s.recv(BUFSIZE)
							write_log("Empfange " + str(img))
							while str(data) != 'done':
								datatowrite = (data).replace('done','')
								rcvb += len(datatowrite)
								f.write(datatowrite)
								data = s.recv(BUFSIZE)
								estop += 1
								if estop > 400:
									break
							write_log(str(img) + ' mit ' + format(float(rcvb/1024), '.1f') + ' kB abgerufen')
						s.close()
						del s
						write_log('connection closed')
		except Exception as ex:
			write_log("Fehler in GetServerWarning : " + str(ex))

	def downloadError(self, error = None):
		self.WeatherInfo["W-Info"] = "Error : " + str(error)
		write_log("Error : " + str(error))

	def GetWeather(self):
		if int(config.plugins.VWeather3.refreshInterval.value) < 60 and int(config.plugins.VWeather3.refreshInterval.value) > 0:
			timeout = 3600000
		elif int(config.plugins.VWeather3.refreshInterval.value) == 0:
			timeout = 0
		else:
			timeout = config.plugins.VWeather3.refreshInterval.value * 1000 * 60
		if timeout > 0 and is_installed:
			try:
				if os.path.isfile("/tmp/VWeather3.log"):
					os.remove("/tmp/VWeather3.log")
				# Berechnung Mondphase
				cmoonphase = self.moonphase()
				self.WeatherInfo["currentMoonPhase"]= cmoonphase[0]
				self.WeatherInfo["currentMoonPicon"] = cmoonphase[1]
				self.timer.start(timeout, True)
				pingcheck = os.system("ping -c 2 -W 2 -w 4 8.8.8.8")
				if pingcheck == 0:
					countrycode = config.plugins.VWeather3.CountryCode.value
					units = config.plugins.VWeather3.Units.value
					if config.plugins.VWeather3.Provider.value == "Darksky":
						if units == "metric":
							dsunits = "si"
						elif units == "imperial":
							dsunits = "us"
						else:
							dsunits = "auto"
						apikey = config.plugins.VWeather3.Darksky_apikey.value
						lat = config.plugins.VWeather3.Darksky_lat.value
						lon = config.plugins.VWeather3.Darksky_lon.value
						url = "https://api.darksky.net/forecast/" + apikey + "/" + lat + "," + lon + "?exclude=hourly,minutely,flags&lang=" + countrycode + "&units=" + dsunits
						write_log("DARKSKY-URL : " + str(url))
						getPage(url, timeout=20).addCallback(self.GotDarkskyWeatherData).addErrback(self.downloadError)
					elif config.plugins.VWeather3.Provider.value == "OpenWeatherMap":
						apikey = config.plugins.VWeather3.OpenWeatherMap_apikey.value
						zipcode = config.plugins.VWeather3.OpenWeatherMap_zipcode.value
						if config.plugins.VWeather3.OpenWeatherMap_geolocation.value == "PLZ":
							geolocation = "zip=" + config.plugins.VWeather3.OpenWeatherMap_zipcode.value
						else:
							geolocation = "q=" + config.plugins.VWeather3.OpenWeatherMap_place.value
		#					geolocation = "q=" + config.plugins.VWeather3.OpenWeatherMap_place.value + "," + countrycode
						url = "http://api.openweathermap.org/data/2.5/forecast?" + geolocation + "&APPID=" + apikey + "&units=" + units + "&lang=" + countrycode
						write_log("OWM-URL : " + str(url))
						getPage(url,method = "GET", timeout=20).addCallback(self.GotOpenWeatherMapWeatherData).addErrback(self.downloadError)
						url = "http://api.openweathermap.org/data/2.5/weather?" + geolocation + "&APPID=" + apikey + "&units=" + units + "&lang=" + countrycode
						write_log("COWMURL : " + str(url))
						getPage(url,method = "GET", timeout=20).addCallback(self.GotCurrentOpenWeatherMapWeatherData).addErrback(self.downloadError)
					elif config.plugins.VWeather3.Provider.value == "Yahoo":
						if units == "metric":
							yunits = "u=c"
						elif units == "imperial":
							yunits = "u=f"
						else:
							yunits = "u=f"
#						url, oauth = make_request(str(config.plugins.VWeather3.Yahoo_woeid.value),yunits)
#						r = requests.get(url=url, headers={'Authorization' : oauth}, timeout=20)
						geolocation = "woeid=" + config.plugins.VWeather3.Yahoo_woeid.value
						query_url = 'https://weather-ydn-yql.media.yahoo.com/forecastrss?' + geolocation + '&format=json&' + yunits
						queryoauth = get_queryoauth()
						write_log("Yahoo URL : " + str(query_url))
						r = requests.get(url=query_url, auth=queryoauth, timeout=20)
						if r.status_code == 200:
								self.GotYahooWeatherData(r.content)
						else:
							write_log("Statuscode : " + str(r.status_code) + " : " + str(r.text))
					if isDWD:
						if os.path.isfile(pluginpath + 'ImageTools.cfg'):
							Config = ConfigParser.ConfigParser(self.defaults)
							Config.read(os.path.join(pluginpath, 'ImageTools.cfg'))
							self.useImageTools = Config.getboolean('ImageTools', 'useimagetools')
							self.ImageBackgroundColor = Config.get('ImageTools', 'imagebackgroundcolor')
							self.ImageRadius = Config.getint('ImageTools', 'imageradius')
							self.ImageRadiusTransparency = Config.getint('ImageTools', 'imageradiustransparency')
							self.ImageTextColor = Config.get('ImageTools', 'imagetextcolor')
						self.conimgs = threading.Thread(name='startConverting', target=self.conImages)
						self.conimgs.setDaemon(True)
						self.conimgs.start()

						if isDWD_Wetter:
							url = 'https://www.dwd.de/DWD/wetter/wv_allg/deutschland/text/vhdl13_' + Wetterregionen[config.plugins.VWeather3.DWD_BL.value]  + '.html'
							write_log("DWD Vorhersage URL : " + str(url))
							getPage(url,method = "GET", timeout=20).addCallback(self.GotDWDForecastData).addErrback(self.downloadError)

	#						url = 'https://www.dwd.de/DE/wetter/vorhersage_aktuell/10-tage/10tage_node.html'
	#						write_log("DWD 10 Tage URL : " + str(url))
	#						getPage(url,method = "GET", timeout=20).addCallback(self.GotDWD10DaysData).addErrback(self.downloadError)

						t = localtime()
						if isDWD_Pollen:
							if (t.tm_hour > 10 and t.tm_hour < 13) or (t.tm_hour > 0 and t.tm_hour < 2) or self.WeatherInfo["DWD_POLLEN_DATETIME"] == " ":
								url = "https://opendata.dwd.de/climate_environment/health/alerts/s31fg.json"
								write_log("DWD-Pollen-URL : " + str(url))
								getPage(url,method = "GET", timeout=20).addCallback(self.GotDWDPollenData).addErrback(self.downloadError)

						if isDWD_Bio:
							if (t.tm_hour > 10 and t.tm_hour < 13) or (t.tm_hour > 0 and t.tm_hour < 2) or not self.WeatherInfo["DWD_BIO_LIST"]:
								url = "https://opendata.dwd.de/climate_environment/health/alerts/biowetter.json"
								write_log("DWD-Biowetter-URL : " + str(url))
								getPage(url,method = "GET", timeout=20).addCallback(self.GotDWDBioData).addErrback(self.downloadError)
				else:
					write_log("kein Internet!")
			except Exception as ex:
				write_log("Fehler in GetWeather : " + str(ex))
		else:
			write_log("Konnte keine Installation von VWeather3 finden.")

	def GetDWDWeather(self):
		timeout = 960000
		if is_installed:
			try:
				self.DWDtimer.start(timeout, True)
				pingcheck = os.system("ping -c 2 -W 2 -w 4 8.8.8.8")
				if pingcheck == 0:
					if isDWD:
						url = "https://www.dwd.de/DWD/warnungen/warnapp/json/warnings.json"
						write_log("DWD-URL : " + str(url))
						getPage(url, timeout=20).addCallback(self.GotDWDWeatherData).addErrback(self.downloadError)
					elif isUWW_AT:
						url = 'http://meteoalarm.eu/documents/rss/at.rss'
						write_log("Meteoalarm AT : " + str(url))
						getPage(url,method = "GET", timeout=20).addCallback(self.GotMeteoalarmAT).addErrback(self.downloadError)
				else:
					write_log("kein Internet!")
			except Exception as ex:
				write_log("Fehler in GetDWDWeather : " + str(ex))
		else:
			write_log("Konnte keine Installation von VWeather3 finden.")

	#OpenWeatherMap
	def GotOpenWeatherMapWeatherData(self, data = None):
		write_log("###################################### OpenWeatherMap Data ################################################")
		write_log("Data : " + str(data))
		if data is not None:
			try:
				parsed_json = json.loads(data)
				for k, v in parsed_json.items():
					write_log(str(k) + ":" + str(v))
				write_log(str(len(parsed_json["list"])))

				write_log("###################################### OpenWeatherMap ################################################")
				for k, v in parsed_json["list"][0].items():
					write_log(str(k) + ":" + str(v))

				self.WeatherInfo["atmoPressure"] = format(float(parsed_json['list'][0]['main']['grnd_level']), '.0f') + " mBar"

				self.WeatherInfo["forecastTomorrow4Date"] = " "
				self.WeatherInfo["forecastTomorrow4Day"] = " "
				self.WeatherInfo["forecastTomorrow4Code"] = " "
				self.WeatherInfo["forecastTomorrow4Picon"] = " "
				self.WeatherInfo["forecastTomorrow4TempMax"] = " "
				self.WeatherInfo["forecastTomorrow4TempMin"] = " "
				self.WeatherInfo["forecastTomorrow4Text"] = " "

				# nächsten Tag finden
				i = 0
				next_day = 0
				sNOW = datetime.datetime.now().strftime('%d.%m.%Y')		# get the current date and compare timestamps to that.
				while i < 8:
					if str(self.convertCurrentDateLong(parsed_json["list"][i]['dt'])) != sNOW:
						next_day = i
						write_log("morgen startet bei Index " + str(next_day))
						break
					i += 1
				self.WeatherInfo["forecastTodayDay"] = self.convertCurrentDay(parsed_json['list'][0]['dt'])
				self.WeatherInfo["forecastTodayDate"] = self.convertCurrentDate(parsed_json['list'][0]['dt'])
				i = 0
				icons = []
				description = []
				tempmin = 100
				tempmax = -100
				if int(next_day) > 0:
					while i < int(next_day):
						icons.append(parsed_json["list"][i]['weather'][0]['icon'])
						description.append(parsed_json["list"][i]['weather'][0]['description'])
						if float(parsed_json["list"][i]['main']['temp']) < tempmin:
							tempmin = float(parsed_json["list"][i]['main']['temp'])
						if float(parsed_json["list"][i]['main']['temp']) > tempmax:
							tempmax = float(parsed_json["list"][i]['main']['temp'])
						i += 1
					self.WeatherInfo["forecastTodayCode"] = str(self.ConvertIconCode(icons[int(len(icons)/2)]))
					self.WeatherInfo["forecastTodayPicon"] = str(self.convertOWMIconName(icons[int(len(icons)/2)]))
					self.WeatherInfo["forecastTodayTempMax"] = format(tempmax, str(numbers)) + self.ConvertTemp(config.plugins.VWeather3.Units.value)
					self.WeatherInfo["forecastTodayTempMin"] = format(tempmin, str(numbers)) + self.ConvertTemp(config.plugins.VWeather3.Units.value)
					self.WeatherInfo["forecastTodayText"] = str(description[int(len(description)/2)])
				else:
					while i < 8:
						icons.append(parsed_json["list"][i]['weather'][0]['icon'])
						description.append(parsed_json["list"][i]['weather'][0]['description'])
						if float(parsed_json["list"][i]['main']['temp']) < tempmin:
							tempmin = float(parsed_json["list"][i]['main']['temp'])
						if float(parsed_json["list"][i]['main']['temp']) > tempmax:
							tempmax = float(parsed_json["list"][i]['main']['temp'])
						i += 1
					self.WeatherInfo["forecastTodayCode"] = str(self.ConvertIconCode(icons[int(len(icons)/2)]))
					self.WeatherInfo["forecastTodayPicon"] = str(self.convertOWMIconName(icons[int(len(icons)/2)]))
					self.WeatherInfo["forecastTodayTempMax"] = format(tempmax, str(numbers)) + self.ConvertTemp(config.plugins.VWeather3.Units.value)
					self.WeatherInfo["forecastTodayTempMin"] = format(tempmin, str(numbers)) + self.ConvertTemp(config.plugins.VWeather3.Units.value)
					self.WeatherInfo["forecastTodayText"] = str(description[int(len(description)/2)])

				if next_day == 0:
					next_day = 8
				i = next_day
				icons = []
				description = []
				tempmin = 100
				tempmax = -100
				self.WeatherInfo["forecastTomorrowDay"] = self.convertCurrentDay(parsed_json['list'][i]['dt'])
				self.WeatherInfo["forecastTomorrowDate"] = self.convertCurrentDate(parsed_json['list'][i]['dt'])
				while i < int(next_day + 8):
					icons.append(parsed_json["list"][i]['weather'][0]['icon'])
					description.append(parsed_json["list"][i]['weather'][0]['description'])
					if float(parsed_json["list"][i]['main']['temp']) < tempmin:
						tempmin = float(parsed_json["list"][i]['main']['temp'])
					if float(parsed_json["list"][i]['main']['temp']) > tempmax:
						tempmax = float(parsed_json["list"][i]['main']['temp'])
					i += 1
				self.WeatherInfo["forecastTomorrowCode"] = str(self.ConvertIconCode(icons[int(len(icons)/2)]))
				self.WeatherInfo["forecastTomorrowPicon"] = str(self.convertOWMIconName(icons[int(len(icons)/2)]))
				self.WeatherInfo["forecastTomorrowTempMax"] = format(tempmax, str(numbers)) + self.ConvertTemp(config.plugins.VWeather3.Units.value)
				self.WeatherInfo["forecastTomorrowTempMin"] = format(tempmin, str(numbers)) + self.ConvertTemp(config.plugins.VWeather3.Units.value)
				self.WeatherInfo["forecastTomorrowText"] = str(description[int(len(description)/2)])

				if next_day == 8:
					next_day = 16
				else:
					next_day = next_day + 8
				day = 0
				for aday in range(0, 4):
					day += 1
					i = next_day + (aday * 8)
					nd = i
					icons = []
					description = []
					tempmin = 100
					tempmax = -100
					if i < int(len(parsed_json["list"])):
						self.WeatherInfo["forecastTomorrow" + str(day) + "Day"] = self.convertCurrentDay(parsed_json['list'][i]['dt'])
						self.WeatherInfo["forecastTomorrow" + str(day) + "Date"] = self.convertCurrentDate(parsed_json['list'][i]['dt'])
						while i < int(nd + 8) and i < int(len(parsed_json["list"])):
							icons.append(parsed_json["list"][i]['weather'][0]['icon'])
							description.append(parsed_json["list"][i]['weather'][0]['description'])
							if float(parsed_json["list"][i]['main']['temp']) < tempmin:
								tempmin = float(parsed_json["list"][i]['main']['temp'])
							if float(parsed_json["list"][i]['main']['temp']) > tempmax:
								tempmax = float(parsed_json["list"][i]['main']['temp'])
							i += 1
						self.WeatherInfo["forecastTomorrow" + str(day) + "Code"] = str(self.ConvertIconCode(icons[int(len(icons)/2)]))
						self.WeatherInfo["forecastTomorrow" + str(day) + "Picon"] = str(self.convertOWMIconName(icons[int(len(icons)/2)]))
						self.WeatherInfo["forecastTomorrow" + str(day) + "TempMax"] = format(tempmax, str(numbers)) + self.ConvertTemp(config.plugins.VWeather3.Units.value)
						self.WeatherInfo["forecastTomorrow" + str(day) + "TempMin"] = format(tempmin, str(numbers)) + self.ConvertTemp(config.plugins.VWeather3.Units.value)
						self.WeatherInfo["forecastTomorrow" + str(day) + "Text"] = str(description[int(len(description)/2)])

			except Exception as ex:
				write_log("Fehler in GotOpenWeatherMapWeatherData : " + str(ex))

	#CurrentOpenWeatherMap
	def GotCurrentOpenWeatherMapWeatherData(self, data = None):
		write_log("###################################### Current OpenWeatherMap Data ################################################")
		write_log("Data : " + str(data))
		if data is not None:
			try:
				parsed_json = json.loads(data)

				self.WeatherInfo["provider"] = "OpenWeatherMap"
				self.WeatherInfo["currentLocation"] = str(self.ConvertCityName(parsed_json['name']))
				self.WeatherInfo["currentCountry"] = str(parsed_json['sys']["country"])

				self.WeatherInfo["windChill"] = format(float(parsed_json['main']['temp']), str(numbers)) + self.ConvertTemp(config.plugins.VWeather3.Units.value)
				if "deg" in parsed_json['wind']:
					self.WeatherInfo["windDirectionShort"] = str(self.ConvertDirectionShort(parsed_json['wind']['deg']))
					self.WeatherInfo["windDirectionLong"] = str(self.ConvertDirectionLong(parsed_json['wind']['deg']))
				else:
					self.WeatherInfo["windDirectionShort"] = "-"
					self.WeatherInfo["windDirectionLong"] = "-"
				self.WeatherInfo["windSpeed"] = format(float(parsed_json['wind']['speed']) * 3.6, '.0f') + self.ConvertSpeed(config.plugins.VWeather3.Units.value)

				self.WeatherInfo["atmoHumidity"] = format(float(parsed_json['main']['humidity']), '.0f') + ' %'
				self.WeatherInfo["atmoRising"] = " "
				if "visibility" in parsed_json:
					self.WeatherInfo["atmoVisibility"] = format(float(parsed_json['visibility'] / 1000), str(numbers)) + self.ConvertVisibility(config.plugins.VWeather3.Units.value)
				else:
					self.WeatherInfo["atmoVisibility"] = "0" + self.ConvertVisibility(config.plugins.VWeather3.Units.value)

				self.WeatherInfo["astroSunrise"] = self.convertAstroSun(parsed_json['sys']['sunrise'])
				self.WeatherInfo["astroSunset"] = self.convertAstroSun(parsed_json['sys']['sunset'])

				self.WeatherInfo["geoLat"] = format(float(parsed_json['coord']['lat']), '.4f')
				self.WeatherInfo["geoLong"] = format(float(parsed_json['coord']['lon']), '.4f')
				self.WeatherInfo["geoData"] = format(float(parsed_json['coord']['lat']), '.4f') + " / " + format(float(parsed_json['coord']['lon']), '.4f')

				self.WeatherInfo["downloadDate"] = self.convertCurrentDateLong(parsed_json['dt'])
				self.WeatherInfo["downloadTime"] = self.convertCurrentTime(parsed_json['dt'])
				self.WeatherInfo["currentWeatherCode"] = self.ConvertIconCode(parsed_json['weather'][0]['icon'])
				self.WeatherInfo["currentWeatherTemp"] = format(float(parsed_json['main']['temp']), str(numbers)) + self.ConvertTemp(config.plugins.VWeather3.Units.value)
				self.WeatherInfo["currentWeatherText"] = str(parsed_json['weather'][0]['description'])
				self.WeatherInfo["currentWeatherPicon"] = self.convertcurrentOWMIconName(parsed_json['weather'][0]['icon'])

				self.WeatherInfo["W-Info"] = self.WeatherInfo["currentWeatherText"] + " bei " + self.WeatherInfo["forecastTodayTempMin"] + " bis " + self.WeatherInfo["forecastTodayTempMax"] + " und " + self.WeatherInfo["atmoHumidity"] + " Luftfeuchtigkeit"
				write_log("###################################### Current OpenWeatherMap ################################################")
				for k, v in parsed_json.items():
					write_log(str(k) + ":" + str(v))
			except Exception as ex:
				write_log("Fehler in GotCurrentOpenWeatherMapWeatherData : " + str(ex))

	#Darksky
	def GotDarkskyWeatherData(self, data = None):
		write_log("Data : " + str(data))
		if data is not None:
			try:
				global dsplace
				parsed_json = json.loads(data)
				for k, v in parsed_json.items():
					write_log(str(k) + ":" + str(v))

				self.WeatherInfo["provider"] = "DarkSky"
				self.WeatherInfo["currentLocation"] = dsplace
				self.WeatherInfo["currentCountry"] = ""
				self.WeatherInfo["W-Info"] = str(parsed_json['daily']['summary'])

				self.WeatherInfo["windChill"] = format(float(parsed_json['currently']['apparentTemperature']), str(numbers)) + self.ConvertTemp(config.plugins.VWeather3.Units.value)
				self.WeatherInfo["windDirectionShort"] = str(self.ConvertDirectionShort(parsed_json['currently']['windBearing']))
				self.WeatherInfo["windDirectionLong"] = str(self.ConvertDirectionLong(parsed_json['currently']['windBearing']))
				self.WeatherInfo["windSpeed"] = format(float(parsed_json['currently']['windSpeed']) * 3.6, '.0f') + self.ConvertSpeed(config.plugins.VWeather3.Units.value)

				self.WeatherInfo["atmoHumidity"] = format(float(parsed_json['currently']['humidity']) * 100, '.0f') + ' %'
				self.WeatherInfo["atmoPressure"] = format(float(parsed_json['currently']['pressure']), '.0f') + ' mBar'
				self.WeatherInfo["atmoRising"] = " "
				self.WeatherInfo["atmoVisibility"] = format(float(parsed_json['currently']['visibility']), str(numbers)) + self.ConvertVisibility(config.plugins.VWeather3.Units.value)

				self.WeatherInfo["astroSunrise"] = self.convertAstroSun(int(parsed_json['daily']['data'][0]['sunriseTime']))
				self.WeatherInfo["astroSunset"] = self.convertAstroSun(int(parsed_json['daily']['data'][0]['sunsetTime']))

				self.WeatherInfo["geoLat"] = format(float(parsed_json['latitude']), '.4f')
				self.WeatherInfo["geoLong"] = format(float(parsed_json['longitude']), '.4f')
				self.WeatherInfo["geoData"] = format(float(parsed_json['latitude']), '.4f') + " / " + format(float(parsed_json['longitude']), '.4f')

				self.WeatherInfo["downloadDate"] = self.convertCurrentDate(int(parsed_json['currently']['time']))
				self.WeatherInfo["downloadTime"] = self.convertCurrentTime(int(parsed_json['currently']['time']))
				self.WeatherInfo["currentWeatherCode"] = self.ConvertIconCode(parsed_json['currently']['icon'])
				self.WeatherInfo["currentWeatherTemp"] = format(float(parsed_json['currently']['temperature']), str(numbers)) + self.ConvertTemp(config.plugins.VWeather3.Units.value)
				self.WeatherInfo["currentWeatherText"] = str(parsed_json['currently']['summary'])
				self.WeatherInfo["currentWeatherPicon"] = self.convertcurrentIconName(parsed_json['currently']['icon'])

				self.WeatherInfo["forecastTodayCode"] = self.ConvertIconCode(parsed_json['daily']['data'][0]['icon'])
				self.WeatherInfo["forecastTodayDay"] = self.convertCurrentDay(int(parsed_json['daily']['data'][0]['time']))
				self.WeatherInfo["forecastTodayDate"] = self.convertCurrentDate(int(parsed_json['daily']['data'][0]['time']))
				self.WeatherInfo["forecastTodayTempMax"] = format(float(parsed_json['daily']['data'][0]['temperatureMax']), str(numbers)) + self.ConvertTemp(config.plugins.VWeather3.Units.value)
				self.WeatherInfo["forecastTodayTempMin"] = format(float(parsed_json['daily']['data'][0]['temperatureMin']), str(numbers)) + self.ConvertTemp(config.plugins.VWeather3.Units.value)
				self.WeatherInfo["forecastTodayText"] = self.convertWeatherText(parsed_json['daily']['data'][0]['icon'])
				self.WeatherInfo["forecastTodayPicon"] = self.convertIconName(parsed_json['daily']['data'][0]['icon'])

				days =["0","1","2","3","4","5","6"]
				for day in days:
					aday = int(day)+1
					if day == "0":
						day = ""
					self.WeatherInfo["forecastTomorrow" + day + "Code"] = self.ConvertIconCode(parsed_json['daily']['data'][aday]['icon'])
					self.WeatherInfo["forecastTomorrow" + day + "Day"] = self.convertCurrentDay(int(parsed_json['daily']['data'][aday]['time']))
					self.WeatherInfo["forecastTomorrow" + day + "Date"] = self.convertCurrentDate(int(parsed_json['daily']['data'][aday]['time']))
					self.WeatherInfo["forecastTomorrow" + day + "TempMax"] = format(float(parsed_json['daily']['data'][aday]['temperatureMax']), str(numbers)) + self.ConvertTemp(config.plugins.VWeather3.Units.value)
					self.WeatherInfo["forecastTomorrow" + day + "TempMin"] = format(float(parsed_json['daily']['data'][aday]['temperatureMin']), str(numbers)) + self.ConvertTemp(config.plugins.VWeather3.Units.value)
					self.WeatherInfo["forecastTomorrow" + day + "Text"] = self.convertWeatherText(parsed_json['daily']['data'][aday]['icon'])
					self.WeatherInfo["forecastTomorrow" + day + "Picon"] = self.convertIconName(parsed_json['daily']['data'][aday]['icon'])

				if "alerts" in parsed_json:
					self.WeatherInfo["alerts"] = str(parsed_json['alerts'][0]['description'])
					if config.plugins.VWeather3.Darksky_alerts.value == "true":
						Notifications.AddPopup(str(parsed_json['alerts'][0]['title']) + " ab " + str(convertDateTime(parsed_json['alerts'][0]['time'])) + "\n" + str(parsed_json['alerts'][0]['description']), MessageBox.TYPE_INFO, 20)
				else:
					self.WeatherInfo["alerts"] = "keine Unwetterwarnungen vorhanden"
				for k, v in self.WeatherInfo.items():
					write_log("WeatherInfo : " + str(k) + ":" + str(v))
			except Exception as ex:
				write_log("Fehler in GotWeatherData : " + str(ex))

	#Yahoo
	def GotYahooWeatherData(self, data = None):
		if data is not None:
			try:
				parsed_json = json.loads(data)
				write_log("###################################### Yahoo Data ################################################")
				write_log(str(data))
				write_log("###################################### Yahoo Items ################################################")
				for k, v in parsed_json.items():
					write_log(str(k) + ":" + str(v))
				self.WeatherInfo["provider"] = "Yahoo"
				self.WeatherInfo["currentLocation"] = str(self.ConvertCityName(parsed_json['location']['city']))
				self.WeatherInfo["currentCountry"] = str(parsed_json['location']['country'])
				self.WeatherInfo["currentRegion"] = self.ConvertRegion(parsed_json['location']['region'])

				self.WeatherInfo["windChill"] = format(float(parsed_json['current_observation']['wind']['chill']), str(numbers)) + self.ConvertTemp(config.plugins.VWeather3.Units.value)
				self.WeatherInfo["windDirectionShort"] = str(self.ConvertDirectionShort(parsed_json['current_observation']['wind']['direction']))
				self.WeatherInfo["windDirectionLong"] = str(self.ConvertDirectionLong(parsed_json['current_observation']['wind']['direction']))
				self.WeatherInfo["windSpeed"] = format(float(parsed_json['current_observation']['wind']['speed']), '.0f') + self.ConvertSpeed(config.plugins.VWeather3.Units.value)

				self.WeatherInfo["atmoHumidity"] = format(float(parsed_json['current_observation']['atmosphere']['humidity']), '.0f') + ' %'
				self.WeatherInfo["atmoPressure"] = format(float(parsed_json['current_observation']['atmosphere']['pressure']), '.0f') + ' mBar'
				self.WeatherInfo["atmoRising"] = self.ConvertRise(parsed_json['current_observation']['atmosphere']['rising'])
				self.WeatherInfo["atmoVisibility"] = format(float(parsed_json['current_observation']['atmosphere']['visibility']), str(numbers)) + self.ConvertVisibility(config.plugins.VWeather3.Units.value)

				self.WeatherInfo["astroSunrise"] = self.ConvertTime(parsed_json['current_observation']['astronomy']['sunrise'])
				self.WeatherInfo["astroSunset"] = self.ConvertTime(parsed_json['current_observation']['astronomy']['sunset'])

				self.WeatherInfo["geoLat"] = format(float(parsed_json['location']['lat']), '.4f')
				self.WeatherInfo["geoLong"] = format(float(parsed_json['location']['long']), '.4f')
				self.WeatherInfo["geoData"] = format(float(parsed_json['location']['lat']), '.4f') + " / " + format(float(parsed_json['location']['long']), '.4f')

				self.WeatherInfo["downloadDate"] = self.convertCurrentDateLong(int(parsed_json['current_observation']['pubDate']))
				self.WeatherInfo["downloadTime"] = self.convertCurrentTime(int(parsed_json['current_observation']['pubDate']))
				self.WeatherInfo["currentWeatherCode"] = self.ConvertCondition(parsed_json['current_observation']['condition']['code'])
				self.WeatherInfo["currentWeatherTemp"] = format(float(parsed_json['current_observation']['condition']['temperature']), str(numbers)) + self.ConvertTemp(config.plugins.VWeather3.Units.value)
				self.WeatherInfo["currentWeatherText"] = self.ConvertInfo(parsed_json['current_observation']['condition']['text'])
				self.WeatherInfo["currentWeatherPicon"] = str(parsed_json['current_observation']['condition']['code'])

				self.WeatherInfo["forecastTodayCode"] = self.ConvertCondition(parsed_json['forecasts'][0]['code'])
				self.WeatherInfo["forecastTodayDay"] = self.convertCurrentDay(int(parsed_json['forecasts'][0]['date']) + get_timezone_delta(parsed_json['location']['timezone_id']))
				self.WeatherInfo["forecastTodayDate"] = self.convertCurrentDate(int(parsed_json['forecasts'][0]['date']) + get_timezone_delta(parsed_json['location']['timezone_id']))
				self.WeatherInfo["forecastTodayTempMax"] = format(float(parsed_json['forecasts'][0]['high']), str(numbers)) + self.ConvertTemp(config.plugins.VWeather3.Units.value)
				self.WeatherInfo["forecastTodayTempMin"] = format(float(parsed_json['forecasts'][0]['low']), str(numbers)) + self.ConvertTemp(config.plugins.VWeather3.Units.value)
				self.WeatherInfo["forecastTodayText"] = self.ConvertInfo(parsed_json['forecasts'][0]['text'])
				self.WeatherInfo["forecastTodayPicon"] = str(parsed_json['forecasts'][0]['code']) 

				days =["0","1","2","3","4","5","6","7","8"]
				for day in days:
					aday = int(day)+1
					if day == "0":
						day = ""
						aday = 1
					self.WeatherInfo["forecastTomorrow" + day + "Code"] = self.ConvertCondition(parsed_json['forecasts'][aday]['code'])
					self.WeatherInfo["forecastTomorrow" + day + "Day"] = self.convertCurrentDay(int(parsed_json['forecasts'][aday]['date']) + get_timezone_delta(parsed_json['location']['timezone_id']))
					self.WeatherInfo["forecastTomorrow" + day + "Date"] = self.convertCurrentDate(int(parsed_json['forecasts'][aday]['date']) + get_timezone_delta(parsed_json['location']['timezone_id']))
					self.WeatherInfo["forecastTomorrow" + day + "TempMax"] = format(float(parsed_json['forecasts'][aday]['high']), str(numbers)) + self.ConvertTemp(config.plugins.VWeather3.Units.value)
					self.WeatherInfo["forecastTomorrow" + day + "TempMin"] = format(float(parsed_json['forecasts'][aday]['low']), str(numbers)) + self.ConvertTemp(config.plugins.VWeather3.Units.value)
					self.WeatherInfo["forecastTomorrow" + day + "Text"] = self.ConvertInfo(parsed_json['forecasts'][aday]['text'])
					self.WeatherInfo["forecastTomorrow" + day + "Picon"] = str(parsed_json['forecasts'][aday]['code'])

				self.WeatherInfo["W-Info"] = self.WeatherInfo["currentWeatherText"] + " bei " + self.WeatherInfo["forecastTodayTempMin"] + " bis " + self.WeatherInfo["forecastTodayTempMax"] + " und " + self.WeatherInfo["atmoHumidity"] + " Luftfeuchtigkeit"
			except Exception as ex:
				write_log("Fehler in GotYahooWeatherData : " + str(ex))

	#DWD
	def GotDWDWeatherData(self, data = None):
		if data is not None:
			try:
				parsed_json = json.loads(str(data).replace("warnWetter.loadWarnings(","").replace(");",""))
				cellID = str(config.plugins.VWeather3.DWD_WeatherCellID.value)
				self.WeatherInfo["DWD_DATETIME"] = self.convertDateTime(int(parsed_json['time']/1000 - 7200))
				if 'warnings' in parsed_json:
					if cellID in parsed_json['warnings']:
						listnumber = 0
						i = 0
						while i < len(parsed_json['warnings'][cellID]):
							if int(parsed_json['warnings'][cellID][i]['level']) > listnumber:
								listnumber = int(i)
							i += 1
						self.WeatherInfo["DWD_ALERT_START"] = self.convertDateTime(int(parsed_json['warnings'][cellID][int(listnumber)]['start']/1000 - 7200))
						self.WeatherInfo["DWD_ALERT_END"] = self.convertDateTime(int(parsed_json['warnings'][cellID][int(listnumber)]['end']/1000 - 7200))
						self.WeatherInfo["DWD_REGION"] = str(parsed_json['warnings'][cellID][int(listnumber)]['regionName'])
						self.WeatherInfo["DWD_ALERT_HEAD"] = str(parsed_json['warnings'][cellID][int(listnumber)]['headline'])
						self.WeatherInfo["DWD_ALERT_EVENT"] = str(parsed_json['warnings'][cellID][int(listnumber)]['event'])
						self.WeatherInfo["alerts"] = str(parsed_json['warnings'][cellID][int(listnumber)]['headline'])
						self.WeatherInfo["DWD_ALERT_TEXT"] = str(parsed_json['warnings'][cellID][int(listnumber)]['description'])
						if str(parsed_json['warnings'][cellID][int(listnumber)]['instruction']) != 'None':
							self.WeatherInfo["DWD_ALERT_INSTRUCTION"] = str(parsed_json['warnings'][cellID][int(listnumber)]['instruction'])
						else:
							self.WeatherInfo["DWD_ALERT_INSTRUCTION"] = " "
						self.WeatherInfo["DWD_WARNLEVEL"] = str(parsed_json['warnings'][cellID][int(listnumber)]['level'])
						wtext = ''
						wlist = []
						for entry in parsed_json['warnings'][cellID]:
							wtext = wtext + str(entry['headline']) + '\n\n' + self.convertDateTime(int(entry['start']/1000 - 7200)) + ' bis ' + self.convertDateTime(int(entry['end']/1000 - 7200)) + '\n\n' + str(entry['description']) + '\n' + str(entry['instruction']) + '\n***********************************************************\n'
							if str(entry['instruction']) != 'None':
								r = (str(entry['headline']), self.convertDateTime(int(entry['start']/1000 - 7200)), self.convertDateTime(int(entry['end']/1000 - 7200)), str(entry['description']), str(entry['instruction']))
							else:
								r = (str(entry['headline']), self.convertDateTime(int(entry['start']/1000 - 7200)), self.convertDateTime(int(entry['end']/1000 - 7200)), str(entry['description']), ' ')
							wlist.append(r)
						self.WeatherInfo["DWD_ALERT_TEXT_LONG"] = str(wtext)
						self.WeatherInfo["DWD_ALERT_LIST"] = wlist

						if "STURM" in self.WeatherInfo["DWD_ALERT_EVENT"].upper() or "BÖEN" in self.WeatherInfo["DWD_ALERT_EVENT"].upper() or "ORKAN" in self.WeatherInfo["DWD_ALERT_EVENT"].upper():
							url = 'https://www.dwd.de/DWD/warnungen/warnapp_gemeinden/json/warnungen_gemeinde_map_' + config.plugins.VWeather3.DWD_BL.value + '_sturm.png'
						elif "SCHNEE" in self.WeatherInfo["DWD_ALERT_EVENT"].upper():
							url = 'https://www.dwd.de/DWD/warnungen/warnapp_gemeinden/json/warnungen_gemeinde_map_' + config.plugins.VWeather3.DWD_BL.value + '_schnee.png'
						elif "GEWITTER" in self.WeatherInfo["DWD_ALERT_EVENT"].upper() or "BLITZ" in self.WeatherInfo["DWD_ALERT_EVENT"].upper():
							url = 'https://www.dwd.de/DWD/warnungen/warnapp_gemeinden/json/warnungen_gemeinde_map_' + config.plugins.VWeather3.DWD_BL.value + '_gewitter.png'
						elif "REGEN" in self.WeatherInfo["DWD_ALERT_EVENT"].upper():
							url = 'https://www.dwd.de/DWD/warnungen/warnapp_gemeinden/json/warnungen_gemeinde_map_' + config.plugins.VWeather3.DWD_BL.value + '_regen.png'
						elif "NEBEL" in self.WeatherInfo["DWD_ALERT_EVENT"].upper():
							url = 'https://www.dwd.de/DWD/warnungen/warnapp_gemeinden/json/warnungen_gemeinde_map_' + config.plugins.VWeather3.DWD_BL.value + '_nebel.png'
						elif "FROST" in self.WeatherInfo["DWD_ALERT_EVENT"].upper():
							url = 'https://www.dwd.de/DWD/warnungen/warnapp_gemeinden/json/warnungen_gemeinde_map_' + config.plugins.VWeather3.DWD_BL.value + '_frost.png'
						elif "GLÄTTE" in self.WeatherInfo["DWD_ALERT_EVENT"].upper() or "GLATT" in self.WeatherInfo["DWD_ALERT_EVENT"].upper():
							url = 'https://www.dwd.de/DWD/warnungen/warnapp_gemeinden/json/warnungen_gemeinde_map_' + config.plugins.VWeather3.DWD_BL.value + '_glatteis.png'
						elif "TAU" in self.WeatherInfo["DWD_ALERT_EVENT"].upper():
							url = 'https://www.dwd.de/DWD/warnungen/warnapp_gemeinden/json/warnungen_gemeinde_map_' + config.plugins.VWeather3.DWD_BL.value + '_tauwetter.png'
						elif "HITZE" in self.WeatherInfo["DWD_ALERT_EVENT"].upper():
							url = 'https://www.dwd.de/DWD/warnungen/warnapp_gemeinden/json/warnungen_gemeinde_map_' + config.plugins.VWeather3.DWD_BL.value + '_hitze.png'
						elif "UV" in self.WeatherInfo["DWD_ALERT_EVENT"].upper():
							url = 'https://www.dwd.de/DWD/warnungen/warnapp_gemeinden/json/warnungen_gemeinde_map_' + config.plugins.VWeather3.DWD_BL.value + '_uv.png'
						else:
							url = 'https://www.dwd.de/DWD/warnungen/warnapp_gemeinden/json/warnungen_gemeinde_map_' + config.plugins.VWeather3.DWD_BL.value + '.png'
						self.downloadImage1(url, 'dwd_alert.png', 10)
						self.downloadImage1(url, 'dwd_alert.png', 10, '/usr/share/enigma2/VWeather3/')
					else:
						self.WeatherInfo["DWD_ALERT_START"] = " "
						self.WeatherInfo["DWD_ALERT_END"] = " "
						self.WeatherInfo["DWD_REGION"] = " "
						self.WeatherInfo["DWD_ALERT_HEAD"] = " "
						self.WeatherInfo["DWD_ALERT_TEXT"] = " "
						self.WeatherInfo["DWD_ALERT_TEXT_LONG"] = " "
						self.WeatherInfo["DWD_ALERT_EVENT"] = " "
						self.WeatherInfo["DWD_ALERT_INSTRUCTION"] = " "
						self.WeatherInfo["alerts"] = "keine Unwetterwarnungen vorhanden"
						self.WeatherInfo["DWD_WARNLEVEL"] = "0"
						self.WeatherInfo["DWD_ALERT_LIST"] = []
				url = 'https://www.dwd.de/DWD/wetter/radar/rad_' + config.plugins.VWeather3.DWD_BL.value + '_akt.jpg'
				self.downloadImage1(url, 'dwd_radar.jpg', 10)
				self.downloadImage1(url, 'dwd_radar.jpg', 10, '/usr/share/enigma2/VWeather3/')
			except Exception as ex:
				write_log("Fehler in GotDWDWeatherData : " + str(ex))

	#DWD Pollen
	def GotDWDPollenData(self, data = None):
		if data is not None:
			try:
				Pollen = json.loads(data)
				pregion = int(config.plugins.VWeather3.DWD_Pollenflugregion.value)
				write_log("###################################### DWD Pollen Items ################################################")
				write_log(str(data))
				write_log('Region : ' + str(pregion))
				i = 0
				self.WeatherInfo["DWD_POLLEN_DATETIME"] = str(Pollen['last_update'])
				while i < len(Pollen['content']):
					if int(Pollen['content'][i]['partregion_id']) == pregion or (int(Pollen['content'][i]['region_id']) == pregion and int(Pollen['content'][i]['partregion_id']) == -1):
						if pregion in [20,50]:
							self.WeatherInfo["DWD_POLLEN_REGION"] = str(Pollen['content'][i]['region_name'])
						else:
							self.WeatherInfo["DWD_POLLEN_REGION"] = str(Pollen['content'][i]['partregion_name'])
						self.WeatherInfo["DWD_POLLEN_LIST"] = Pollen['content'][i]['Pollen']
						t = localtime()
						if t.tm_hour < 11:
							self.WeatherInfo["DWD_POLLEN_TODAY_HASEL_INTENSITY"] = Pollenimgidx[Pollen['content'][i]['Pollen']['Hasel']['tomorrow']]
							self.WeatherInfo["DWD_POLLEN_TODAY_HASEL_LOAD"] = Pollengruppen[Pollen['content'][i]['Pollen']['Hasel']['tomorrow']]
							self.WeatherInfo["DWD_POLLEN_TODAY_ESCHE_INTENSITY"] = Pollenimgidx[Pollen['content'][i]['Pollen']['Esche']['tomorrow']]
							self.WeatherInfo["DWD_POLLEN_TODAY_ESCHE_LOAD"] = Pollengruppen[Pollen['content'][i]['Pollen']['Esche']['tomorrow']]
							self.WeatherInfo["DWD_POLLEN_TODAY_ERLE_INTENSITY"] = Pollenimgidx[Pollen['content'][i]['Pollen']['Erle']['tomorrow']]
							self.WeatherInfo["DWD_POLLEN_TODAY_ERLE_LOAD"] = Pollengruppen[Pollen['content'][i]['Pollen']['Erle']['tomorrow']]
							self.WeatherInfo["DWD_POLLEN_TODAY_BIRKE_INTENSITY"] = Pollenimgidx[Pollen['content'][i]['Pollen']['Birke']['tomorrow']]
							self.WeatherInfo["DWD_POLLEN_TODAY_BIRKE_LOAD"] = Pollengruppen[Pollen['content'][i]['Pollen']['Birke']['tomorrow']]
							self.WeatherInfo["DWD_POLLEN_TODAY_GRAESER_INTENSITY"] = Pollenimgidx[Pollen['content'][i]['Pollen']['Graeser']['tomorrow']]
							self.WeatherInfo["DWD_POLLEN_TODAY_GRAESER_LOAD"] = Pollengruppen[Pollen['content'][i]['Pollen']['Graeser']['tomorrow']]
							self.WeatherInfo["DWD_POLLEN_TODAY_AMBROSIA_INTENSITY"] = Pollenimgidx[Pollen['content'][i]['Pollen']['Ambrosia']['tomorrow']]
							self.WeatherInfo["DWD_POLLEN_TODAY_AMBROSIA_LOAD"] = Pollengruppen[Pollen['content'][i]['Pollen']['Ambrosia']['tomorrow']]
							self.WeatherInfo["DWD_POLLEN_TODAY_ROGGEN_INTENSITY"] = Pollenimgidx[Pollen['content'][i]['Pollen']['Roggen']['tomorrow']]
							self.WeatherInfo["DWD_POLLEN_TODAY_ROGGEN_LOAD"] = Pollengruppen[Pollen['content'][i]['Pollen']['Roggen']['tomorrow']]
							self.WeatherInfo["DWD_POLLEN_TODAY_BEIFUSS_INTENSITY"] = Pollenimgidx[Pollen['content'][i]['Pollen']['Beifuss']['tomorrow']]
							self.WeatherInfo["DWD_POLLEN_TODAY_BEIFUSS_LOAD"] = Pollengruppen[Pollen['content'][i]['Pollen']['Beifuss']['tomorrow']]

							self.WeatherInfo["DWD_POLLEN_TOMORROW_HASEL_INTENSITY"] = Pollenimgidx[Pollen['content'][i]['Pollen']['Hasel']['dayafter_to']]
							self.WeatherInfo["DWD_POLLEN_TOMORROW_HASEL_LOAD"] = Pollengruppen[Pollen['content'][i]['Pollen']['Hasel']['dayafter_to']]
							self.WeatherInfo["DWD_POLLEN_TOMORROW_ESCHE_INTENSITY"] = Pollenimgidx[Pollen['content'][i]['Pollen']['Esche']['dayafter_to']]
							self.WeatherInfo["DWD_POLLEN_TOMORROW_ESCHE_LOAD"] = Pollengruppen[Pollen['content'][i]['Pollen']['Esche']['dayafter_to']]
							self.WeatherInfo["DWD_POLLEN_TOMORROW_ERLE_INTENSITY"] = Pollenimgidx[Pollen['content'][i]['Pollen']['Erle']['dayafter_to']]
							self.WeatherInfo["DWD_POLLEN_TOMORROW_ERLE_LOAD"] = Pollengruppen[Pollen['content'][i]['Pollen']['Erle']['dayafter_to']]
							self.WeatherInfo["DWD_POLLEN_TOMORROW_BIRKE_INTENSITY"] = Pollenimgidx[Pollen['content'][i]['Pollen']['Birke']['dayafter_to']]
							self.WeatherInfo["DWD_POLLEN_TOMORROW_BIRKE_LOAD"] = Pollengruppen[Pollen['content'][i]['Pollen']['Birke']['dayafter_to']]
							self.WeatherInfo["DWD_POLLEN_TOMORROW_GRAESER_INTENSITY"] = Pollenimgidx[Pollen['content'][i]['Pollen']['Graeser']['dayafter_to']]
							self.WeatherInfo["DWD_POLLEN_TOMORROW_GRAESER_LOAD"] = Pollengruppen[Pollen['content'][i]['Pollen']['Graeser']['dayafter_to']]
							self.WeatherInfo["DWD_POLLEN_TOMORROW_AMBROSIA_INTENSITY"] = Pollenimgidx[Pollen['content'][i]['Pollen']['Ambrosia']['dayafter_to']]
							self.WeatherInfo["DWD_POLLEN_TOMORROW_AMBROSIA_LOAD"] = Pollengruppen[Pollen['content'][i]['Pollen']['Ambrosia']['dayafter_to']]
							self.WeatherInfo["DWD_POLLEN_TOMORROW_ROGGEN_INTENSITY"] = Pollenimgidx[Pollen['content'][i]['Pollen']['Roggen']['dayafter_to']]
							self.WeatherInfo["DWD_POLLEN_TOMORROW_ROGGEN_LOAD"] = Pollengruppen[Pollen['content'][i]['Pollen']['Roggen']['dayafter_to']]
							self.WeatherInfo["DWD_POLLEN_TOMORROW_BEIFUSS_INTENSITY"] = Pollenimgidx[Pollen['content'][i]['Pollen']['Beifuss']['dayafter_to']]
							self.WeatherInfo["DWD_POLLEN_TOMORROW_BEIFUSS_LOAD"] = Pollengruppen[Pollen['content'][i]['Pollen']['Beifuss']['dayafter_to']]
						else:
							self.WeatherInfo["DWD_POLLEN_TODAY_HASEL_INTENSITY"] = Pollenimgidx[Pollen['content'][i]['Pollen']['Hasel']['today']]
							self.WeatherInfo["DWD_POLLEN_TODAY_HASEL_LOAD"] = Pollengruppen[Pollen['content'][i]['Pollen']['Hasel']['today']]
							self.WeatherInfo["DWD_POLLEN_TODAY_ESCHE_INTENSITY"] = Pollenimgidx[Pollen['content'][i]['Pollen']['Esche']['today']]
							self.WeatherInfo["DWD_POLLEN_TODAY_ESCHE_LOAD"] = Pollengruppen[Pollen['content'][i]['Pollen']['Esche']['today']]
							self.WeatherInfo["DWD_POLLEN_TODAY_ERLE_INTENSITY"] = Pollenimgidx[Pollen['content'][i]['Pollen']['Erle']['today']]
							self.WeatherInfo["DWD_POLLEN_TODAY_ERLE_LOAD"] = Pollengruppen[Pollen['content'][i]['Pollen']['Erle']['today']]
							self.WeatherInfo["DWD_POLLEN_TODAY_BIRKE_INTENSITY"] = Pollenimgidx[Pollen['content'][i]['Pollen']['Birke']['today']]
							self.WeatherInfo["DWD_POLLEN_TODAY_BIRKE_LOAD"] = Pollengruppen[Pollen['content'][i]['Pollen']['Birke']['today']]
							self.WeatherInfo["DWD_POLLEN_TODAY_GRAESER_INTENSITY"] = Pollenimgidx[Pollen['content'][i]['Pollen']['Graeser']['today']]
							self.WeatherInfo["DWD_POLLEN_TODAY_GRAESER_LOAD"] = Pollengruppen[Pollen['content'][i]['Pollen']['Graeser']['today']]
							self.WeatherInfo["DWD_POLLEN_TODAY_AMBROSIA_INTENSITY"] = Pollenimgidx[Pollen['content'][i]['Pollen']['Ambrosia']['today']]
							self.WeatherInfo["DWD_POLLEN_TODAY_AMBROSIA_LOAD"] = Pollengruppen[Pollen['content'][i]['Pollen']['Ambrosia']['today']]
							self.WeatherInfo["DWD_POLLEN_TODAY_ROGGEN_INTENSITY"] = Pollenimgidx[Pollen['content'][i]['Pollen']['Roggen']['today']]
							self.WeatherInfo["DWD_POLLEN_TODAY_ROGGEN_LOAD"] = Pollengruppen[Pollen['content'][i]['Pollen']['Roggen']['today']]
							self.WeatherInfo["DWD_POLLEN_TODAY_BEIFUSS_INTENSITY"] = Pollenimgidx[Pollen['content'][i]['Pollen']['Beifuss']['today']]
							self.WeatherInfo["DWD_POLLEN_TODAY_BEIFUSS_LOAD"] = Pollengruppen[Pollen['content'][i]['Pollen']['Beifuss']['today']]

							self.WeatherInfo["DWD_POLLEN_TOMORROW_HASEL_INTENSITY"] = Pollenimgidx[Pollen['content'][i]['Pollen']['Hasel']['tomorrow']]
							self.WeatherInfo["DWD_POLLEN_TOMORROW_HASEL_LOAD"] = Pollengruppen[Pollen['content'][i]['Pollen']['Hasel']['tomorrow']]
							self.WeatherInfo["DWD_POLLEN_TOMORROW_ESCHE_INTENSITY"] = Pollenimgidx[Pollen['content'][i]['Pollen']['Esche']['tomorrow']]
							self.WeatherInfo["DWD_POLLEN_TOMORROW_ESCHE_LOAD"] = Pollengruppen[Pollen['content'][i]['Pollen']['Esche']['tomorrow']]
							self.WeatherInfo["DWD_POLLEN_TOMORROW_ERLE_INTENSITY"] = Pollenimgidx[Pollen['content'][i]['Pollen']['Erle']['tomorrow']]
							self.WeatherInfo["DWD_POLLEN_TOMORROW_ERLE_LOAD"] = Pollengruppen[Pollen['content'][i]['Pollen']['Erle']['tomorrow']]
							self.WeatherInfo["DWD_POLLEN_TOMORROW_BIRKE_INTENSITY"] = Pollenimgidx[Pollen['content'][i]['Pollen']['Birke']['tomorrow']]
							self.WeatherInfo["DWD_POLLEN_TOMORROW_BIRKE_LOAD"] = Pollengruppen[Pollen['content'][i]['Pollen']['Birke']['tomorrow']]
							self.WeatherInfo["DWD_POLLEN_TOMORROW_GRAESER_INTENSITY"] = Pollenimgidx[Pollen['content'][i]['Pollen']['Graeser']['tomorrow']]
							self.WeatherInfo["DWD_POLLEN_TOMORROW_GRAESER_LOAD"] = Pollengruppen[Pollen['content'][i]['Pollen']['Graeser']['tomorrow']]
							self.WeatherInfo["DWD_POLLEN_TOMORROW_AMBROSIA_INTENSITY"] = Pollenimgidx[Pollen['content'][i]['Pollen']['Ambrosia']['tomorrow']]
							self.WeatherInfo["DWD_POLLEN_TOMORROW_AMBROSIA_LOAD"] = Pollengruppen[Pollen['content'][i]['Pollen']['Ambrosia']['tomorrow']]
							self.WeatherInfo["DWD_POLLEN_TOMORROW_ROGGEN_INTENSITY"] = Pollenimgidx[Pollen['content'][i]['Pollen']['Roggen']['tomorrow']]
							self.WeatherInfo["DWD_POLLEN_TOMORROW_ROGGEN_LOAD"] = Pollengruppen[Pollen['content'][i]['Pollen']['Roggen']['tomorrow']]
							self.WeatherInfo["DWD_POLLEN_TOMORROW_BEIFUSS_INTENSITY"] = Pollenimgidx[Pollen['content'][i]['Pollen']['Beifuss']['tomorrow']]
							self.WeatherInfo["DWD_POLLEN_TOMORROW_BEIFUSS_LOAD"] = Pollengruppen[Pollen['content'][i]['Pollen']['Beifuss']['tomorrow']]

						break
					i += 1
			except Exception as ex:
				write_log("GotDWDPollenData : " + str(ex))

	#DWD Biowetter
	def GotDWDBioData(self, data = None):
		if data is not None:
			try:
				Bio = json.loads(data)
				bioregion = int(Biowetterregionen[config.plugins.VWeather3.DWD_BL.value])
				write_log("###################################### DWD Biowetter Items ################################################")
				write_log(str(Bio['zone'][bioregion]))

				self.WeatherInfo["DWD_BIO_LIST"] = Bio['zone'][bioregion]

			except Exception as ex:
				write_log("GotDWDBioData : " + str(ex))

	#DWD Wettervorhersage
	def GotDWDForecastData(self, data=None):
		if data is not None:
			try:
				soup = BeautifulSoup(data,'html.parser')
				forecast = []
				for idx in range(2,6):
					res = soup.find_all('pre')[idx]
					r = str(res).replace('<pre style="font-family: sans-serif">','').replace('\r\n','').replace('\r','').replace('<br/>','').replace('</pre>','')
					forecast.append(r)
				self.WeatherInfo["DWD_FORECAST_LIST"] = forecast
				write_log('DWD Vorhersage : ' + str(self.WeatherInfo["DWD_FORECAST_LIST"]))
			except Exception as ex:
				write_log("GotDWDForecastData : " + str(ex))

	#Meteoalarm Wetterwarnungen AT
	def GotMeteoalarmAT(self, data=None):
		def strip_html(text):
			def fixup(m):
				text = m.group(0)
				if text[:1] == "<":
					return "" # ignore tags
				if text[:2] == "&#":
					try:
						if text[:3] == "&#x":
							return unichr(int(text[3:-1], 16))
						else:
							return unichr(int(text[2:-1]))
					except ValueError:
						pass
				elif text[:1] == "&":
					import htmlentitydefs
					entity = htmlentitydefs.entitydefs.get(text[1:-1])
					if entity:
						if entity[:2] == "&#":
							try:
								return unichr(int(entity[2:-1]))
							except ValueError:
								pass
						else:
							return unicode(entity, "iso-8859-1")
				return text # leave as is
			return re.sub("(?s)<[^>]*>|&#?\w+;", fixup, text)
		if data is not None:
			magic = '''<rss version="2.0"
			xmlns:atom="http://www.w3.org/2005/Atom"
			xmlns:content="http://purl.org/rss/1.0/modules/content/"
			xmlns:dc="http://purl.org/dc/elements/1.1/"
			xmlns:slash="http://purl.org/rss/1.0/modules/slash/"
		>'''
			try:
				self.WeatherInfo["DWD_ALERT_START"] = " "
				self.WeatherInfo["DWD_ALERT_END"] = " "
				self.WeatherInfo["DWD_REGION"] = " "
				self.WeatherInfo["DWD_ALERT_HEAD"] = " "
				self.WeatherInfo["DWD_ALERT_TEXT"] = " "
				self.WeatherInfo["DWD_ALERT_EVENT"] = " "
				self.WeatherInfo["DWD_WARNLEVEL"] = "0"
				self.WeatherInfo["DWD_ALERT_TEXT_LONG"] = " "
				t = localtime()
				self.WeatherInfo["DWD_DATETIME"] = '%02d.%02d.%04d - %02d:%02d:%02d' % (t.tm_mday, t.tm_mon, t.tm_year, t.tm_hour, t.tm_min, t.tm_sec)
				contenttext = data
				root = ET.fromstring(contenttext.replace('<content type="xhtml">',"<content:encoded><![CDATA[").replace("</content>","]]></content:encoded>").replace('<feed xmlns="http://www.w3.org/2005/Atom">',magic).replace("</feed>","</rss>"))

				if str(config.plugins.VWeather3.UWW_AT_BL.value) == 'Niederöstereich':
					slen = 6
				elif str(config.plugins.VWeather3.UWW_AT_BL.value) == 'Oberöstereich':
					slen = 4
				elif str(config.plugins.VWeather3.UWW_AT_BL.value) == 'Kärnten':
					slen = 1
				else:
					slen = len(config.plugins.VWeather3.UWW_AT_BL.value)
				for item in root.findall('./channel/item'):
					found = False
					for child in item:
						if str(child.tag) == "title":
							if str(child.text.decode('utf8')[:slen]) != str(config.plugins.VWeather3.UWW_AT_BL.value).decode('utf8')[:slen]:
								break
							else:
								self.WeatherInfo["DWD_REGION"] = child.text.encode('utf8')
								self.WeatherInfo["DWD_WARNLEVEL"] = "5"
								found = True
						elif str(child.tag) == "description":
							dstemp = strip_html(child.text.encode('utf8')).replace('Today','Heute\n').replace('Tomorrow','\nMorgen\n').replace('deutsch', '').replace(' CET', '')
							dates = re.findall(r'\d{2}.\d{2}.\d{4} \d{2}:\d{2}', dstemp)
							for idx in range(0,4):
								en = string.find(dstemp, 'english')
								if en > 0:
									de = string.find(dstemp, '.', en) + 1
									if de > 0:
										dstemp = dstemp[:en] + dstemp[de:]
									else:
										dstemp = dstemp[:en]
							if dates:
								self.WeatherInfo["DWD_ALERT_START"] = str(dates[0])
								self.WeatherInfo["DWD_ALERT_END"] = str(dates[1])
								self.WeatherInfo["DWD_ALERT_TEXT"] = (dstemp).replace('From: ','vom ').replace(' Until: ',' bis ').replace(': ', '\n')
						elif str(child.tag) == 'pubDate':
							tstamp = mktime(datetime.datetime.strptime(child.text.encode('utf8'), '%a, %d %b %Y %H:%M:%S +0200').timetuple()) + 3600
							self.WeatherInfo["DWD_DATETIME"] = str(datetime.datetime.fromtimestamp(tstamp).strftime("%d.%m.%Y %H:%M"))
						self.WeatherInfo["DWD_ALERT_TEXT_LONG"] = self.WeatherInfo["DWD_ALERT_START"] + self.WeatherInfo["DWD_ALERT_END"] + self.WeatherInfo["DWD_ALERT_TEXT"]
					if found:
						break
				alerttext = ''
				if "STURM" in self.WeatherInfo["DWD_ALERT_TEXT"].upper() or "BÖEN" in self.WeatherInfo["DWD_ALERT_TEXT"].upper() or "ORKAN" in self.WeatherInfo["DWD_ALERT_TEXT"].upper() or "WIND" in self.WeatherInfo["DWD_ALERT_TEXT"].upper():
					self.WeatherInfo["DWD_ALERT_EVENT"] = 'Wind'
					alerttext = 'Wind'
				if "SCHNEE" in self.WeatherInfo["DWD_ALERT_TEXT"].upper() or "NEUSCHNEE" in self.WeatherInfo["DWD_ALERT_TEXT"].upper():
					self.WeatherInfo["DWD_ALERT_EVENT"] = 'Schnee'
					if len(alerttext) > 1:
						alerttext = alerttext + ', Schnee'
					else:
						alerttext = 'Schnee'
				if "GEWITTER" in self.WeatherInfo["DWD_ALERT_TEXT"].upper() or "BLITZ" in self.WeatherInfo["DWD_ALERT_TEXT"].upper():
					self.WeatherInfo["DWD_ALERT_EVENT"] = 'Gewitter'
					if len(alerttext) > 1:
						alerttext = alerttext + ', Gewitter'
					else:
						alerttext = 'Gewitter'
				if "REGEN" in self.WeatherInfo["DWD_ALERT_TEXT"].upper():
					self.WeatherInfo["DWD_ALERT_EVENT"] = 'Regen'
					if len(alerttext) > 1:
						alerttext = alerttext + ', Regen'
					else:
						alerttext = 'Regen'
				if "NEBEL" in self.WeatherInfo["DWD_ALERT_TEXT"].upper():
					self.WeatherInfo["DWD_ALERT_EVENT"] = 'Nebel'
					if len(alerttext) > 1:
						alerttext = alerttext + ', Nebel'
					else:
						alerttext = 'Nebel'
				if "FROST" in self.WeatherInfo["DWD_ALERT_TEXT"].upper():
					self.WeatherInfo["DWD_ALERT_EVENT"] = 'Frost'
					if len(alerttext) > 1:
						alerttext = alerttext + ', Frost'
					else:
						alerttext = 'Frost'
				if "GLÄTTE" in self.WeatherInfo["DWD_ALERT_TEXT"].upper() or "GLATT" in self.WeatherInfo["DWD_ALERT_TEXT"].upper():
					self.WeatherInfo["DWD_ALERT_EVENT"] = 'Glätte'
					if len(alerttext) > 1:
						alerttext = alerttext + ', Glätte'
					else:
						alerttext = 'Glätte'
				if "HITZE" in self.WeatherInfo["DWD_ALERT_TEXT"].upper():
					self.WeatherInfo["DWD_ALERT_EVENT"] = 'Hitze'
					if len(alerttext) > 1:
						alerttext = alerttext + ', Hitze'
					else:
						alerttext = 'Hitze'
				self.WeatherInfo["DWD_ALERT_HEAD"] = 'Warnung vor ' + alerttext
				url = 'https://file.wetter.at/mowis/animationen/unwetterradar_01.jpg'
				self.downloadImage1(url, 'dwd_radar.jpg', 10)
				self.downloadImage1(url, 'dwd_radar.jpg', 10, '/usr/share/enigma2/VWeather3/')
			except Exception as ex:
				write_log("GotMeteoalarmAT : " + str(ex))

	#DWD 10-Tage-Vorhersage
	def GotDWD10DaysData(self, data=None):
		if data is not None:
			try:
				soup = BeautifulSoup(data,'html.parser')
				res = soup.find("div", {"id": "wettertext"})
				self.WeatherInfo["DWD_FORECAST_10DAYS"] = str(res).replace('<div id="wettertext">','').replace('<br/>\n<br/>','\n').replace('<br/><br/>','\n').replace('<br/>','\n').replace('\r\n','').replace('\r','').replace('<h3>','').replace('</h3>','').replace('</pre>','').replace('<pre style="font-family: sans-serif">','').replace('<strong>','').replace('</strong>','').replace('</div>','')
				write_log('DWD Vorhersage : ' + str(self.WeatherInfo["DWD_FORECAST_10DAYS"]))
			except Exception as ex:
				write_log("GotDWD10DaysData : " + str(ex))

	def downloadImage1(self, url, filename, timeout, path=picturepath):
		try:
			picfile = os.path.join(path, filename)
			r = requests.get(url, stream=True, timeout=timeout)
			if r.status_code == 200:
				with open(picfile, 'wb') as f:
					r.raw.decode_content = True
					shutil.copyfileobj(r.raw, f)
		except Exception as ex:
			write_log("download image: " + str(ex))

	def conImages(self):
		def downloadImage(url, filename, timeout):
			try:
				picfile = os.path.join(picturepath, filename)
				r = requests.get(url, stream=True, timeout=timeout)
				if r.status_code == 200:
					with open(picfile, 'wb') as f:
						r.raw.decode_content = True
						shutil.copyfileobj(r.raw, f)
			except Exception as ex:
				write_log("download image: " + str(ex))

		if config.plugins.VWeather3.NetworkMode.value != "Client":
			if isDWD:
				t = localtime()
				bio = (t.tm_hour > 10 and t.tm_hour < 13) or (t.tm_hour > 0 and t.tm_hour < 2) or not self.WeatherInfo["DWD_BIO_LIST"]
				pol = (t.tm_hour > 10 and t.tm_hour < 13) or (t.tm_hour > 0 and t.tm_hour < 2) or self.WeatherInfo["DWD_POLLEN_DATETIME"] == " "
				if config.plugins.VWeather3.DWD_ANIMATED_RADAR.value:
					if not os.path.exists(picturepath + 'dwd_radar'):
						os.makedirs(picturepath + 'dwd_radar')
					splitRadarImage(picturepath + 'dwd_radar/dwd_radar', 'http://www.wettergefahren.de/DWD/wetter/radar/Radarfilm_WEB_DL.gif')
				if isDWD_Wetter:
					url = 'https://www.dwd.de/DWD/wetter/aktuell/deutschland/bilder/wx_' + config.plugins.VWeather3.DWD_BL.value + '_akt.jpg'
					downloadImage(url, 'aktuell.jpg', 10)
					url = 'https://www.dwd.de/DWD/wetter/wv_allg/deutschland/bilder/vhs_' + config.plugins.VWeather3.DWD_BL.value + '_heutenacht.jpg'
					downloadImage(url, 'heutenacht.jpg', 10)
					url = 'https://www.dwd.de/DWD/wetter/wv_allg/deutschland/bilder/vhs_' + config.plugins.VWeather3.DWD_BL.value + '_morgenfrueh.jpg'
					downloadImage(url, 'morgenfrueh.jpg', 10)
					url = 'https://www.dwd.de/DWD/wetter/wv_allg/deutschland/bilder/vhs_' + config.plugins.VWeather3.DWD_BL.value + '_morgenspaet.jpg'
					downloadImage(url, 'morgenspaet.jpg', 10)
					url = 'https://www.dwd.de/DWD/wetter/wv_allg/deutschland/bilder/vhs_' + config.plugins.VWeather3.DWD_BL.value + '_uebermorgenfrueh.jpg'
					downloadImage(url, 'uebermorgenfrueh.jpg', 10)
					url = 'https://www.dwd.de/DWD/wetter/wv_allg/deutschland/bilder/vhs_' + config.plugins.VWeather3.DWD_BL.value + '_uebermorgenspaet.jpg'
					downloadImage(url, 'uebermorgenspaet.jpg', 10)
					url = 'https://www.dwd.de/DWD/wetter/wv_allg/deutschland/bilder/vhs_' + config.plugins.VWeather3.DWD_BL.value + '_tag4frueh.jpg'
					downloadImage(url, 'tag4frueh.jpg', 10)
					url = 'https://www.dwd.de/DWD/wetter/wv_allg/deutschland/bilder/vhs_' + config.plugins.VWeather3.DWD_BL.value + '_tag4spaet.jpg'
					downloadImage(url, 'tag4spaet.jpg', 10)
					url = 'https://www.dwd.de/DWD/wetter/wv_allg/deutschland/bilder/trendpic_' + config.plugins.VWeather3.DWD_BL.value + '.jpg'
					downloadImage(url, 'trend.jpg', 10)
				if not self.useImageTools:
					if isDWD_Bio:
						if bio:
							url = 'https://www.dwd.de/DWD/warnungen/medizin/biowetter/biowetter_h_0.png'
							downloadImage(url, 'bio_allg_heute.png', 10)
							url = 'https://www.dwd.de/DWD/warnungen/medizin/biowetter/biowetter_m_0.png'
							downloadImage(url, 'bio_allg_morgen.png', 10)
							url = 'https://www.dwd.de/DWD/warnungen/medizin/biowetter/biowetter_h_1.png'
							downloadImage(url, 'bio_asthma_heute.png', 10)
							url = 'https://www.dwd.de/DWD/warnungen/medizin/biowetter/biowetter_m_1.png'
							downloadImage(url, 'bio_asthma_morgen.png', 10)
							url = 'https://www.dwd.de/DWD/warnungen/medizin/biowetter/biowetter_h_2.png'
							downloadImage(url, 'bio_kreislauf_heute.png', 10)
							url = 'https://www.dwd.de/DWD/warnungen/medizin/biowetter/biowetter_m_2.png'
							downloadImage(url, 'bio_kreislauf_morgen.png', 10)
							url = 'https://www.dwd.de/DWD/warnungen/medizin/biowetter/biowetter_h_4.png'
							downloadImage(url, 'bio_rheuma_heute.png', 10)
							url = 'https://www.dwd.de/DWD/warnungen/medizin/biowetter/biowetter_m_4.png'
							downloadImage(url, 'bio_rheuma_morgen.png', 10)
					if isDWD_Pollen:
						if pol:
							url = 'https://www.dwd.de/DWD/warnungen/medizin/pollen/pollen_1_0.png'
							downloadImage(url, 'pollen_0_heute.png', 10)
							url = 'https://www.dwd.de/DWD/warnungen/medizin/pollen/pollen_2_0.png'
							downloadImage(url, 'pollen_0_morgen.png', 10)
							url = 'https://www.dwd.de/DWD/warnungen/medizin/pollen/pollen_1_1.png'
							downloadImage(url, 'pollen_1_heute.png', 10)
							url = 'https://www.dwd.de/DWD/warnungen/medizin/pollen/pollen_2_1.png'
							downloadImage(url, 'pollen_1_morgen.png', 10)
							url = 'https://www.dwd.de/DWD/warnungen/medizin/pollen/pollen_1_2.png'
							downloadImage(url, 'pollen_2_heute.png', 10)
							url = 'https://www.dwd.de/DWD/warnungen/medizin/pollen/pollen_2_2.png'
							downloadImage(url, 'pollen_2_morgen.png', 10)
							url = 'https://www.dwd.de/DWD/warnungen/medizin/pollen/pollen_1_3.png'
							downloadImage(url, 'pollen_3_heute.png', 10)
							url = 'https://www.dwd.de/DWD/warnungen/medizin/pollen/pollen_2_3.png'
							downloadImage(url, 'pollen_3_morgen.png', 10)
							url = 'https://www.dwd.de/DWD/warnungen/medizin/pollen/pollen_1_4.png'
							downloadImage(url, 'pollen_4_heute.png', 10)
							url = 'https://www.dwd.de/DWD/warnungen/medizin/pollen/pollen_2_4.png'
							downloadImage(url, 'pollen_4_morgen.png', 10)
							url = 'https://www.dwd.de/DWD/warnungen/medizin/pollen/pollen_1_5.png'
							downloadImage(url, 'pollen_5_heute.png', 10)
							url = 'https://www.dwd.de/DWD/warnungen/medizin/pollen/pollen_2_5.png'
							downloadImage(url, 'pollen_5_morgen.png', 10)
							url = 'https://www.dwd.de/DWD/warnungen/medizin/pollen/pollen_1_6.png'
							downloadImage(url, 'pollen_6_heute.png', 10)
							url = 'https://www.dwd.de/DWD/warnungen/medizin/pollen/pollen_2_6.png'
							downloadImage(url, 'pollen_6_morgen.png', 10)
							url = 'https://www.dwd.de/DWD/warnungen/medizin/pollen/pollen_1_7.png'
							downloadImage(url, 'pollen_7_heute.png', 10)
							url = 'https://www.dwd.de/DWD/warnungen/medizin/pollen/pollen_2_7.png'
							downloadImage(url, 'pollen_7_morgen.png', 10)
				else:
					try:
						if isDWD_Bio:
							if bio:
								convertOnlinePicture('https://www.dwd.de/DWD/warnungen/medizin/biowetter/biowetter_h_0.png', os.path.join(picturepath, 'bio_allg_heute.png'), self.ImageBackgroundColor, self.ImageRadius, 255-self.ImageRadiusTransparency, self.ImageTextColor, self.ImageTextColor)
								convertOnlinePicture('https://www.dwd.de/DWD/warnungen/medizin/biowetter/biowetter_m_0.png', os.path.join(picturepath, 'bio_allg_morgen.png'), self.ImageBackgroundColor, self.ImageRadius, 255-self.ImageRadiusTransparency, self.ImageTextColor, self.ImageTextColor)
								convertOnlinePicture('https://www.dwd.de/DWD/warnungen/medizin/biowetter/biowetter_h_1.png', os.path.join(picturepath, 'bio_asthma_heute.png'), self.ImageBackgroundColor, self.ImageRadius, 255-self.ImageRadiusTransparency, self.ImageTextColor, self.ImageTextColor)
								convertOnlinePicture('https://www.dwd.de/DWD/warnungen/medizin/biowetter/biowetter_m_1.png', os.path.join(picturepath, 'bio_asthma_morgen.png'), self.ImageBackgroundColor, self.ImageRadius, 255-self.ImageRadiusTransparency, self.ImageTextColor, self.ImageTextColor)
								convertOnlinePicture('https://www.dwd.de/DWD/warnungen/medizin/biowetter/biowetter_h_2.png', os.path.join(picturepath, 'bio_kreislauf_heute.png'), self.ImageBackgroundColor, self.ImageRadius, 255-self.ImageRadiusTransparency, self.ImageTextColor, self.ImageTextColor)
								convertOnlinePicture('https://www.dwd.de/DWD/warnungen/medizin/biowetter/biowetter_m_2.png', os.path.join(picturepath, 'bio_kreislauf_morgen.png'), self.ImageBackgroundColor, self.ImageRadius, 255-self.ImageRadiusTransparency, self.ImageTextColor, self.ImageTextColor)
								convertOnlinePicture('https://www.dwd.de/DWD/warnungen/medizin/biowetter/biowetter_h_4.png', os.path.join(picturepath, 'bio_rheuma_heute.png'), self.ImageBackgroundColor, self.ImageRadius, 255-self.ImageRadiusTransparency, self.ImageTextColor, self.ImageTextColor)
								convertOnlinePicture('https://www.dwd.de/DWD/warnungen/medizin/biowetter/biowetter_m_4.png', os.path.join(picturepath, 'bio_rheuma_morgen.png'), self.ImageBackgroundColor, self.ImageRadius, 255-self.ImageRadiusTransparency, self.ImageTextColor, self.ImageTextColor)
						if isDWD_Pollen:
							if pol:
								convertOnlinePicture('https://www.dwd.de/DWD/warnungen/medizin/pollen/pollen_1_0.png', os.path.join(picturepath, 'pollen_0_heute.png'), self.ImageBackgroundColor, self.ImageRadius, 255-self.ImageRadiusTransparency, self.ImageTextColor, self.ImageTextColor)
								convertOnlinePicture('https://www.dwd.de/DWD/warnungen/medizin/pollen/pollen_2_0.png', os.path.join(picturepath, 'pollen_0_morgen.png'), self.ImageBackgroundColor, self.ImageRadius, 255-self.ImageRadiusTransparency, self.ImageTextColor, self.ImageTextColor)
								convertOnlinePicture('https://www.dwd.de/DWD/warnungen/medizin/pollen/pollen_1_1.png', os.path.join(picturepath, 'pollen_1_heute.png'), self.ImageBackgroundColor, self.ImageRadius, 255-self.ImageRadiusTransparency, self.ImageTextColor, self.ImageTextColor)
								convertOnlinePicture('https://www.dwd.de/DWD/warnungen/medizin/pollen/pollen_2_1.png', os.path.join(picturepath, 'pollen_1_morgen.png'), self.ImageBackgroundColor, self.ImageRadius, 255-self.ImageRadiusTransparency, self.ImageTextColor, self.ImageTextColor)
								convertOnlinePicture('https://www.dwd.de/DWD/warnungen/medizin/pollen/pollen_1_2.png', os.path.join(picturepath, 'pollen_2_heute.png'), self.ImageBackgroundColor, self.ImageRadius, 255-self.ImageRadiusTransparency, self.ImageTextColor, self.ImageTextColor)
								convertOnlinePicture('https://www.dwd.de/DWD/warnungen/medizin/pollen/pollen_2_2.png', os.path.join(picturepath, 'pollen_2_morgen.png'), self.ImageBackgroundColor, self.ImageRadius, 255-self.ImageRadiusTransparency, self.ImageTextColor, self.ImageTextColor)
								convertOnlinePicture('https://www.dwd.de/DWD/warnungen/medizin/pollen/pollen_1_3.png', os.path.join(picturepath, 'pollen_3_heute.png'), self.ImageBackgroundColor, self.ImageRadius, 255-self.ImageRadiusTransparency, self.ImageTextColor, self.ImageTextColor)
								convertOnlinePicture('https://www.dwd.de/DWD/warnungen/medizin/pollen/pollen_2_3.png', os.path.join(picturepath, 'pollen_3_morgen.png'), self.ImageBackgroundColor, self.ImageRadius, 255-self.ImageRadiusTransparency, self.ImageTextColor, self.ImageTextColor)
								convertOnlinePicture('https://www.dwd.de/DWD/warnungen/medizin/pollen/pollen_1_4.png', os.path.join(picturepath, 'pollen_4_heute.png'), self.ImageBackgroundColor, self.ImageRadius, 255-self.ImageRadiusTransparency, self.ImageTextColor, self.ImageTextColor)
								convertOnlinePicture('https://www.dwd.de/DWD/warnungen/medizin/pollen/pollen_2_4.png', os.path.join(picturepath, 'pollen_4_morgen.png'), self.ImageBackgroundColor, self.ImageRadius, 255-self.ImageRadiusTransparency, self.ImageTextColor, self.ImageTextColor)
								convertOnlinePicture('https://www.dwd.de/DWD/warnungen/medizin/pollen/pollen_1_5.png', os.path.join(picturepath, 'pollen_5_heute.png'), self.ImageBackgroundColor, self.ImageRadius, 255-self.ImageRadiusTransparency, self.ImageTextColor, self.ImageTextColor)
								convertOnlinePicture('https://www.dwd.de/DWD/warnungen/medizin/pollen/pollen_2_5.png', os.path.join(picturepath, 'pollen_5_morgen.png'), self.ImageBackgroundColor, self.ImageRadius, 255-self.ImageRadiusTransparency, self.ImageTextColor, self.ImageTextColor)
								convertOnlinePicture('https://www.dwd.de/DWD/warnungen/medizin/pollen/pollen_1_6.png', os.path.join(picturepath, 'pollen_6_heute.png'), self.ImageBackgroundColor, self.ImageRadius, 255-self.ImageRadiusTransparency, self.ImageTextColor, self.ImageTextColor)
								convertOnlinePicture('https://www.dwd.de/DWD/warnungen/medizin/pollen/pollen_2_6.png', os.path.join(picturepath, 'pollen_6_morgen.png'), self.ImageBackgroundColor, self.ImageRadius, 255-self.ImageRadiusTransparency, self.ImageTextColor, self.ImageTextColor)
								convertOnlinePicture('https://www.dwd.de/DWD/warnungen/medizin/pollen/pollen_1_7.png', os.path.join(picturepath, 'pollen_7_heute.png'), self.ImageBackgroundColor, self.ImageRadius, 255-self.ImageRadiusTransparency, self.ImageTextColor, self.ImageTextColor)
								convertOnlinePicture('https://www.dwd.de/DWD/warnungen/medizin/pollen/pollen_2_7.png', os.path.join(picturepath, 'pollen_7_morgen.png'), self.ImageBackgroundColor, self.ImageRadius, 255-self.ImageRadiusTransparency, self.ImageTextColor, self.ImageTextColor)
					except Exception as ex:
						del self.conimgs
		del self.conimgs

	def moonphase(self, sourcepath=None):
		picon = '1'
		ptext = 'Vollmond'
		# constants
		syn_moon_month = 29.530589 									# synodal length of moon cycle 
		hist_fullmoon = 2018,9,25,6,1,36,0,0,1 						# base full-moon as struct time 
		moon_time = mktime(hist_fullmoon) 							# base full-moon - seconds since epoch 
		hist_fullmoon_days = moon_time/86400 						# base full-moon - days since epoch 
		now_days = mktime(localtime())/86400 						# days since eval 
		days_since_hist_fullmoon = now_days - hist_fullmoon_days    # difference in days between base fullmoon and now 
		full_moons_since = days_since_hist_fullmoon/syn_moon_month  # Number of full-moons that have passed since base full-moon 
		phase = round(full_moons_since,2) 							# rounded to 2 digits 
		phase = (phase-int(phase))									# trailing rest = % moon-phase 

		# calculate moon phase
		if phase == 0: phase=1
		if phase < 0.25:
			ptext="abnehmender Mond" 
		elif phase == 0.25:
			ptext="abnehmender Halbmond" 
		elif 0.25 < phase < 0.50:
			ptext="abnehmende Sichel" 
		elif phase == 0.50:
			ptext="Neumond" 
		elif 0.50 < phase < 0.75:
			ptext="zunehmende Sichel" 
		elif phase == 0.75:
			ptext="zunehmender Halbmond" 
		elif 0.75 < phase < 1:
			ptext="zunehmender Mond" 
		elif phase == 1:
			ptext = "Vollmond"
			
		hmoonA = float(pi/2)                            # area of unit circle/2
		# calculate percentage of moon illuminated
		if phase < 0.5:
				s = cos(phase * pi * 2)
				ellipse = s * 1 * pi                    # Ellipsenfäche = Produkt der beiden Halbachsen * Pi 
				hEllA = ellipse / 2                     # Ellipse Area/2 (major half axis * minor half axis * pi)/2
				illA = hmoonA + hEllA                   # illuminated area of moon = Half moon area plus half Ellipse
		else:
				s = -cos(phase * pi *2)                 # minor half axis of ellipse
				ellipse = s * 1 * pi
				hEllA = ellipse / 2                     # Ellipse Area/2 (major half axis * minor half axis)/2
				illA = hmoonA - hEllA                   # illuminated area = Half moon area minus half Ellipse Area

		illumperc =  illA / pi * 100                    # illuminated area relative to full moon area (based on unit circle r=1)	
		illumperc = round(illumperc,1)
			
		if phase > 0 and illumperc > 95:
			picon="095" 
		if phase > 0.07 and illumperc > 90:
			picon="090" 
		if phase > 0.10 and illumperc > 85:
			picon="085" 
		if phase > 0.12 and illumperc > 80:
			picon="080" 
		if phase > 0.14 and illumperc > 75:
			picon="075" 
		if phase > 0.16 and illumperc > 70:
			picon="070" 
		if phase > 0.18 and illumperc > 65:
			picon="065" 
		if phase > 0.20 and illumperc > 60:
			picon="060" 
		if phase > 0.21 and illumperc > 55:
			picon="055" 
		if phase > 0.23 and illumperc > 50:
			picon="050" 
		if phase > 0.24 and illumperc > 45:
			picon="045" 
		if phase > 0.26 and illumperc > 40:
			picon="040" 
		if phase > 0.28 and illumperc > 35:
			picon="035" 
		if phase > 0.29 and illumperc > 30:
			picon="030" 
		if phase > 0.31 and illumperc > 25:
			picon="025" 
		if phase > 0.33 and illumperc > 20:
			picon="020" 
		if phase > 0.35 and illumperc > 15:
			picon="015" 
		if phase > 0.37 and illumperc > 10:
			picon="010" 
		if phase > 0.39 and illumperc > 5:
			picon="05" 
		if phase > 0.42 and illumperc >= 0:
			picon="1" 
		if phase > 0.50 and illumperc > 0:
			picon="5" 
		if phase > 0.57 and illumperc > 5:
			picon="10" 
		if phase > 0.60 and illumperc > 10:
			picon="15" 
		if phase > 0.62 and illumperc > 15:
			picon="20" 
		if phase > 0.64 and illumperc > 20:
			picon="25" 
		if phase > 0.66 and illumperc > 25:
			picon="30" 
		if phase > 0.68 and illumperc > 30:
			picon="35" 
		if phase > 0.70 and illumperc > 35:
			picon="40" 
		if phase > 0.71 and illumperc > 40:
			picon="45" 
		if phase > 0.73 and illumperc > 45:
			picon="50" 
		if phase > 0.75 and illumperc > 50:
			picon="55" 
		if phase > 0.76 and illumperc > 55:
			picon="60" 
		if phase > 0.78 and illumperc > 60:
			picon="65" 
		if phase > 0.79 and illumperc > 65:
			picon="70" 
		if phase > 0.81 and illumperc > 70:
			picon="75" 
		if phase > 0.83 and illumperc > 75:
			picon="80" 
		if phase > 0.85 and illumperc > 80:
			picon="85" 
		if phase > 0.87 and illumperc > 85:
			picon="90" 
		if phase > 0.89 and illumperc > 90:
			picon="95" 
		if phase > 0.92 and illumperc > 95:
			picon="100"

		#Versuche alternatives Icon zu finden
		try:
			if sourcepath:
				if os.path.isdir(sourcepath):
					if str(sourcepath).endswith('/'):
						self.Path = sourcepath
					else:
						self.Path = sourcepath + '/'
				else:
					if str(sourcepath).endswith('/'):
						self.Path = '/usr/share/enigma2/' + sourcepath
					else:
						self.Path = '/usr/share/enigma2/' + sourcepath + '/'
				path = str(self.Path).replace('//','/')
				if os.path.isdir(path):
					iconlist = glob.glob(path + '*.png')
					for filename in iconlist:
						if '010.png' in filename:
							write_log('return default moonicon')
							return ptext, picon
					for n, i in enumerate(iconlist):
						iconlist[n] = int(iconlist[n].replace(path, '').replace('.png', ''))
					write_log('Anzahl MondIcons = ' + str(len(iconlist)))
					nearest = min(iconlist, key=lambda v: abs((phase*100)-v))
					write_log('found nearest Picon' + str(phase) + ' - ' + str(nearest))
					return ptext, str(nearest)
		except Exception as ex:
			write_log('Fehler in getalternativeicon : ' + str(ex))
			return ptext, picon
		return ptext, picon

	def get_timezonedelta(self, zone, ts):
		try:
			from dateutil import tz

			local = tz.tzlocal()
			tz = tz.gettz(str(zone))

			ts = datetime.datetime.fromtimestamp(int(ts))
			ts_local = ts.replace(tzinfo=local)
			ts_tz = ts.replace(tzinfo=tz)

			write_log("timezonedelta : " + str((ts_local - ts_tz).total_seconds()))
			return (ts_local - ts_tz).total_seconds()
		except Exception as ex:
			write_log("convert timezone: " + str(ex))
			return 0

	def ConvertTime(self, time):
		if config.plugins.VWeather3.Units.value == "imperial":
			parts = time.split()
			time3, time4 = parts[0], parts[1]
			parts = time3.split(":")
			time1, time2 = parts[0], parts[1]
			if len(time1) < 2:
				time1 = "0" + time1
			if len(time2) < 2:
				time2 = "0" + time2
			if time4 == "am":
				time = str(time1) + ":" + str(time2) + str(time4.replace("am", " AM"))
			else:
				time = str(time1) + ":" + str(time2) + str(time4.replace("pm", " PM"))
		else:
			parts = time.split()
			time3, time4 = parts[0], parts[1]
			parts = time3.split(":")
			time1, time2 = parts[0], parts[1]
			if len(time1) < 2:
				time1 = "0" + time1
			if len(time2) < 2:
				time2 = "0" + time2
			if time4 == "am":
				time = str(time1) + ":" + str(time2) + str(time4.replace("am", " Uhr"))
			else:
				time1 = int(time1) + 12
				time = str(time1) + ":" + str(time2) + str(time4.replace("pm", " Uhr"))
		return str(time)

	def ConvertRise(self, rise):
		if str(rise) == '-1':
				rise = "<<"
		elif str(rise) == '1':
				rise = ">>"
		elif str(rise) == '0':
				rise = "="
		else:
				rise = ""
		return str(rise)

	def ConvertRegion(self, region):
		if region == " BW" or region == " Baden-Wurttemberg":
			region = "Baden-Württemberg"
		elif region == " BY" or region == " Bavaria":
			region = "Bayern"
		elif region == " BE" or region == " Berlin":
			region = "Berlin"
		elif region == " BB" or region == " Brandenburg":
			region = "Brandenburg"
		elif region == " HB" or region == " Bremen":
			region = "Bremen"
		elif region == " HH" or region == " Hamburg":
			region = "Hamburg"
		elif region == " HE" or region == " Hesse":
			region = "Hessen"
		elif region == " MV" or region == " Mecklenburg-Vorpommern":
			region = "Mecklenburg-Vorpommern"
		elif region == " NI" or region == " Lower Saxony":
			region = "Niedersachsen"
		elif region == " NW" or region == " North Rhine-Westphalia":
			region = "Nordrhein-Westfalen"
		elif region == " RP" or region == " Rhineland-Palatinate":
			region = "Rheinland-Pfalz"
		elif region == " SL" or region == " Saarland":
			region = "Saarland"
		elif region == " SN" or region == " Saxony":
			region = "Sachsen"
		elif region == " ST" or region == " Saxony-Anhalt":
			region = "Sachsen-Anhalt"
		elif region == " SH" or region == " Schleswig-Holstein":
			region = "Schleswig-Holstein"
		elif region == " TH" or region == " Thuringia":
			region = "Thüringen"
		return str(region)

	def ConvertCondition(self, code):
		code = int(code)
	#	Keine Daten
		condition = "("
	#	0 Tornado, 1 Tropical Storm, 2 Hurricane
		if code == 0 or code == 1 or code == 2:
			condition = "F"
	#	3 Severe Thunderstorms
		elif code == 3:
			condition = "0"
	#	4 Thunderstorms
		elif code == 4:
			condition = "Z"
	#	5 Mixed Rain and Snow, 6 Mixed Rain and Sleet, 35 Mixed Rain and Hail
		elif code == 5  or code == 6 or code == 35:
			condition = "W"
	#	8 Freezing Drizzle, 9 Drizzle, 10 Freezing Rain, 18 Sleet
		elif code == 8 or code == 9 or code == 10 or code == 18:
			condition = "U"
	#	17 Hail
		elif code == 17:
			condition = "V"
	#	25 Cold
		elif code == 25:
			condition = "G"
	#	11 Showers, 12 Rain
		elif code == 11 or code == 12 or code == 7:
			condition = "R"
	#	39 Scattered Showers, 40 Scattered Showers
		elif code == 39 or code == 40:
			condition = "Q"
	#	7 Snow Sleet, 13 Snow Flurries, 14 Light Snow Showers, 15 Blowing Snow, 16 Snow
	#	41 Heavy Snow, 42 Scattered Snow Showers, 43 Heavy Snow, 46 Snow Showers
		elif code == 13 or code == 14 or code == 15 or code == 16 or code == 41 or code == 42 or code == 43 or code == 46:
			condition = "X"
	#	19 Dusty, 22 Smoky
		elif code == 19 or code == 22:
			condition = "E"
	#	20 Foggy, 21 Hazel
		elif code == 20 or code == 21:
			condition = "M"
	#	23 Breezy, 24 Windy
		elif code == 23 or code == 24:
			condition = "F"
	#	26 Cloudy, 27 Mostly Cloudy (night), 28 Mostly Cloudy (day)
		elif code == 26 or code == 27 or code == 28:
			condition = "Y"
	#	29 Partly Cloudy (night)
		elif code == 29:
			condition = "I"
	#	30 Partly Cloudy (day)
		elif code == 30:
			condition = "H"
	#	44 Partly Cloudy
		elif code == 44:
			condition = "N"
	#	31 Clear (night), 33 Mostly Clear (night)
		elif code == 31 or code == 33:
			condition = "C"
	#	32 Sunny (day), 34 Mostly Sunny (day), 36 Hot
		elif code == 32 or code == 34 or code == 36:
			condition = "B"
	#	37 Isolated Thunderstorms, 38 Isolated Thunderstorms
		elif code == 37 or code == 38:
			condition = "O"
	#	45 Thundershowers, 47 Scattered Thundershowers
		elif code == 45 or code == 47:
			condition = "P"
	#	3200 N/A
		else:
			condition = ")"
		return str(condition)

	# ... called for Yahoo weather description, always in english from API
	def ConvertInfo(self, text):
		return str(_(text))


	def ConvertDirectionShort(self, direction):
		dir = int(direction)
		if dir >= 0 and dir <= 20:
			direction = _("N")
		elif dir >= 21 and dir <= 35:
			direction = _("N-NE")
		elif dir >= 36 and dir <= 55:
			direction = _("NE")
		elif dir >= 56 and dir <= 70:
			direction = _("E-NE")
		elif dir >= 71 and dir <= 110:
			direction = _("E")
		elif dir >= 111 and dir <= 125:
			direction = _("E-SE")
		elif dir >= 126 and dir <= 145:
			direction = _("SE")
		elif dir >= 146 and dir <= 160:
			direction = _("S-SE")
		elif dir >= 161 and dir <= 200:
			direction = _("S")
		elif dir >= 201 and dir <= 215:
			direction = _("S-SW")
		elif dir >= 216 and dir <= 235:
			direction = _("SW")
		elif dir >= 236 and dir <= 250:
			direction = _("W-SW")
		elif dir >= 251 and dir <= 290:
			direction = _("W")
		elif dir >= 291 and dir <= 305:
			direction = _("W-NW")
		elif dir >= 306 and dir <= 325:
			direction = _("NW")
		elif dir >= 326 and dir <= 340:
			direction = _("N-NW")
		elif dir >= 341 and dir <= 360:
			direction = _("N")
		else:
			direction = _("N/A")
		return str(direction)

	def ConvertDirectionLong(self, direction):
		dir = int(direction)
		if dir >= 0 and dir <= 20:
			direction = _("North")
		elif dir >= 21 and dir <= 35:
			direction = _("North-Northeast")
		elif dir >= 36 and dir <= 55:
			direction = _("Northeast")
		elif dir >= 56 and dir <= 70:
			direction = _("East-Northeast")
		elif dir >= 71 and dir <= 110:
			direction = _("East")
		elif dir >= 111 and dir <= 125:
			direction = _("East-Southeast")
		elif dir >= 126 and dir <= 145:
			direction = _("Southeast")
		elif dir >= 146 and dir <= 160:
			direction = _("South-Southeast")
		elif dir >= 161 and dir <= 200:
			direction = _("South")
		elif dir >= 201 and dir <= 215:
			direction = _("South-Southwest")
		elif dir >= 216 and dir <= 235:
			direction = _("Southwest")
		elif dir >= 236 and dir <= 250:
			direction = _("West-Southwest")
		elif dir >= 251 and dir <= 290:
			direction = _("West")
		elif dir >= 291 and dir <= 305:
			direction = _("West-Northwest")
		elif dir >= 306 and dir <= 325:
			direction = _("Northwest")
		elif dir >= 326 and dir <= 340:
			direction = _("North-Northwest")
		elif dir >= 341 and dir <= 360:
			direction = _("North")
		else:
			direction = _("N/A")

		return str(direction)

	def convertOWMIconName(self, IconName):
		if IconName == "01d":
			return "32"
		elif IconName == "02d":
			return "34"
		elif IconName == "03d":
			return "28"
		elif IconName == "04d":
			return "26"
		elif IconName == "05d":
			return "39"
		elif IconName == "06d":
			return "37"
		elif IconName == "07d":
			return "5"
		elif IconName == "08d":
			return "13"
		elif IconName == "09d":
			return "18"
		elif IconName == "10d":
			return "39"
		elif IconName == "11d":
			return "38"
		elif IconName == "12d":
			return "5"
		elif IconName == "13d":
			return "13"
		elif IconName == "14d":
			return "17"
		elif IconName == "15d":
			return "19"
		elif IconName == "20d":
			return "37"
		elif IconName == "21d":
			return "37"
		elif IconName == "22d":
			return "3"
		elif IconName == "23d":
			return "5"
		elif IconName == "30d":
			return "38"
		elif IconName == "31d":
			return "38"
		elif IconName == "32d":
			return "5"
		elif IconName == "33d":
			return "13"
		elif IconName == "34d":
			return "14"
		elif IconName == "40d":
			return "39"
		elif IconName == "46d":
			return "11"
		elif IconName == "47d":
			return "11"
		elif IconName == "48d":
			return "5"
		elif IconName == "49d":
			return "6"
		elif IconName == "50d":
			return "19"
		elif IconName == "01n":
			return "32"
		elif IconName == "02n":
			return "34"
		elif IconName == "03n":
			return "28"
		elif IconName == "04n":
			return "26"
		elif IconName == "05n":
			return "38"
		elif IconName == "06n":
			return "47"
		elif IconName == "07n":
			return "46"
		elif IconName == "08n":
			return "46"
		elif IconName == "09n":
			return "45"
		elif IconName == "10n":
			return "11"
		elif IconName == "11n":
			return "47"
		elif IconName == "13n":
			return "46"
		elif IconName == "40n":
			return "45"
		elif IconName == "41n":
			return "46"
		elif IconName == "50n":
			return "19"
		else:
			write_log("fehlender IconName : " + str(IconName))
			return "3200"

	def convertcurrentOWMIconName(self, IconName):
		if IconName == "01d":
			return "32"
		elif IconName == "02d":
			return "34"
		elif IconName == "03d":
			return "28"
		elif IconName == "04d":
			return "26"
		elif IconName == "05d":
			return "39"
		elif IconName == "06d":
			return "37"
		elif IconName == "07d":
			return "5"
		elif IconName == "08d":
			return "13"
		elif IconName == "09d":
			return "18"
		elif IconName == "10d":
			return "39"
		elif IconName == "11d":
			return "38"
		elif IconName == "12d":
			return "5"
		elif IconName == "13d":
			return "13"
		elif IconName == "14d":
			return "17"
		elif IconName == "15d":
			return "19"
		elif IconName == "20d":
			return "37"
		elif IconName == "21d":
			return "37"
		elif IconName == "22d":
			return "3"
		elif IconName == "23d":
			return "5"
		elif IconName == "30d":
			return "38"
		elif IconName == "31d":
			return "38"
		elif IconName == "32d":
			return "5"
		elif IconName == "33d":
			return "13"
		elif IconName == "34d":
			return "14"
		elif IconName == "40d":
			return "39"
		elif IconName == "46d":
			return "11"
		elif IconName == "47d":
			return "11"
		elif IconName == "48d":
			return "5"
		elif IconName == "49d":
			return "6"
		elif IconName == "50d":
			return "19"
		elif IconName == "01n":
			return "31"
		elif IconName == "02n":
			return "33"
		elif IconName == "03n":
			return "29"
		elif IconName == "04n":
			return "26"
		elif IconName == "05n":
			return "38"
		elif IconName == "06n":
			return "47"
		elif IconName == "07n":
			return "46"
		elif IconName == "08n":
			return "46"
		elif IconName == "09n":
			return "45"
		elif IconName == "10n":
			return "11"
		elif IconName == "11n":
			return "47"
		elif IconName == "13n":
			return "46"
		elif IconName == "40n":
			return "45"
		elif IconName == "41n":
			return "46"
		elif IconName == "50n":
			return "19"
		else:
			write_log("fehlender IconName : " + str(IconName))
			return "3200"

	def convertIconName(self, IconName):
		if IconName == "sleet":
			return "7"
		elif IconName == "wind":
			return "23"
		elif IconName == "fog":
			return "20"
		elif IconName == "partly-cloudy-night":
			return "30"
		elif IconName == "cloudy":
			return "26"
		elif IconName == "clear-night":
			return "32"
		elif IconName == "clear-day":
			return "32"
		elif IconName == "partly-cloudy-day":
			return "30"
		elif IconName == "rain":
			return "12"
		elif IconName == "snow":
			return "14"
		else:
			write_log("fehlender IconName : " + str(IconName))
			return "3200"

	def convertcurrentIconName(self, IconName):
		if IconName == "sleet":
			return "7"
		elif IconName == "wind":
			return "23"
		elif IconName == "fog":
			return "20"
		elif IconName == "partly-cloudy-night":
			return "29"
		elif IconName == "cloudy":
			return "26"
		elif IconName == "clear-night":
			return "31"
		elif IconName == "clear-day":
			return "32"
		elif IconName == "partly-cloudy-day":
			return "30"
		elif IconName == "rain":
			return "12"
		elif IconName == "snow":
			return "14"
		else:
			write_log("fehlender IconName : " + str(IconName))
			return "3200"

	# ... called for DarkSky weather description, actually the icon name ist used here 
	def convertWeatherText(self, WeatherText):
		return str(_(WeatherText.replace('-',' ')))

	def convertAstroSun(self, val):
		value = datetime.datetime.fromtimestamp(int(val))
		return value.strftime('%H:%M')

	def convertCurrentDate(self, val):
		value = datetime.datetime.fromtimestamp(int((datetime.datetime.fromtimestamp(int(val)) - datetime.datetime(1970,1,1)).total_seconds()))
		if config.plugins.VWeather3.DateFormat.value == "kurz":
			return value.strftime('%d.%m.')
		else:
			return value.strftime('%d.%m.%Y')

	def convertCurrentDateLong(self, val):
		value = datetime.datetime.fromtimestamp(int((datetime.datetime.fromtimestamp(int(val)) - datetime.datetime(1970,1,1)).total_seconds()))
		return value.strftime('%d.%m.%Y')

	def convertCurrentTime(self, val):
		value = datetime.datetime.fromtimestamp(int(val))
		return value.strftime('%H:%M:%S')

	def convertCurrentDay(self, val):
		svalue = datetime.datetime.fromtimestamp(int((datetime.datetime.fromtimestamp(int(val)) - datetime.datetime(1970,1,1)).total_seconds()))
		value = int(svalue.strftime("%w"))
		if config.plugins.VWeather3.DayFormat.value == "kurz":
			return swdays_en[value]
		else:
			return wdays_en[value]

	def convertDateTime(self, val):
		value = datetime.datetime.fromtimestamp(int((datetime.datetime.fromtimestamp(int(val)) - datetime.datetime(1970,1,1)).total_seconds()))
		return value.strftime('%d.%m.%Y %H:%M')

	def ConvertTemp(self, unit):
		if config.plugins.VWeather3.spaces.value:
			if config.plugins.VWeather3.Units.value == "imperial":
				return " °F"
			if config.plugins.VWeather3.Units.value == "metric":
				return " °C"
			else:
				return " °K"
		else:
			if config.plugins.VWeather3.Units.value == "imperial":
				return "°F"
			if config.plugins.VWeather3.Units.value == "metric":
				return "°C"
			else:
				return "°K"

	def ConvertSpeed(self, unit):
		if config.plugins.VWeather3.Units.value == "imperial":
			return " mpH"
		if config.plugins.VWeather3.Units.value == "metric":
			return " km/h"
		else:
			return " mpH"

	def ConvertVisibility(self, unit):
		if config.plugins.VWeather3.Units.value == "imperial":
			return " miles"
		if config.plugins.VWeather3.Units.value == "metric":
			return " km"
		else:
			return " miles"

	def ConvertCityName(self, name):
		if name == "Munich":
			return "München"
		elif name == "Cologne":
			return "Köln"
		else:
			return str(name)

	def ConvertIconCode(self, IconName):
		if IconName == "01d":
			return "B"
		elif IconName == "02d":
			return "H"
		elif IconName == "03d":
			return "H"
		elif IconName == "04d":
			return "N"
		elif IconName == "05d":
			return "Q"
		elif IconName == "06d":
			return "O"
		elif IconName == "07d":
			return "U"
		elif IconName == "08d":
			return "W"
		elif IconName == "09d":
			return "X"
		elif IconName == "10d":
			return "Q"
		elif IconName == "11d":
			return "S"
		elif IconName == "12d":
			return "X"
		elif IconName == "13d":
			return "W"
		elif IconName == "14d":
			return "O"
		elif IconName == "15d":
			return "N"
		elif IconName == "20d":
			return "E"
		elif IconName == "21d":
			return "E"
		elif IconName == "22d":
			return "Z"
		elif IconName == "23d":
			return "T"
		elif IconName == "30d":
			return "S"
		elif IconName == "31d":
			return "S"
		elif IconName == "32d":
			return "T"
		elif IconName == "33d":
			return "W"
		elif IconName == "34d":
			return "W"
		elif IconName == "40d":
			return "H"
		elif IconName == "46d":
			return "Q"
		elif IconName == "47d":
			return "Q"
		elif IconName == "48d":
			return "U"
		elif IconName == "49d":
			return "T"
		elif IconName == "50d":
			return "M"
		elif IconName == "01n":
			return "C"
		elif IconName == "02n":
			return "I"
		elif IconName == "03n":
			return "I"
		elif IconName == "04n":
			return "N"
		elif IconName == "05n":
			return "O"
		elif IconName == "06n":
			return "I"
		elif IconName == "07n":
			return "U"
		elif IconName == "08n":
			return "U"
		elif IconName == "09n":
			return "Q"
		elif IconName == "10n":
			return "U"
		elif IconName == "11n":
			return "I"
		elif IconName == "13n":
			return "U"
		elif IconName == "40n":
			return "Q"
		elif IconName == "41n":
			return "U"
		elif IconName == "sleet":
			return "W"
		elif IconName == "wind":
			return "F"
		elif IconName == "fog":
			return "M"
		elif IconName == "partly-cloudy-night":
			return "I"
		elif IconName == "cloudy":
			return "H"
		elif IconName == "clear-night":
			return "C"
		elif IconName == "clear-day":
			return "B"
		elif IconName == "partly-cloudy-day":
			return "H"
		elif IconName == "rain":
			return "X"
		elif IconName == "snow":
			return "W"
		else:
			return ")"

	def get_most_element(self, lst):
		return max(set(lst), key=lst.count)
