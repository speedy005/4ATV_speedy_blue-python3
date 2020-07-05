#######################################################################
#
#    Converter for Enigma2
#    Coded by shamann and Rampo(c)2018
#    Mod by Maggy
#    This program is free software; you can redistribute it and/or
#    modify it under the terms of the GNU General Public License
#    as published by the Free Software Foundation; either version 2
#    of the License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    Using in skin.xml countdown to "Christmas":
#
#    <widget source="global.CurrentTime" render="Label" position="0,0" size="1000,35" font="Regular;30" valign="center" halign="center" transparent="1">
#      <convert type="CountdownToChristmasOrNewYear">Christmas</convert>
#    </widget>
#
#    or countdown to "New Year"
#
#    <widget source="global.CurrentTime" render="Label" position="0,0" size="1000,35" font="Regular;30" valign="center" halign="center" transparent="1">
#      <convert type="CountdownToChristmasOrNewYear">NewYear</convert>
#    </widget>
#
#    
#######################################################################
from Converter import Converter
from Components.Element import cached
from datetime import datetime, time

class speedyCountdownToChristmasOrNewYear(Converter, object):
	DAYS = 0
	TIME = 1

	def __init__(self, type):
		Converter.__init__(self, type)
		if type == "Christmas":
			self.type = self.DAYS
		else:
			self.type = self.TIME

	@cached
	def getText(self):
		time = self.source.time
		if time is None:
			return ""
		if self.type == self.DAYS:
			return self.calculate()
		elif self.type == self.TIME:
			return self.calculate(False)
		else:
			return "???"

	text = property(getText)

	def calculate(self,what=True):
		now = datetime.now()
		if what:
			xmas = datetime(now.year, 12, 25)
			delta = xmas - now
			final= delta.days
			if final > 0:
				return str(final) + " Tage bis zum Weihnachtsfest!"
			elif final == 0:
				return "Froehliche Weihnachten!"
			elif final < 0:
				return "Weihnachten ist vorbei, bis zum naechsten Jahr!"
		else:
			leaving_date = datetime.strptime('%s-01-01 00:00:00' % str(int(now.year)+1),'%Y-%m-%d %H:%M:%S')
			return '%d Tage, %d Std. %d Min. %d Sek.' % self.daysHoursMinutesSecondsFromSeconds(self.dateDiffInSeconds(now,leaving_date)) +  " bis zum neuen Jahr!"

	def dateDiffInSeconds(self,date1, date2):
		timedelta = date2 - date1
		return timedelta.days * 24 * 3600 + timedelta.seconds

	def daysHoursMinutesSecondsFromSeconds(self,seconds):
		(minutes, seconds) = divmod(seconds, 60)
		(hours, minutes) = divmod(minutes, 60)
		(days, hours) = divmod(hours, 24)
		return (days, hours, minutes, seconds)		
		