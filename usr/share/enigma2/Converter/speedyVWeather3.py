# -*- encoding: utf-8 -*-
####################################################################################################
####################################################################################################
#                                                                                                  #
#	Weatherconverter for VU+                                                                       #
#	Coded by tsiegel (c) 2019                                                                      #
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
####################################################################################################
####################################################################################################

from Components.Converter.Converter import Converter
from Components.Element import cached
from Components.config import config, ConfigSubsection, ConfigNumber, ConfigSelection, ConfigYesNo, ConfigText, ConfigInteger
from Screens.MessageBox import MessageBox
from Tools import Notifications
from twisted.web.client import getPage
from operator import itemgetter
from enigma import eTimer
from time import time, localtime, mktime, strftime
from datetime import timedelta, datetime
import datetime
import json
import os


config.plugins.VWeather3 = ConfigSubsection()
config.plugins.VWeather3.refreshInterval = ConfigInteger(default = 60, limits = (30, 300))
config.plugins.VWeather3.Log = ConfigYesNo(default = True)
config.plugins.VWeather3.Provider = ConfigSelection(default = "Darksky", choices = [("Darksky", _("Darksky")),("OpenWeatherMap", _("OpenWeatherMap"))])
config.plugins.VWeather3.CountryCode = ConfigSelection(default = "de", choices = [("bg", _("Bulgarian")),("ca", _("Catalan")),("cz", _("Czech")),("de", _("Deutschland")),("el", _("Greek")),("en", _("English")),("fi", _("Finnish")),("fr", _("Frensh")),("it", _("Italien")),("nl", _("Dutch")),("pl", _("Polish")),("es", _("Spanish")),("tr", _("Turkish"))])# Ländercode nach ISO-3166 Alpha-2
config.plugins.VWeather3.Units = ConfigSelection(default = "metric", choices = [("metric", _("Celsius")),("imperial", _("Fahrenheit")),("", _("Kelvin"))])      # metric = °Celsius ; imperial = Fahrenheit ; default = Kelvin
config.plugins.VWeather3.numbers = ConfigInteger(default = 1, limits = (0, 2))

config.plugins.VWeather3.Darksky_apikey = ConfigText(default = "9764f65bf6e4fa4418fdd656f98abc48")
config.plugins.VWeather3.Darksky_lat = ConfigText(default = "51.0541726")
config.plugins.VWeather3.Darksky_lon = ConfigText(default = "12.3638229")
config.plugins.VWeather3.Darksky_alerts = ConfigYesNo(default = False)

config.plugins.VWeather3.OpenWeatherMap_apikey = ConfigText(default = "1234567890")
config.plugins.VWeather3.OpenWeatherMap_geolocation = ConfigSelection(default = "Ort", choices = [("PLZ", _("PLZ")),("Ort", _("Ort"))])
config.plugins.VWeather3.OpenWeatherMap_zipcode = ConfigText(default = "40880")
config.plugins.VWeather3.OpenWeatherMap_place = ConfigText(default = "Ratingen")

weather_data = None
wdays = ["Sonntag","Montag","Dienstag","Mittwoch","Donnerstag","Freitag","Samstag"]
swdays = ["So","Mo","Di","Mi","Do","Fr","Sa"]
wdays_en = ["Sunday","Monday","Tuesday","Wednesday","Thursday","Friday","Saturday"]
swdays_en = ["Sun","Mon","Tue","Wed","Thu","Fri","Sat"]

log = config.plugins.VWeather3.Log.value
numbers = '.' + str(config.plugins.VWeather3.numbers.value) + 'f'

def write_log(svalue):
	if log:
		t = localtime()
		logtime = '%02d:%02d:%02d' % (t.tm_hour, t.tm_min, t.tm_sec)
		VWeather3_log = open('/tmp/VWeather3.log',"a")
		VWeather3_log.write(str(logtime) + " - " + str(svalue) + "\n")
		VWeather3_log.close()


class speedyVWeather3(Converter, object):
	def __init__(self, type):
		Converter.__init__(self, type)
		global weather_data
		if weather_data is None:
			weather_data = WeatherData()
		self.type = type

	@cached
	def getText(self):
		WeatherInfo = weather_data.WeatherInfo
		if self.type == "alerts":
			return WeatherInfo[self.type]
		if self.type == "provider":
			return WeatherInfo[self.type]
		if self.type == "currentLocation":
			return WeatherInfo[self.type]
		elif self.type == "currentCountry":
			return WeatherInfo[self.type]
		elif self.type == "currentRegion":
			return WeatherInfo[self.type]
		elif self.type == "windChill":
			return WeatherInfo[self.type]
		elif self.type == "windDirectionShort":
			return WeatherInfo[self.type]
		elif self.type == "windDirectionLong":
			return WeatherInfo[self.type]
		elif self.type == "windSpeed":
			return WeatherInfo[self.type]
		elif self.type == "atmoHumidity":
			return WeatherInfo[self.type]
		elif self.type == "atmoPressure":
			return WeatherInfo[self.type]
		elif self.type == "atmoRising":
			return WeatherInfo[self.type]
		elif self.type == "atmoVisibility":
			return WeatherInfo[self.type]
		elif self.type == "astroSunrise":
			return WeatherInfo[self.type]
		elif self.type == "astroSunset":
			return WeatherInfo[self.type]
		elif self.type == "geoData":
			return WeatherInfo[self.type]
		elif self.type == "geoLat":
			return WeatherInfo[self.type]
		elif self.type == "geoLong":
			return WeatherInfo[self.type]
		elif self.type == "downloadDate":
			return WeatherInfo[self.type]
		elif self.type == "downloadTime":
			return WeatherInfo[self.type]
		elif self.type == "currentWeatherTemp":
			return WeatherInfo[self.type]
		elif self.type == "currentWeatherText":
			return WeatherInfo[self.type]
		elif self.type == "currentWeatherCode":
			return WeatherInfo[self.type]
		elif self.type == "currentWeatherPicon":
			return WeatherInfo[self.type]
		elif self.type == "forecastTodayCode":
			return WeatherInfo[self.type]
		elif self.type == "forecastTodayDay":
			return WeatherInfo[self.type]
		elif self.type == "forecastTodayDate":
			return WeatherInfo[self.type]
		elif self.type == "forecastTodayTempMin":
			return WeatherInfo[self.type]
		elif self.type == "forecastTodayTempMax":
			return WeatherInfo[self.type]
		elif self.type == "forecastTodayText":
			return WeatherInfo[self.type]
		elif self.type == "forecastTodayPicon":
			return WeatherInfo[self.type]
		elif self.type == "forecastTomorrowCode":
			return WeatherInfo[self.type]
		elif self.type == "forecastTomorrowDay":
			return WeatherInfo[self.type]
		elif self.type == "forecastTomorrowDate":
			return WeatherInfo[self.type]
		elif self.type == "forecastTomorrowTempMin":
			return WeatherInfo[self.type]
		elif self.type == "forecastTomorrowTempMax":
			return WeatherInfo[self.type]
		elif self.type == "forecastTomorrowText":
			return WeatherInfo[self.type]
		elif self.type == "forecastTomorrowPicon":
			return WeatherInfo[self.type]
		elif self.type == "forecastTomorrow1Code":
			return WeatherInfo[self.type]
		elif self.type == "forecastTomorrow1Day":
			return WeatherInfo[self.type]
		elif self.type == "forecastTomorrow1Date":
			return WeatherInfo[self.type]
		elif self.type == "forecastTomorrow1TempMin":
			return WeatherInfo[self.type]
		elif self.type == "forecastTomorrow1TempMax":
			return WeatherInfo[self.type]
		elif self.type == "forecastTomorrow1Text":
			return WeatherInfo[self.type]
		elif self.type == "forecastTomorrow1Picon":
			return WeatherInfo[self.type]
		elif self.type == "forecastTomorrow2Code":
			return WeatherInfo[self.type]
		elif self.type == "forecastTomorrow2Day":
			return WeatherInfo[self.type]
		elif self.type == "forecastTomorrow2Date":
			return WeatherInfo[self.type]
		elif self.type == "forecastTomorrow2TempMin":
			return WeatherInfo[self.type]
		elif self.type == "forecastTomorrow2TempMax":
			return WeatherInfo[self.type]
		elif self.type == "forecastTomorrow2Text":
			return WeatherInfo[self.type]
		elif self.type == "forecastTomorrow2Picon":
			return WeatherInfo[self.type]
		elif self.type == "forecastTomorrow3Code":
			return WeatherInfo[self.type]
		elif self.type == "forecastTomorrow3Day":
			return WeatherInfo[self.type]
		elif self.type == "forecastTomorrow3Date":
			return WeatherInfo[self.type]
		elif self.type == "forecastTomorrow3TempMin":
			return WeatherInfo[self.type]
		elif self.type == "forecastTomorrow3TempMax":
			return WeatherInfo[self.type]
		elif self.type == "forecastTomorrow3Text":
			return WeatherInfo[self.type]
		elif self.type == "forecastTomorrow3Picon":
			return WeatherInfo[self.type]
		elif self.type == "forecastTomorrow4Code":
			return WeatherInfo[self.type]
		elif self.type == "forecastTomorrow4Day":
			return WeatherInfo[self.type]
		elif self.type == "forecastTomorrow4Date":
			return WeatherInfo[self.type]
		elif self.type == "forecastTomorrow4TempMin":
			return WeatherInfo[self.type]
		elif self.type == "forecastTomorrow4TempMax":
			return WeatherInfo[self.type]
		elif self.type == "forecastTomorrow4Text":
			return WeatherInfo[self.type]
		elif self.type == "forecastTomorrow4Picon":
			return WeatherInfo[self.type]
		elif self.type == "forecastTomorrow5Code":
			return WeatherInfo[self.type]
		elif self.type == "forecastTomorrow5Day":
			return WeatherInfo[self.type]
		elif self.type == "forecastTomorrow5Date":
			return WeatherInfo[self.type]
		elif self.type == "forecastTomorrow5TempMin":
			return WeatherInfo[self.type]
		elif self.type == "forecastTomorrow5TempMax":
			return WeatherInfo[self.type]
		elif self.type == "forecastTomorrow5Text":
			return WeatherInfo[self.type]
		elif self.type == "forecastTomorrow5Picon":
			return WeatherInfo[self.type]
		elif self.type == "forecastTomorrow6Code":
			return WeatherInfo[self.type]
		elif self.type == "forecastTomorrow6Day":
			return WeatherInfo[self.type]
		elif self.type == "forecastTomorrow6Date":
			return WeatherInfo[self.type]
		elif self.type == "forecastTomorrow6TempMin":
			return WeatherInfo[self.type]
		elif self.type == "forecastTomorrow6TempMax":
			return WeatherInfo[self.type]
		elif self.type == "forecastTomorrow6Text":
			return WeatherInfo[self.type]
		elif self.type == "forecastTomorrow6Picon":
			return WeatherInfo[self.type]
		elif self.type == "forecastTomorrow7Code":
			return WeatherInfo[self.type]
		elif self.type == "forecastTomorrow7Day":
			return WeatherInfo[self.type]
		elif self.type == "forecastTomorrow7Date":
			return WeatherInfo[self.type]
		elif self.type == "forecastTomorrow7TempMin":
			return WeatherInfo[self.type]
		elif self.type == "forecastTomorrow7TempMax":
			return WeatherInfo[self.type]
		elif self.type == "forecastTomorrow7Text":
			return WeatherInfo[self.type]
		elif self.type == "forecastTomorrow7Picon":
			return WeatherInfo[self.type]
		elif self.type == "forecastTomorrow8Code":
			return WeatherInfo[self.type]
		elif self.type == "forecastTomorrow8Day":
			return WeatherInfo[self.type]
		elif self.type == "forecastTomorrow8Date":
			return WeatherInfo[self.type]
		elif self.type == "forecastTomorrow8TempMin":
			return WeatherInfo[self.type]
		elif self.type == "forecastTomorrow8TempMax":
			return WeatherInfo[self.type]
		elif self.type == "forecastTomorrow8Text":
			return WeatherInfo[self.type]
		elif self.type == "forecastTomorrow8Picon":
			return WeatherInfo[self.type]
		elif self.type == "CF":
			return self.getCF()
		else:
			return "not supported"

	def getCF(self):
			return ""

	text = property(getText)

class WeatherData:
	def __init__(self):
		self.WeatherInfo = WeatherInfo = { 
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
			"forecastTomorrow5Code": "(",
			"forecastTomorrow5Day": "N/A",
			"forecastTomorrow5Date": "N/A",
			"forecastTomorrow5TempMin": "0",
			"forecastTomorrow5TempMax": "0",
			"forecastTomorrow5Text": "N/A",
			"forecastTomorrow5Picon": "3200",
			"forecastTomorrow6Code": "(",
			"forecastTomorrow6Day": "N/A",
			"forecastTomorrow6Date": "N/A",
			"forecastTomorrow6TempMin": "0",
			"forecastTomorrow6TempMax": "0",
			"forecastTomorrow6Text": "N/A",
			"forecastTomorrow6Picon": "3200",
			"forecastTomorrow7Code": "(",
			"forecastTomorrow7Day": "N/A",
			"forecastTomorrow7Date": "N/A",
			"forecastTomorrow7TempMin": "0",
			"forecastTomorrow7TempMax": "0",
			"forecastTomorrow7Text": "N/A",
			"forecastTomorrow7Picon": "3200",
			"forecastTomorrow8Code": "(",
			"forecastTomorrow8Day": "N/A",
			"forecastTomorrow8Date": "N/A",
			"forecastTomorrow8TempMin": "0",
			"forecastTomorrow8TempMax": "0",
			"forecastTomorrow8Text": "N/A",
			"forecastTomorrow8Picon": "3200",
		}

		if config.plugins.VWeather3.refreshInterval.value > 0:
			self.timer = eTimer()
			self.timer.callback.append(self.GetWeather)
			self.GetWeather()

	def downloadError(self, error = None):
		write_log("Error : " + str(error))

	def GetWeather(self):
		timeout = config.plugins.VWeather3.refreshInterval.value * 1000 * 60
		if timeout > 0:
			self.timer.start(timeout, True)
			countrycode = config.plugins.VWeather3.CountryCode.value
			units = config.plugins.VWeather3.Units.value
			if os.path.isfile("/tmp/VWeather3.log"):
				os.remove("/tmp/VWeather3.log")
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
				if log:
					write_log("DARKSKY-URL : " + str(url))
				getPage(url).addCallback(self.GotDarkskyWeatherData).addErrback(self.downloadError)
			elif config.plugins.VWeather3.Provider.value == "OpenWeatherMap":
				apikey = config.plugins.VWeather3.OpenWeatherMap_apikey.value
				zipcode = config.plugins.VWeather3.OpenWeatherMap_zipcode.value
				if config.plugins.VWeather3.OpenWeatherMap_geolocation.value == "PLZ":
					geolocation = "zip=" + config.plugins.VWeather3.OpenWeatherMap_zipcode.value + "," + countrycode
				else:
					geolocation = "q=" + config.plugins.VWeather3.OpenWeatherMap_place.value
#					geolocation = "q=" + config.plugins.VWeather3.OpenWeatherMap_place.value + "," + countrycode
				url = "http://api.openweathermap.org/data/2.5/forecast?" + geolocation + "&APPID=" + apikey + "&units=" + units + "&lang=" + countrycode
				if log:
					write_log("OWM-URL : " + str(url))
				getPage(url,method = "GET").addCallback(self.GotOpenWeatherMapWeatherData).addErrback(self.downloadError)
				url = "http://api.openweathermap.org/data/2.5/weather?" + geolocation + "&APPID=" + apikey + "&units=" + units + "&lang=" + countrycode
				if log:
					write_log("COWMURL : " + str(url))
				getPage(url,method = "GET").addCallback(self.GotCurrentOpenWeatherMapWeatherData).addErrback(self.downloadError)


	#OpenWeatherMap
	def GotOpenWeatherMapWeatherData(self, data = None):
		if log:
			write_log("###################################### OpenWeatherMap Data ################################################")
			write_log("Data : " + str(data))
		if data is not None:
			try:
				parsed_json = json.loads(data)
				if log:
					for k, v in parsed_json.items():
						write_log(str(k) + ":" + str(v))
					write_log(str(len(parsed_json["list"])))

					write_log("###################################### OpenWeatherMap ################################################")
					for k, v in parsed_json["list"][0].items():
						write_log(str(k) + ":" + str(v))

				self.WeatherInfo["atmoPressure"] = format(float(parsed_json['list'][0]['main']['grnd_level']), '.0f') + " mBar"

				# nächsten Tag finden
				i = 0
				next_day = 0
				while i < 8:
					if str(self.convertCurrentTime(parsed_json["list"][i]['dt'])) == "23:00:00" or str(self.convertCurrentTime(parsed_json["list"][i]['dt'])) == "00:00:00" or str(self.convertCurrentTime(parsed_json["list"][i]['dt'])) == "01:00:00":
						next_day = i
						if log:
							write_log("morgen startet bei Index " + str(next_day))
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
						if float(parsed_json["list"][i]['main']['temp_min']) < tempmin:
							tempmin = float(parsed_json["list"][i]['main']['temp_min'])
						if float(parsed_json["list"][i]['main']['temp_max']) > tempmax:
							tempmax = float(parsed_json["list"][i]['main']['temp_max'])
						i += 1
					self.WeatherInfo["forecastTodayCode"] = str(self.ConvertIconCode(self.get_most_element(icons)))
					self.WeatherInfo["forecastTodayPicon"] = str(self.convertOWMIconName(self.get_most_element(icons)))
					self.WeatherInfo["forecastTodayTempMax"] = format(tempmax, str(numbers)) + self.ConvertTemp(config.plugins.VWeather3.Units.value)
					self.WeatherInfo["forecastTodayTempMin"] = format(tempmin, str(numbers)) + self.ConvertTemp(config.plugins.VWeather3.Units.value)
					self.WeatherInfo["forecastTodayText"] = str(self.get_most_element(description))
				else:
					while i < 8:
						icons.append(parsed_json["list"][i]['weather'][0]['icon'])
						description.append(parsed_json["list"][i]['weather'][0]['description'])
						if float(parsed_json["list"][i]['main']['temp_min']) < tempmin:
							tempmin = float(parsed_json["list"][i]['main']['temp_min'])
						if float(parsed_json["list"][i]['main']['temp_max']) > tempmax:
							tempmax = float(parsed_json["list"][i]['main']['temp_max'])
						i += 1
					self.WeatherInfo["forecastTodayCode"] = str(self.ConvertIconCode(self.get_most_element(icons)))
					self.WeatherInfo["forecastTodayPicon"] = str(self.convertOWMIconName(self.get_most_element(icons)))
					self.WeatherInfo["forecastTodayTempMax"] = format(tempmax, str(numbers)) + self.ConvertTemp(config.plugins.VWeather3.Units.value)
					self.WeatherInfo["forecastTodayTempMin"] = format(tempmin, str(numbers)) + self.ConvertTemp(config.plugins.VWeather3.Units.value)
					self.WeatherInfo["forecastTodayText"] = str(self.get_most_element(description))

				if next_day == 0:
					next_day = 8
				i = next_day
				icons = []
				description = []
				tempmin = 100
				tempmax = -100
				self.WeatherInfo["forecastTomorrowDay"] = self.convertCurrentDay(parsed_json['list'][i]['dt'])
				self.WeatherInfo["forecastTomorrowDate"] = self.convertCurrentDate(parsed_json['list'][i]['dt'])
				if log:
					write_log("Tag startet bei  " + str(parsed_json["list"][i]['dt_txt']) + " mit Index " + str(next_day))
				while i < int(next_day + 16):
					icons.append(parsed_json["list"][i]['weather'][0]['icon'])
					description.append(parsed_json["list"][i]['weather'][0]['description'])
					if float(parsed_json["list"][i]['main']['temp_min']) < tempmin:
						tempmin = float(parsed_json["list"][i]['main']['temp_min'])
					if float(parsed_json["list"][i]['main']['temp_max']) > tempmax:
						tempmax = float(parsed_json["list"][i]['main']['temp_max'])
					i += 1
				self.WeatherInfo["forecastTomorrowCode"] = str(self.ConvertIconCode(self.get_most_element(icons)))
				self.WeatherInfo["forecastTomorrowPicon"] = str(self.convertOWMIconName(self.get_most_element(icons)))
				self.WeatherInfo["forecastTomorrowTempMax"] = format(tempmax, str(numbers)) + self.ConvertTemp(config.plugins.VWeather3.Units.value)
				self.WeatherInfo["forecastTomorrowTempMin"] = format(tempmin, str(numbers)) + self.ConvertTemp(config.plugins.VWeather3.Units.value)
				self.WeatherInfo["forecastTomorrowText"] = str(self.get_most_element(description))

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
					self.WeatherInfo["forecastTomorrow" + str(day) + "Day"] = self.convertCurrentDay(parsed_json['list'][i]['dt'])
					self.WeatherInfo["forecastTomorrow" + str(day) + "Date"] = self.convertCurrentDate(parsed_json['list'][i]['dt'])
					if log:
						write_log("Tag startet bei  " + str(parsed_json["list"][i]['dt_txt']) + " mit Index " + str(nd))
					while i < int(nd + 8) and i < int(len(parsed_json["list"])):
						icons.append(parsed_json["list"][i]['weather'][0]['icon'])
						description.append(parsed_json["list"][i]['weather'][0]['description'])
						if float(parsed_json["list"][i]['main']['temp_min']) < tempmin:
							tempmin = float(parsed_json["list"][i]['main']['temp_min'])
						if float(parsed_json["list"][i]['main']['temp_max']) > tempmax:
							tempmax = float(parsed_json["list"][i]['main']['temp_max'])
						i += 1
					self.WeatherInfo["forecastTomorrow" + str(day) + "Code"] = str(self.ConvertIconCode(self.get_most_element(icons)))
					self.WeatherInfo["forecastTomorrow" + str(day) + "Picon"] = str(self.convertOWMIconName(self.get_most_element(icons)))
					self.WeatherInfo["forecastTomorrow" + str(day) + "TempMax"] = format(tempmax, str(numbers)) + self.ConvertTemp(config.plugins.VWeather3.Units.value)
					self.WeatherInfo["forecastTomorrow" + str(day) + "TempMin"] = format(tempmin, str(numbers)) + self.ConvertTemp(config.plugins.VWeather3.Units.value)
					self.WeatherInfo["forecastTomorrow" + str(day) + "Text"] = str(self.get_most_element(description))

				# OWM liefert in der Freeversion nur 5 Tage - die restlichen werden hier aufgefüllt
				for aday in range(1, 5):
					self.WeatherInfo["forecastTomorrow" + str(day+aday) + "Day"] = " " # self.convertCurrentDay(int(parsed_json['list'][i]['dt']) + aday*86400)
					self.WeatherInfo["forecastTomorrow" + str(day+aday) + "Date"] = " " # self.convertCurrentDate(int(parsed_json['list'][i]['dt']) + aday*86400)
					self.WeatherInfo["forecastTomorrow" + str(day+aday) + "Code"] = " " # str(self.convertOWMIconName(self.get_most_element(icons)))
					self.WeatherInfo["forecastTomorrow" + str(day+aday) + "Picon"] = " " # str(self.convertOWMIconName(self.get_most_element(icons)))
					self.WeatherInfo["forecastTomorrow" + str(day+aday) + "TempMax"] = " " # format(tempmax, str(numbers)) + self.ConvertTemp(config.plugins.VWeather3.Units.value)
					self.WeatherInfo["forecastTomorrow" + str(day+aday) + "TempMin"] = " " # format(tempmin, str(numbers)) + self.ConvertTemp(config.plugins.VWeather3.Units.value)
					self.WeatherInfo["forecastTomorrow" + str(day+aday) + "Text"] = " " # str(self.get_most_element(description))
			except Exception as ex:
				write_log("Fehler in GotOpenWeatherMapWeatherData : " + str(ex))

	#CurrentOpenWeatherMap
	def GotCurrentOpenWeatherMapWeatherData(self, data = None):
		if log:
			write_log("###################################### Current OpenWeatherMap Data ################################################")
			write_log("Data : " + str(data))
		if data is not None:
			try:
				parsed_json = json.loads(data)

				self.WeatherInfo["provider"] = "OpenWeatherMap"
				self.WeatherInfo["currentLocation"] = str(self.ConvertCityName(parsed_json['name']))
				self.WeatherInfo["currentCountry"] = str(parsed_json['sys']["country"])

				self.WeatherInfo["windChill"] = format(float(parsed_json['main']['temp']), str(numbers)) + self.ConvertTemp(config.plugins.VWeather3.Units.value)
				self.WeatherInfo["windDirectionShort"] = str(self.ConvertDirectionShort(parsed_json['wind']['deg']))
				self.WeatherInfo["windDirectionLong"] = str(self.ConvertDirectionLong(parsed_json['wind']['deg']))
				self.WeatherInfo["windSpeed"] = format(float(parsed_json['wind']['speed']) * 3.6, '.0f') + self.ConvertSpeed(config.plugins.VWeather3.Units.value)

				self.WeatherInfo["atmoHumidity"] = format(float(parsed_json['main']['humidity']), '.0f') + ' %'
				self.WeatherInfo["atmoRising"] = "-1"
				self.WeatherInfo["atmoVisibility"] = format(float(parsed_json['visibility'] / 1000), str(numbers)) + self.ConvertVisibility(config.plugins.VWeather3.Units.value)

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
				self.WeatherInfo["currentWeatherPicon"] = self.convertOWMIconName(parsed_json['weather'][0]['icon'])

				if log:
					write_log("###################################### Current OpenWeatherMap ################################################")
					for k, v in parsed_json.items():
						write_log(str(k) + ":" + str(v))
			except Exception as ex:
				write_log("Fehler in GotCurrentOpenWeatherMapWeatherData : " + str(ex))

	#Darksky
	def GotDarkskyWeatherData(self, data = None):
		if log:
			write_log("Data : " + str(data))
		if data is not None:
			try:
				parsed_json = json.loads(data)
				if log:
					for k, v in parsed_json.items():
						write_log(str(k) + ":" + str(v))

				self.WeatherInfo["provider"] = "Darksky"
				self.WeatherInfo["currentLocation"] = format(float(parsed_json['latitude']), '.4f') + " / " + format(float(parsed_json['longitude']), '.4f')
				self.WeatherInfo["currentCountry"] = "DE"

				self.WeatherInfo["windChill"] = format(float(parsed_json['currently']['apparentTemperature']), str(numbers)) + self.ConvertTemp(config.plugins.VWeather3.Units.value)
				self.WeatherInfo["windDirectionShort"] = str(self.ConvertDirectionShort(parsed_json['currently']['windBearing']))
				self.WeatherInfo["windDirectionLong"] = str(self.ConvertDirectionLong(parsed_json['currently']['windBearing']))
				self.WeatherInfo["windSpeed"] = format(float(parsed_json['currently']['windSpeed']), '.0f') + self.ConvertSpeed(config.plugins.VWeather3.Units.value)

				self.WeatherInfo["atmoHumidity"] = format(float(parsed_json['currently']['humidity']) * 100, '.0f') + ' %'
				self.WeatherInfo["atmoPressure"] = format(float(parsed_json['currently']['pressure']), '.0f') + ' mBar'
				self.WeatherInfo["atmoRising"] = ""
				self.WeatherInfo["atmoVisibility"] = format(float(parsed_json['currently']['visibility']), str(numbers)) + self.ConvertVisibility(config.plugins.VWeather3.Units.value)

				self.WeatherInfo["astroSunrise"] = self.convertAstroSun(parsed_json['daily']['data'][0]['sunriseTime'])
				self.WeatherInfo["astroSunset"] = self.convertAstroSun(parsed_json['daily']['data'][0]['sunsetTime'])

				self.WeatherInfo["geoLat"] = format(float(parsed_json['latitude']), '.4f')
				self.WeatherInfo["geoLong"] = format(float(parsed_json['longitude']), '.4f')
				self.WeatherInfo["geoData"] = format(float(parsed_json['latitude']), '.4f') + " / " + format(float(parsed_json['longitude']), '.4f')

				self.WeatherInfo["downloadDate"] = self.convertCurrentDate(parsed_json['currently']['time'])
				self.WeatherInfo["downloadTime"] = self.convertCurrentTime(parsed_json['currently']['time'])
				self.WeatherInfo["currentWeatherCode"] = self.ConvertIconCode(parsed_json['currently']['icon'])
				self.WeatherInfo["currentWeatherTemp"] = format(float(parsed_json['currently']['temperature']), str(numbers)) + self.ConvertTemp(config.plugins.VWeather3.Units.value)
				self.WeatherInfo["currentWeatherText"] = str(parsed_json['currently']['summary'])
				self.WeatherInfo["currentWeatherPicon"] = self.convertIconName(parsed_json['currently']['icon'])

				self.WeatherInfo["forecastTodayCode"] = self.ConvertIconCode(parsed_json['daily']['data'][0]['icon'])
				self.WeatherInfo["forecastTodayDay"] = self.convertCurrentDay(parsed_json['daily']['data'][0]['time'])
				self.WeatherInfo["forecastTodayDate"] = self.convertCurrentDate(parsed_json['daily']['data'][0]['time'])
				self.WeatherInfo["forecastTodayTempMax"] = format(float(parsed_json['daily']['data'][0]['temperatureMax']), str(numbers)) + self.ConvertTemp(config.plugins.VWeather3.Units.value)
				self.WeatherInfo["forecastTodayTempMin"] = format(float(parsed_json['daily']['data'][0]['temperatureMin']), str(numbers)) + self.ConvertTemp(config.plugins.VWeather3.Units.value)
				self.WeatherInfo["forecastTodayText"] = self.convertWeatherText(parsed_json['daily']['data'][0]['icon'])
				self.WeatherInfo["forecastTodayPicon"] = self.convertIconName(parsed_json['daily']['data'][0]['icon'])

				self.WeatherInfo["forecastTomorrowCode"] = self.ConvertIconCode(parsed_json['daily']['data'][1]['icon'])
				self.WeatherInfo["forecastTomorrowDay"] = self.convertCurrentDay(parsed_json['daily']['data'][1]['time'])
				self.WeatherInfo["forecastTomorrowDate"] = self.convertCurrentDate(parsed_json['daily']['data'][1]['time'])
				self.WeatherInfo["forecastTomorrowTempMax"] = format(float(parsed_json['daily']['data'][1]['temperatureMax']), str(numbers)) + self.ConvertTemp(config.plugins.VWeather3.Units.value)
				self.WeatherInfo["forecastTomorrowTempMin"] = format(float(parsed_json['daily']['data'][1]['temperatureMin']), str(numbers)) + self.ConvertTemp(config.plugins.VWeather3.Units.value)
				self.WeatherInfo["forecastTomorrowText"] = self.convertWeatherText(parsed_json['daily']['data'][1]['icon'])
				self.WeatherInfo["forecastTomorrowPicon"] = self.convertIconName(parsed_json['daily']['data'][1]['icon'])

				self.WeatherInfo["forecastTomorrow1Code"] = self.ConvertIconCode(parsed_json['daily']['data'][2]['icon'])
				self.WeatherInfo["forecastTomorrow1Day"] = self.convertCurrentDay(parsed_json['daily']['data'][2]['time'])
				self.WeatherInfo["forecastTomorrow1Date"] = self.convertCurrentDate(parsed_json['daily']['data'][2]['time'])
				self.WeatherInfo["forecastTomorrow1TempMax"] = format(float(parsed_json['daily']['data'][2]['temperatureMax']), str(numbers)) + self.ConvertTemp(config.plugins.VWeather3.Units.value)
				self.WeatherInfo["forecastTomorrow1TempMin"] = format(float(parsed_json['daily']['data'][2]['temperatureMin']), str(numbers)) + self.ConvertTemp(config.plugins.VWeather3.Units.value)
				self.WeatherInfo["forecastTomorrow1Text"] = self.convertWeatherText(parsed_json['daily']['data'][2]['icon'])
				self.WeatherInfo["forecastTomorrow1Picon"] = self.convertIconName(parsed_json['daily']['data'][2]['icon'])

				self.WeatherInfo["forecastTomorrow2Code"] = self.ConvertIconCode(parsed_json['daily']['data'][3]['icon'])
				self.WeatherInfo["forecastTomorrow2Day"] = self.convertCurrentDay(parsed_json['daily']['data'][3]['time'])
				self.WeatherInfo["forecastTomorrow2Date"] = self.convertCurrentDate(parsed_json['daily']['data'][3]['time'])
				self.WeatherInfo["forecastTomorrow2TempMax"] = format(float(parsed_json['daily']['data'][3]['temperatureMax']), str(numbers)) + self.ConvertTemp(config.plugins.VWeather3.Units.value)
				self.WeatherInfo["forecastTomorrow2TempMin"] = format(float(parsed_json['daily']['data'][3]['temperatureMin']), str(numbers)) + self.ConvertTemp(config.plugins.VWeather3.Units.value)
				self.WeatherInfo["forecastTomorrow2Text"] = self.convertWeatherText(parsed_json['daily']['data'][3]['icon'])
				self.WeatherInfo["forecastTomorrow2Picon"] = self.convertIconName(parsed_json['daily']['data'][3]['icon'])

				self.WeatherInfo["forecastTomorrow3Code"] = self.ConvertIconCode(parsed_json['daily']['data'][4]['icon'])
				self.WeatherInfo["forecastTomorrow3Day"] = self.convertCurrentDay(parsed_json['daily']['data'][4]['time'])
				self.WeatherInfo["forecastTomorrow3Date"] = self.convertCurrentDate(parsed_json['daily']['data'][4]['time'])
				self.WeatherInfo["forecastTomorrow3TempMax"] = format(float(parsed_json['daily']['data'][4]['temperatureMax']), str(numbers)) + self.ConvertTemp(config.plugins.VWeather3.Units.value)
				self.WeatherInfo["forecastTomorrow3TempMin"] = format(float(parsed_json['daily']['data'][4]['temperatureMin']), str(numbers)) + self.ConvertTemp(config.plugins.VWeather3.Units.value)
				self.WeatherInfo["forecastTomorrow3Text"] = self.convertWeatherText(parsed_json['daily']['data'][4]['icon'])
				self.WeatherInfo["forecastTomorrow3Picon"] = self.convertIconName(parsed_json['daily']['data'][4]['icon'])

				self.WeatherInfo["forecastTomorrow4Code"] = self.ConvertIconCode(parsed_json['daily']['data'][5]['icon'])
				self.WeatherInfo["forecastTomorrow4Day"] = self.convertCurrentDay(parsed_json['daily']['data'][5]['time'])
				self.WeatherInfo["forecastTomorrow4Date"] = self.convertCurrentDate(parsed_json['daily']['data'][5]['time'])
				self.WeatherInfo["forecastTomorrow4TempMax"] = format(float(parsed_json['daily']['data'][5]['temperatureMax']), str(numbers)) + self.ConvertTemp(config.plugins.VWeather3.Units.value)
				self.WeatherInfo["forecastTomorrow4TempMin"] = format(float(parsed_json['daily']['data'][5]['temperatureMin']), str(numbers)) + self.ConvertTemp(config.plugins.VWeather3.Units.value)
				self.WeatherInfo["forecastTomorrow4Text"] = self.convertWeatherText(parsed_json['daily']['data'][5]['icon'])
				self.WeatherInfo["forecastTomorrow4Picon"] = self.convertIconName(parsed_json['daily']['data'][5]['icon'])

				self.WeatherInfo["forecastTomorrow5Code"] = self.ConvertIconCode(parsed_json['daily']['data'][6]['icon'])
				self.WeatherInfo["forecastTomorrow5Day"] = self.convertCurrentDay(parsed_json['daily']['data'][6]['time'])
				self.WeatherInfo["forecastTomorrow5Date"] = self.convertCurrentDate(parsed_json['daily']['data'][6]['time'])
				self.WeatherInfo["forecastTomorrow5TempMax"] = format(float(parsed_json['daily']['data'][6]['temperatureMax']), str(numbers)) + self.ConvertTemp(config.plugins.VWeather3.Units.value)
				self.WeatherInfo["forecastTomorrow5TempMin"] = format(float(parsed_json['daily']['data'][6]['temperatureMin']), str(numbers)) + self.ConvertTemp(config.plugins.VWeather3.Units.value)
				self.WeatherInfo["forecastTomorrow5Text"] = self.convertWeatherText(parsed_json['daily']['data'][6]['icon'])
				self.WeatherInfo["forecastTomorrow5Picon"] = self.convertIconName(parsed_json['daily']['data'][6]['icon'])

				self.WeatherInfo["forecastTomorrow6Code"] = self.ConvertIconCode(parsed_json['daily']['data'][7]['icon'])
				self.WeatherInfo["forecastTomorrow6Day"] = self.convertCurrentDay(parsed_json['daily']['data'][7]['time'])
				self.WeatherInfo["forecastTomorrow6Date"] = self.convertCurrentDate(parsed_json['daily']['data'][7]['time'])
				self.WeatherInfo["forecastTomorrow6TempMax"] = format(float(parsed_json['daily']['data'][7]['temperatureMax']), str(numbers)) + self.ConvertTemp(config.plugins.VWeather3.Units.value)
				self.WeatherInfo["forecastTomorrow6TempMin"] = format(float(parsed_json['daily']['data'][7]['temperatureMin']), str(numbers)) + self.ConvertTemp(config.plugins.VWeather3.Units.value)
				self.WeatherInfo["forecastTomorrow6Text"] = self.convertWeatherText(parsed_json['daily']['data'][7]['icon'])
				self.WeatherInfo["forecastTomorrow6Picon"] = self.convertIconName(parsed_json['daily']['data'][7]['icon'])

				# Darksky liefert in der Freeversion nur 8 Tage - die restlichen werden hier aufgefüllt
				self.WeatherInfo["forecastTomorrow7Code"] = " " #str(parsed_json['daily']['data'][7]['icon'])
				self.WeatherInfo["forecastTomorrow7Day"] = " " #self.convertCurrentDay(parsed_json['daily']['data'][7]['time'])
				self.WeatherInfo["forecastTomorrow7Date"] = " " #self.convertCurrentDate(parsed_json['daily']['data'][7]['time'])
				self.WeatherInfo["forecastTomorrow7TempMax"] = " " #format(float(parsed_json['daily']['data'][7]['temperatureMax']), str(numbers)) + self.ConvertTemp(config.plugins.VWeather3.Units.value)
				self.WeatherInfo["forecastTomorrow7TempMin"] = " " #format(float(parsed_json['daily']['data'][7]['temperatureMin']), str(numbers)) + self.ConvertTemp(config.plugins.VWeather3.Units.value)
				self.WeatherInfo["forecastTomorrow7Text"] = " " #self.convertWeatherText(parsed_json['daily']['data'][7]['icon'])
				self.WeatherInfo["forecastTomorrow7Picon"] = " " #self.convertIconName(parsed_json['daily']['data'][7]['icon'])

				self.WeatherInfo["forecastTomorrow8Code"] = " " #str(parsed_json['daily']['data'][7]['icon'])
				self.WeatherInfo["forecastTomorrow8Day"] = " " #self.convertCurrentDay(parsed_json['daily']['data'][7]['time'])
				self.WeatherInfo["forecastTomorrow8Date"] = " " #self.convertCurrentDate(parsed_json['daily']['data'][7]['time'])
				self.WeatherInfo["forecastTomorrow8TempMax"] = " " #format(float(parsed_json['daily']['data'][7]['temperatureMax']), str(numbers)) + self.ConvertTemp(config.plugins.VWeather3.Units.value)
				self.WeatherInfo["forecastTomorrow8TempMin"] = " " #format(float(parsed_json['daily']['data'][7]['temperatureMin']), str(numbers)) + self.ConvertTemp(config.plugins.VWeather3.Units.value)
				self.WeatherInfo["forecastTomorrow8Text"] = " " #self.convertWeatherText(parsed_json['daily']['data'][7]['icon'])
				self.WeatherInfo["forecastTomorrow8Picon"] = " " #self.convertIconName(parsed_json['daily']['data'][7]['icon'])

				if "alerts" in parsed_json:
					self.WeatherInfo["alerts"] = str(parsed_json['alerts'][0]['description'])
					if config.plugins.VWeather3.Darksky_alerts.value == "true":
						Notifications.AddPopup(str(parsed_json['alerts'][0]['title']) + " ab " + str(convertDateTime(parsed_json['alerts'][0]['time'])) + "\n" + str(parsed_json['alerts'][0]['description']), MessageBox.TYPE_INFO, 20)
				else:
					self.WeatherInfo["alerts"] = "keine Unwetterwarnungen vorhanden"
				if log:
					for k, v in self.WeatherInfo.items():
						write_log("WeatherInfo : " + str(k) + ":" + str(v))
			except Exception as ex:
				write_log("Fehler in GotWeatherData : " + str(ex))

	def ConvertDirectionShort(self, direction):
		dir = int(direction)
		if dir >= 0 and dir <= 20:
				direction = "N"
		elif dir >= 21 and dir <= 35:
				direction = "NNO"
		elif dir >= 36 and dir <= 55:
				direction = "NO"
		elif dir >= 56 and dir <= 70:
				direction = "ONO"
		elif dir >= 71 and dir <= 110:
				direction = "O"
		elif dir >= 111 and dir <= 125:
				direction = "OSO"
		elif dir >= 126 and dir <= 145:
				direction = "SO"
		elif dir >= 146 and dir <= 160:
				direction = "SSO"
		elif dir >= 161 and dir <= 200:
				direction = "S"
		elif dir >= 201 and dir <= 215:
				direction = "SSW"
		elif dir >= 216 and dir <= 235:
				direction = "SW"
		elif dir >= 236 and dir <= 250:
				direction = "WSW"
		elif dir >= 251 and dir <= 290:
				direction = "W"
		elif dir >= 291 and dir <= 305:
				direction = "WNW"
		elif dir >= 306 and dir <= 325:
				direction = "NW"
		elif dir >= 326 and dir <= 340:
				direction = "NNW"
		elif dir >= 341 and dir <= 360:
				direction = "N"
		else:
				direction = "N/A"
		return str(direction)

	def ConvertDirectionLong(self, direction):
		if config.plugins.VWeather3.Units.value == "imperial":
			dir = int(direction)
			if dir >= 0 and dir <= 20:
					direction = "North"
			elif dir >= 21 and dir <= 35:
					direction = "North-Northeast"
			elif dir >= 36 and dir <= 55:
					direction = "Northeast"
			elif dir >= 56 and dir <= 70:
					direction = "East-Nordeast"
			elif dir >= 71 and dir <= 110:
					direction = "East"
			elif dir >= 111 and dir <= 125:
					direction = "East-Southeast"
			elif dir >= 126 and dir <= 145:
					direction = "Southeast"
			elif dir >= 146 and dir <= 160:
					direction = "South-Southeast"
			elif dir >= 161 and dir <= 200:
					direction = "South"
			elif dir >= 201 and dir <= 215:
					direction = "South-Southwest"
			elif dir >= 216 and dir <= 235:
					direction = "Southwest"
			elif dir >= 236 and dir <= 250:
					direction = "West-Southwest"
			elif dir >= 251 and dir <= 290:
					direction = "West"
			elif dir >= 291 and dir <= 305:
					direction = "West-Northwest"
			elif dir >= 306 and dir <= 325:
					direction = "Northwest"
			elif dir >= 326 and dir <= 340:
					direction = "North-Northwest"
			elif dir >= 341 and dir <= 360:
					direction = "North"
			else:
					direction = "N/A"
		else:
			dir = int(direction)
			if dir >= 0 and dir <= 20:
					direction = "Nord"
			elif dir >= 21 and dir <= 35:
					direction = "Nord-Nordost"
			elif dir >= 36 and dir <= 55:
					direction = "Nordost"
			elif dir >= 56 and dir <= 70:
					direction = "Ost-Nordost"
			elif dir >= 71 and dir <= 110:
					direction = "Ost"
			elif dir >= 111 and dir <= 125:
					direction = "Ost-Südost"
			elif dir >= 126 and dir <= 145:
					direction = "Südost"
			elif dir >= 146 and dir <= 160:
					direction = "Süd-Südost"
			elif dir >= 161 and dir <= 200:
					direction = "Süd"
			elif dir >= 201 and dir <= 215:
					direction = "Süd-Südwest"
			elif dir >= 216 and dir <= 235:
					direction = "Südwest"
			elif dir >= 236 and dir <= 250:
					direction = "West-Südwest"
			elif dir >= 251 and dir <= 290:
					direction = "West"
			elif dir >= 291 and dir <= 305:
					direction = "West-Nordwest"
			elif dir >= 306 and dir <= 325:
					direction = "Nordwest"
			elif dir >= 326 and dir <= 340:
					direction = "Nord-Nordwest"
			elif dir >= 341 and dir <= 360:
					direction = "Nord"
			else:
					direction = "N/A"
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
			return "20"
		elif IconName == "01n":
			return "31"
		elif IconName == "02n":
			return "33"
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
			return "46"
		elif IconName == "11n":
			return "47"
		elif IconName == "13n":
			return "46"
		elif IconName == "40n":
			return "45"
		elif IconName == "41n":
			return "46"
		else:
			if log:
				write_log("fehlender IconName : " + str(IconName))
			return "3200"

	def convertIconName(self, IconName):
		if IconName == "sleet":
			return "13"
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
			return "15"
		else:
			if log:
				write_log("fehlender IconName : " + str(IconName))
			return "3200"

	def convertWeatherText(self, WeatherText):
		if WeatherText == "sleet":
			return "Schneeregen"
		elif WeatherText == "wind":
			return "windig"
		elif WeatherText == "fog":
			return "nebelig"
		elif WeatherText == "partly-cloudy-night":
			return "teilweise bewölgt"
		elif WeatherText == "cloudy":
			return "bewölgt"
		elif WeatherText == "clear-night":
			return "klare Nacht"
		elif WeatherText == "clear-day":
			return "klarer Tag"
		elif WeatherText == "partly-cloudy-day":
			return "teilweise bewölkt"
		elif WeatherText == "rain":
			return "Regen"
		elif WeatherText == "snow":
			return "Schnee"
		else:
			if log:
				write_log("fehlender WeatherText : " + str(WeatherText))
			return "N/A"

	def convertAstroSun(self, val):
		value = datetime.datetime.fromtimestamp(int(val))
		return value.strftime('%H:%M')

	def convertCurrentDate(self, val):
		value = datetime.datetime.fromtimestamp(int(val))
		return value.strftime('%d.%m.')

	def convertCurrentDateLong(self, val):
		value = datetime.datetime.fromtimestamp(int(val))
		return value.strftime('%d.%m.%Y')

	def convertCurrentTime(self, val):
		value = datetime.datetime.fromtimestamp(int(val))
		return value.strftime('%H:%M:%S')

	def convertCurrentDay(self, val):
		value = int(datetime.datetime.fromtimestamp(int(val)).strftime("%w"))
		skinname = str(config.skin.primary_skin.value).replace("/skin.xml","")
		if skinname == "Vu_HD_1080P" or skinname == "StyleFHD" or skinname == "AtileHD" or skinname == "MuteSpectator":
			if str(config.plugins.VWeather3.CountryCode.value) != "de":
				return swdays_en[value]
			else:
				return swdays[value]
		else:
			if str(config.plugins.VWeather3.CountryCode.value) != "de":
				return wdays_en[value]
			else:
				return wdays[value]

	def convertDateTime(self, val):
		value = datetime.datetime.fromtimestamp(int(val))
		return value.strftime('%d.%m.%Y %H:%M:%S')

	def ConvertTemp(self, unit):
		if config.plugins.VWeather3.Units.value == "imperial":
			return " °F"
		if config.plugins.VWeather3.Units.value == "metric":
			return " °C"
		else:
			return " °K"

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
			return name

	def ConvertIconCode(self, c):
		condition = "("
		if c == "01d" or c == "02d":
			condition = "S"
		elif c == "03d" or c == "04d":
			condition = "Z"
		elif c == "05d"  or c == "06d" or c == "07d" or c == "18d":
			condition = "U"
		elif c == "08d" or c == "10d" or c == "25d":
			condition = "G"
		elif c == "09d":
			condition = "Q"
		elif c == "11d" or c == "12d" or c == "40d":
			condition = "R"
		elif c == "13d" or c == "14d" or c == "15d" or c == "16d" or c == "41d" or c == "46d" or c == "42d" or c == "43d":
			condition = "W"
		elif c == "17d" or c == "35d":
			condition = "X"
		elif c == "19d":
			condition = "F"
		elif c == "20d" or c == "21d" or c == "22d":
			condition = "L"
		elif c == "23d" or c == "24d":
			condition = "S"
		elif c == "26d" or c == "44d":
			condition = "N"
		elif c == "27d" or c == "29d":
			condition = "I"
		elif c == "28d" or c == "30d":
			condition = "H"
		elif c == "31d" or c == "33d":
			condition = "C"
		elif c == "32d" or c == "34d":
			condition = "B"
		elif c == "36d":
			condition = "B"
		elif c == "37d" or c == "38d" or c == "39d" or c == "45d" or c == "47d":
			condition = "0"
		elif c == "01n" or c == "02n":
			condition = "S"
		elif c == "03n" or c == "04n":
			condition = "Z"
		elif c == "05n"  or c == "06n" or c == "07n" or c == "18n":
			condition = "U"
		elif c == "08n" or c == "10n" or c == "25n":
			condition = "G"
		elif c == "09n":
			condition = "Q"
		elif c == "11n" or c == "12n" or c == "40n":
			condition = "R"
		elif c == "13n" or c == "14n" or c == "15n" or c == "16n" or c == "41n" or c == "46n" or c == "42n" or c == "43n":
			condition = "W"
		elif c == "17n" or c == "35n":
			condition = "X"
		elif c == "19n":
			condition = "F"
		elif c == "20n" or c == "21n" or c == "22n":
			condition = "L"
		elif c == "23n" or c == "24n":
			condition = "S"
		elif c == "26n" or c == "44n":
			condition = "N"
		elif c == "27n" or c == "29n":
			condition = "I"
		elif c == "28n" or c == "30n":
			condition = "H"
		elif c == "31n" or c == "33n":
			condition = "C"
		elif c == "32n" or c == "34n":
			condition = "B"
		elif c == "36n":
			condition = "B"
		elif c == "37n" or c == "38n" or c == "39n" or c == "45n" or c == "47n":
			condition = "0"
		elif c == "sleet":
			condition = "W"
		elif c == "wind":
			condition = "S"
		elif c == "fog":
			condition = "L"
		elif c == "partly-cloudy-night":
			condition = "I"
		elif c == "cloudy":
			condition = "N"
		elif c == "clear-night":
			condition = "C"
		elif c == "clear-day":
			condition = "B"
		elif c == "partly-cloudy-day":
			condition = "H"
		elif c == "rain":
			return "15"
		elif c == "snow":
			return "12"
		else:
			condition = ")"
		return str(condition)

	def get_most_element(self, lst):
		return max(set(lst), key=lst.count)
