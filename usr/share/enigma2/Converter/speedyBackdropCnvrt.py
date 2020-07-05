# -*- coding: utf-8 -*-
# by digiteng...12-2019

from Components.Converter.Converter import Converter
from Components.Element import cached
import json
import re
import os
import urllib2

try:
	if os.path.isdir('/media/usb/backdrop'):
		folder_size = 0
		for (path, dirs, files) in os.walk('/media/usb/backdrop'):
			for file in files:
				filename = os.path.join(path, file)
				folder_size += os.path.getsize(filename)
		posterP_sz = "%0.f" % (folder_size/(1024*1024.0))
		if posterP_sz >= 10: # '/media/usb/backdrop' folder remove size(10MB)...
			import shutil
			shutil.rmtree('/media/usb/backdrop')
except:
	pass

if not os.path.isdir('/media/usb/backdrop'):
	os.mkdir('/media/usb/backdrop')

class speedyBackdropCnvrt(Converter, object):

	def __init__(self, type):
		Converter.__init__(self, type)
		self.type = type

	@cached
	def getText(self):
		event = self.source.event
		if event is None:
			return ""

		if not event is None:
			if self.type == "BACKDROP":
				self.evnt = event.getEventName()
				try:
					p = '((.*?)) \([T](\d+)\)'
					e1 = re.search(p,self.evnt)
					if e1:
						jr = e1.group(1)
						self.evntNm = re.sub('\s+', '+', jr)
					else:
						self.evntNm = re.sub('\s+', '+', self.evnt)
					self.evntNmPstr = self.evntNm + ".jpg"
					if not os.path.exists("/media/usb/backdrop/%s.jpg"%(self.evntNm)):
						ses_ep = self.sessionEpisode(event)
						if ses_ep != "" and len(ses_ep) > 0:
							self.srch = "tv"
							self.searchPoster()
						else:
							self.srch = "multi"
							self.searchPoster()
					else:
						return self.evntNm
				except:
					pass
		else:
			return ""
	text = property(getText)
	
	def searchPoster(self):
		url_json = "https://api.themoviedb.org/3/search/%s?api_key=3c3efcf47c3577558812bb9d64019d65&language=de-DE&append_to_response=images&include_image_language=de,null&query=%s"%(self.srch, self.evntNm)
		jp = json.load(urllib2.urlopen(url_json))

		imgP = (jp['results'][0]['backdrop_path'])
		url_poster = "https://image.tmdb.org/t/p/w300%s"%(imgP)
		dwn_poster = "/media/usb/backdrop/%s.jpg"%(self.evntNm)
		if not os.path.exists(dwn_poster):
			with open(dwn_poster,'wb') as f:
				f.write(urllib2.urlopen(url_poster).read())
				f.close()
				return self.evntNm

	def sessionEpisode(self, event):
		fd = event.getShortDescription() + "\n" + event.getExtendedDescription()
		pattern = ["(\d+). Staffel, Folge (\d+)", "T(\d+) Ep.(\d+)", "'Episodio (\d+)' T(\d+)"]
		for i in pattern:
			seg = re.search(i, fd)
			if seg:
				if re.search("Episodio",i):
					return "S"+seg.group(2).zfill(2)+"E"+seg.group(1).zfill(2)
				else :
					return "S"+seg.group(1).zfill(2)+"E"+seg.group(2).zfill(2)
		return ""