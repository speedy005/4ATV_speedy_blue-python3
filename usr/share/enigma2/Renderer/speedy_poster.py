# -*- coding: utf-8 -*-
# by digiteng...02.2020
# <widget source="session.Event_Now" render="poster" position="0,0" size="185,278" zPosition="1" />
from Renderer import Renderer
from enigma import ePixmap, ePicLoad
from Components.AVSwitch import AVSwitch
from Components.Pixmap import Pixmap
from urllib import quote
import json
import re
import os
import urllib2

if os.path.isdir("/media/usb"):
	path_folder = "/media/usb/poster/"
else:
	path_folder = "/media/usb/poster/"

try:
	folder_size=sum([sum(map(lambda fname: os.path.getsize(os.path.join(path_folder, fname)), files)) for path_folder, folders, files in os.walk(path_folder)])
	posters_sz = "%0.f" % (folder_size/(1024*1024.0))
	if posters_sz >= "10":    # folder remove size(10MB)...
		import shutil
		shutil.rmtree(path_folder)
except:
	pass

class speedy_poster(Renderer):

	def __init__(self):
		Renderer.__init__(self)
		self.pstrNm = ''

	GUI_WIDGET = ePixmap
	def changed(self, what):
		try:
			if not self.instance:
				return
			event = self.source.event
			if what[0] != self.CHANGED_CLEAR:
				if event:
					evnt = event.getEventName()
					p = '((.*?)).\(.*?(.*?)\)'
					e1 = re.search(p, evnt)
					if e1:
						jr = e1.group(1)
						eName = jr
					else:
						eName = evnt
					pstrNm = path_folder + eName.lower() + ".jpg"
					if os.path.exists(pstrNm):
						try:
							size = self.instance.size()
							self.picload = ePicLoad()
							sc = AVSwitch().getFramebufferScale()
							if self.picload:
								self.picload.setPara((size.width(),
								size.height(),
								sc[0],
								sc[1],
								False,
								1,
								'#00000000'))
							result = self.picload.startDecode(pstrNm, 0, 0, False)
							if result == 0:
								ptr = self.picload.getData()
								if ptr != None:
									self.instance.setPixmap(ptr)
									self.instance.show()

						except:
							self.instance.hide()
					else:
						self.searchPoster()
						self.instance.hide()
				else:
					self.instance.hide()
		except:
			pass

	def searchPoster(self):
		event = self.source.event
		if not event is None:
			self.evnt = event.getEventName()
			try:
				p = '((.*?)).\(.*?(.*?)\)'
				e1 = re.search(p,self.evnt)
				if e1:
					jr = e1.group(1)
					self.evntNm = jr
				else:
					self.evntNm = self.evnt
				if not os.path.exists(path_folder + "%s.jpg"%(self.evntNm)):
					ses_ep = self.sessionEpisode(event)
					if ses_ep != "" and len(ses_ep) > 0:
						self.srch = "tv"
						self.savePoster()
					else:
						self.srch = "multi"
						self.savePoster()

			except:
				pass
		else:
			return ""

	def savePoster(self):
		url_json = "https://api.themoviedb.org/3/search/%s?api_key=3c3efcf47c3577558812bb9d64019d65&query=%s"%(self.srch, quote(self.evntNm))
		jp = json.load(urllib2.urlopen(url_json))
		poster = (jp['results'][0]['poster_path'])
		url_poster = "https://image.tmdb.org/t/p/w185_and_h278_bestv2%s"%(poster)
		if not os.path.isdir(path_folder):
			os.makedirs(path_folder)
		dwn_poster = path_folder + "%s.jpg"%(self.evntNm)
		if not os.path.exists(dwn_poster):
			with open(dwn_poster.lower(),'wb') as f:
				f.write(urllib2.urlopen(url_poster).read())
				f.close()
		return


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
