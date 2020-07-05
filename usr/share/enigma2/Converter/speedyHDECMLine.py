#
#  ECM LINE Converter
#
#  Coded by tomele for Kraven Skins
#
#  This code is licensed under the Creative Commons 
#  Attribution-NonCommercial-ShareAlike 4.0 International 
#  License. To view a copy of this license, visit
#  http://creativecommons.org/licenses/by-nc-sa/4.0/ 
#

from enigma import iServiceInformation, iPlayableService
from Components.Converter.Converter import Converter
from Components.Element import cached
from Components.config import config
from Poll import Poll
try:
   from enigma import eDVBCI_UI
   from enigma import eDVBCIInterfaces
   CI = True
except:
   CI = False
import os, gettext
from Tools.Directories import resolveFilename, SCOPE_LANGUAGE, SCOPE_PLUGINS
from Components.Language import language

lang = language.getLanguage()
os.environ["LANGUAGE"] = lang[:2]
gettext.bindtextdomain("enigma2", resolveFilename(SCOPE_LANGUAGE))
gettext.textdomain("enigma2")
gettext.bindtextdomain("SevenHD", "%s%s" % (resolveFilename(SCOPE_PLUGINS), "Extensions/SevenHD/locale/"))

def _(txt):
	t = gettext.dgettext("SevenHD", txt)
	if t == txt:
		t = gettext.gettext(txt)
	return t

class speedyHDECMLine(Poll, Converter, object):

	SATINFO = 0
	VERYSHORTCAID = 1
	VERYSHORTREADER = 2
	SHORTHOPS = 3
	SHORTREADER = 4
	NORMAL = 5
	LONG = 6
	VERYLONG = 7
	
	FTAINVISIBLE = 0
	FTAVISIBLE = 1
	
	def __init__(self, type):
		Poll.__init__(self)
		Converter.__init__(self, type)

		args = type.split(',')
		if len(args) != 2: 
			raise ElementError("type must contain exactly 2 arguments")
	
		type = args.pop(0)
		invisible = args.pop(0)
				
		if type == 'SatInfo':
			self.type = self.SATINFO
		elif type == 'VeryShortCaid':
			self.type = self.VERYSHORTCAID
		elif type == 'VeryShortReader':
			self.type = self.VERYSHORTREADER
		elif type == 'ShortHops':
			self.type = self.SHORTHOPS
		elif type == 'ShortReader':
			self.type = self.SHORTREADER
		elif type == 'Normal':
			self.type = self.NORMAL
		elif type == 'Long':
			self.type = self.LONG
		else:
			self.type = self.VERYLONG
		
		if invisible == "FTAInvisible":
			self.invisible = self.FTAINVISIBLE
		else:
			self.invisible = self.FTAVISIBLE

		self.poll_interval = 5000
		self.poll_enabled = True

	@cached
	def getText(self):

		ecmline = ''

		if self.IsCrypted():
			
			try:
				f = open('/tmp/ecm.info', 'r')
				flines = f.readlines()
				f.close()
			except:
				
				if CI:
				   NUM_CI=eDVBCIInterfaces.getInstance().getNumOfSlots()
                                   if NUM_CI > 0:
				      
                                      channel_caid_list = self.get_system_caid()
                                      appname = 'unsupported Cam/Card'
                                      found_caid = False
                                      
                                      for slot in range(NUM_CI):
                                          appname = eDVBCI_UI.getInstance().getAppName(slot)
                                          self.ci_cam = appname
                                          i=0
                                          caidlist=[]
                                      
                                          for caid in eDVBCIInterfaces.getInstance().readCICaIds(slot):
			                      i+=1
                                              caidlist.append((str(hex(int(caid)))))
                                          
                                          for channel_caid in channel_caid_list:
                                              if channel_caid in caidlist:
                                                 caidlist=[]
                                                 caidlist.append((str(channel_caid)))
                                                 appname = self.ci_cam
                                                 found_caid = True
                                                 break
                                              else:
                                                 appname = 'unsupported Cam/Card'
                                                 caid = str(channel_caid)
                                                 found_caid = False
                                      
                                      if found_caid:
                                         for entrie in caidlist:
                                             caid = '0x' + str(entrie)
                                      
                                      try:
                                         caid = caid.lstrip('0x')
                                         caid = caid.upper()
                                      except:
                                         caid = str('unknow')
                                         
                                      system = 'System: unknow'    
                                      if ((caid>='100') and (caid<='1FF')):
					     system = 'System: SECA'
                                      if ((caid>='500') and (caid<='5FF')):
			  		     system = 'System: VIACCESS'
                                      if ((caid>='600') and (caid<='6FF')):
					     system = 'System: IRDETO'
                                      if ((caid>='900') and (caid<='9FF')):
					     system = 'System: NDS'
                                      if ((caid>='B00') and (caid<='BFF')):
				             system = 'System: CONAX'
                                      if ((caid>='D00') and (caid<='DFF')):
					     system = 'System: CWORKS'
                                      if ((caid>='E00') and (caid<='EFF')):
					     system = 'System: POWERVU'
                                      if ((caid>='1700') and (caid<='17FF')):
					     system = 'System: BETA'
                                      if ((caid>='1800') and (caid<='18FF')):
					     system = 'System: NAGRA'
                                      
                                      ecmline = 'Slot ' + str(i) + ': ' + str(appname) + ' Caid: ' + str(caid.lower()) + ' ' + str(system)
                                      
                                   else:
				      ecmline = _('No CICam/Card/EMU available')
                                else:
				   ecmline = _('No CICam/Card/EMU available')
			else:
				camInfo = {}
				for line in flines:
					r = line.split(':', 1)
					if len(r) > 1 :
						camInfo[r[0].strip('\n\r\t ')] = r[1].strip('\n\r\t ')
	
				caid = camInfo.get('caid','')
				
				caid = caid.lstrip('0x')
				caid = caid.upper()
				caid = caid.zfill(4)
				
				if ((caid>='0100') and (caid<='01FF')):
					system = 'System: SECA'
				elif ((caid>='0500') and (caid<='05FF')):
					system = 'System: VIACCESS'
				elif ((caid>='0600') and (caid<='06FF')):
					system = 'System: IRDETO'
				elif ((caid>='0900') and (caid<='09FF')):
					system = 'System: NDS'
				elif ((caid>='0B00') and (caid<='0BFF')):
					system = 'System: CONAX'
				elif ((caid>='0D00') and (caid<='0DFF')):
					system = 'System: CWORKS'
				elif ((caid>='0E00') and (caid<='0EFF')):
					system = 'System: POWERVU'
				elif ((caid>='1700') and (caid<='17FF')):
					system = 'System: BETA'
				elif ((caid>='1800') and (caid<='18FF')):
					system = 'System: NAGRA'
				else:
					system = _('not available')
	
				caid = 'CAID: ' + caid
				
				prov = camInfo.get('prov','')
				prov = prov.lstrip("0x")
				prov = prov.upper()
				prov = prov.zfill(6)
				prov = 'Provider: ' + prov
				
				ecmtime = camInfo.get('ecm time','')
				if ecmtime:
					if "msec" in ecmtime:
						ecmtime = 'ECM: ' + ecmtime				
					else:
						ecmtime = 'ECM: ' + ecmtime	+ ' s'			
	
				hops = 'Hops: ' + str(camInfo.get('hops',''))
				address = 'Server: ' + str(camInfo.get('address',''))
				reader = 'Reader: ' + str(camInfo.get('reader',''))
				source = 'Source: ' + str(camInfo.get('source',''))
				
				using = str(camInfo.get('using',''))
	
				active = ''
				
				if  source == 'emu':
					active = 'EMU'
					ecmline = active + ' - ' + caid
				
				elif using == 'emu':
					active = 'EMU'
					if self.type == self.VERYSHORT:
						ecmline = caid + ', ' + ecmtime
					else:
						ecmline = active + ' - ' + caid + ' - ' + ecmtime
					
				elif 'system' in camInfo :
					active = 'CCCAM'
					if self.type == self.SATINFO:
						ecmline = caid + ', ' + ecmtime
					elif self.type == self.VERYSHORTCAID:
						ecmline = caid + ' - ' + ecmtime
					elif self.type == self.VERYSHORTREADER:
						ecmline = address + ' - ' + ecmtime
					elif self.type == self.SHORTHOPS:
						ecmline = caid + ' - ' + hops + ' - ' + ecmtime
					elif self.type == self.SHORTREADER:
						ecmline = caid + ' - ' + address + ' - ' + ecmtime
					elif self.type == self.NORMAL:
						ecmline = caid + ' - ' + address + ' - ' + hops + ' - ' + ecmtime					
					elif self.type == self.LONG:
						ecmline = caid + ' - ' + system + ' - ' + address + ' - ' + hops + ' - ' + ecmtime					
					else:
						ecmline = active + ' - ' + caid + ' - ' + system + ' - ' + address + ' - ' + hops + ' - ' + ecmtime					
	
				elif 'reader' in camInfo :
					active = 'OSCAM'
					if self.type == self.SATINFO:
						ecmline = caid + ', ' + ecmtime
					elif self.type == self.VERYSHORTCAID:
						ecmline = caid + ' - ' + ecmtime
					elif self.type == self.VERYSHORTREADER:
						ecmline = reader + ' - ' + ecmtime
					elif self.type == self.SHORTHOPS:
						ecmline = caid + ' - ' + hops + ' - ' + ecmtime
					elif self.type == self.SHORTREADER:
						ecmline = caid + ' - ' + reader + ' - ' + ecmtime
					elif self.type == self.NORMAL:
						ecmline = caid + ' - ' + reader + ' - ' + hops + ' - ' + ecmtime					
					elif self.type == self.LONG:
						ecmline = caid + ' - ' + system + ' - ' + reader + ' - ' + hops + ' - ' + ecmtime					
					else:
						ecmline = active + ' - ' + caid + ' - ' + system + ' - ' + reader + ' - ' + hops + ' - ' + ecmtime
	
				elif 'prov' in camInfo :
					active = 'MGCAMD'
					if self.type == self.SATINFO:
						ecmline = caid + ', ' + ecmtime
					elif self.type == self.VERYSHORTCAID:
						ecmline = caid + ' - ' + ecmtime
					elif self.type == self.VERYSHORTREADER:
						ecmline = source + ' - ' + ecmtime
					elif self.type == self.SHORTHOPS:
						ecmline = caid + ' - ' + ecmtime
					elif self.type == self.SHORTREADER:
						ecmline = caid + ' - ' + source + ' - ' + ecmtime
					elif self.type == self.NORMAL:
						ecmline = caid + ' - ' + source + ' - ' + prov + ' - ' + ecmtime					
					elif self.type == self.LONG:
						ecmline = caid + ' - ' + system + ' - ' + source + ' - ' + prov + ' - ' + ecmtime					
					else:
						ecmline = active + ' - ' + caid + ' - ' + system + ' - ' + source + ' - ' + prov + ' - ' + ecmtime
	
				else:
					active = 'Unknown'
					ecmline = _('not available')

		else:
			if self.invisible == self.FTAINVISIBLE:
				ecmline = ''
			else:
				ecmline = _('free to air')		
					
		return ecmline

	text = property(getText)

	@cached
	def IsCrypted(self):
		crypted = 0
		service = self.source.service
		if service:
			info = service and service.info()
			if info:
				crypted = info.getInfo(iServiceInformation.sIsCrypted)
		return crypted
	
	def get_system_caid(self):
		caidlist = []
                service = self.source.service
                if service:
                   info = service and service.info()
                   if info:
                      caids = info.getInfoObject(iServiceInformation.sCAIDs)
                      if caids:
                         for caid in caids:
                             caidlist.append((str(hex(int(caid)))))
                             
        	return caidlist
                	
	def changed(self, what):
		if (what[0] == self.CHANGED_SPECIFIC and what[1] == iPlayableService.evUpdatedInfo) or what[0] == self.CHANGED_POLL:
			Converter.changed(self, what)