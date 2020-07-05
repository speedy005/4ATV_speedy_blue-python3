# by nikolasi for maggy
from Tools.LoadPixmap import LoadPixmap 
from Renderer import Renderer 
from enigma import ePixmap, eTimer 
from Tools.Directories import fileExists
import os

class speedyAnimatedWeatherPixmap2(Renderer):
	__module__ = __name__
	
	def __init__(self):                
		Renderer.__init__(self)
		self.path = '/media/hdd/AnimatedWeatherPixmap'
		#self.path = '/media/usb/AnimatedWeatherPixmap'
		self.pixdelay = 100
		self.control = 1
		self.ftpcontrol = 1
		self.slideicon = None
		self.slideicon1 = None
		self.slideicon2 = None
		self.slideicon3 = None
		self.slideicon4 = None
		self.slideicon5 = None	
		self.datenow = 0
		self.datepast = 0
		self.datetuday = 0
		self.date2 = 0
		self.date3 = 0
		self.date4 = 0			
		self.txt_naim = {'8': '9', '1': '0', '2': '0', '3': '0', '4': '0', '17': '0', '35': '0', '16': '14', '42': '14', '43': '14', '40': '18', '24': '23', '29': '27', '33': '27' ,'30': '28' ,'34': '28' ,'38': '37' ,'25': '44'}
		
	def applySkin(self, desktop, parent):
		attribs = []
		for (attrib, value,) in self.skinAttributes:
		        if attrib == "path":
			      self.path = value                         
			elif attrib == "pixdelay":
				self.pixdelay = int(value)
			elif attrib == "ftpcontrol":
				self.ftpcontrol = int(value)				
			elif attrib == "control":
				self.control = int(value)
			elif attrib == "datenow":
				self.datenow = int(value)
			elif attrib == "datepast":
				self.datepast = int(value)
			elif attrib == "datetuday":
				self.datetuday = int(value)
			elif attrib == "date2":
				self.date2 = int(value)
			elif attrib == "date3":
				self.date3 = int(value)
			elif attrib == "date4":
				self.date4 = int(value)					
			else:
				attribs.append((attrib, value))
				
		self.skinAttributes = attribs
		return Renderer.applySkin(self, desktop, parent)
		
	GUI_WIDGET = ePixmap
	
	def changed(self, what):
	    if self.instance:
		sname = ''
		namenow = ''
		nameprow = ''
		nametuday = ''
		nameday2 = ''
		nameday3 = ''
		nameday4 = ''
		namepast = ''
		name = ''
		name2 = ''
		name3 = ''
		name4 = ''
		name5 = ''
		if (what[0] != self.CHANGED_CLEAR):
		     sname = self.source.text
		     if not "none" in sname:
                        namenow, nameprow, nametuday, nameday2, nameday3,  nameday4 = sname.split(',')
                        if self.datenow == 1:
                           name = self.txt_naim.get(namenow, namenow)
                        elif self.datepast == 1:
                           namepast = self.txt_naim.get(nameprow, nameprow)
                        elif self.datetuday == 1:
                           name2 = self.txt_naim.get(nametuday, nametuday)
                        elif self.date2 == 1:
                           name3 = self.txt_naim.get(nameday2, nameday2)
                        elif self.date3 == 1:
                           name4 = self.txt_naim.get(nameday3, nameday3)
                        elif self.date4 == 1:
                           name5 = self.txt_naim.get(nameday4, nameday4)                            
                        if self.ftpcontrol == 1:
                            if fileExists('/tmp/AnimatedWeatherPixmap'):
		               self.runAnim(name, namepast, name2, name3, name4, name5)
		            else:
                                self.dovloud(name, namepast, name2, name3, name4, name5)
		        else:
                            self.runAnim(name, namepast, name2, name3, name4, name5)

        def dovloud(self, name, namepast, name2, name3, name4, name5):
                os.system('wget -q ftp://satmoscow:r5tyWevlsjbj@sat.moscow/QuickWeather/AnimatedWeatherPixmap2.tar.gz -O /tmp/AnimatedWeatherPixmap2.tar.gz')
                os.system('tar xzvf /tmp/AnimatedWeatherPixmap2.tar.gz -C /')
                os.system('rm -rf /tmp/AnimatedWeatherPixmap2.tar.gz')
                self.runAnim(name, namepast, name2, name3, name4, name5)

        def runAnim(self, name, namepast, name2, name3, name4, name5):
            global total, total1, total2, total3, total4, total5
            animokicon = False
            if self.datenow == 1:
                if fileExists('%s/%s' % (self.path, name)):
                    pathanimicon = '%s/%s/a' % (self.path, name)
                    path = '%s/%s' % (self.path, name)
                    dir_work = os.listdir(path)
                    total = len(dir_work)
                    self.slideicon = total
                    animokicon = True
                else:
                    if fileExists('%s/NA' % self.path):    
                        pathanimicon = '%s/NA/a' % self.path
                        path = '%s/NA'  % self.path
                        dir_work = os.listdir(path)
                        total = len(dir_work)
                        self.slideicon = total
                        animokicon = True
                if animokicon == True:
                    self.picsicon = []
                    for x in range(self.slideicon):
                        self.picsicon.append(LoadPixmap(pathanimicon + str(x) + '.png'))
                    self.timericon = eTimer()
                    self.timericon.callback.append(self.timerEvent)
                    self.timericon.start(100, True)
            elif self.datepast == 1:
                if fileExists('%s/%s' % (self.path, namepast)):
                    pathanimicon1 = '%s/%s/a' % (self.path, namepast)
                    path1 = '%s/%s' % (self.path, namepast)
                    dir_work1 = os.listdir(path1)
                    total1 = len(dir_work1)
                    self.slideicon1 = total1
                    animokicon = True
                else:
                    if fileExists('%s/NA' % self.path):    
                        pathanimicon1 = '%s/NA/a' % self.path
                        path1 = '%s/NA'  % self.path
                        dir_work1 = os.listdir(path1)
                        total1 = len(dir_work1)
                        self.slideicon1 = total1
                        animokicon = True
                if animokicon == True:
                    self.picsicon1 = []
                    for x in range(self.slideicon1):
                        self.picsicon1.append(LoadPixmap(pathanimicon1 + str(x) + '.png'))
                    self.timericon1 = eTimer()
                    self.timericon1.callback.append(self.timerEvent1)
                    self.timericon1.start(100, True)
            elif self.datetuday == 1:
                if fileExists('%s/%s' % (self.path, name2)):
                    pathanimicon2 = '%s/%s/a' % (self.path, name2)
                    path2 = '%s/%s' % (self.path, name2)
                    dir_work2 = os.listdir(path2)
                    total2 = len(dir_work2)
                    self.slideicon2 = total2
                    animokicon = True
                else:
                    if fileExists('%s/NA' % self.path):    
                        pathanimicon2 = '%s/NA/a' % self.path
                        path2 = '%s/NA'  % self.path
                        dir_work2 = os.listdir(path2)
                        total2 = len(dir_work2)
                        self.slideicon2 = total2
                        animokicon = True
                if animokicon == True:
                    self.picsicon2 = []
                    for x in range(self.slideicon2):
                        self.picsicon2.append(LoadPixmap(pathanimicon2 + str(x) + '.png'))
                    self.timericon2 = eTimer()
                    self.timericon2.callback.append(self.timerEvent2)
                    self.timericon2.start(100, True)
            elif self.date2 == 1:
                if fileExists('%s/%s' % (self.path, name3)):
                    pathanimicon3 = '%s/%s/a' % (self.path, name3)
                    path3 = '%s/%s' % (self.path, name3)
                    dir_work3 = os.listdir(path3)
                    total3 = len(dir_work3)
                    self.slideicon3 = total3
                    animokicon = True
                else:
                    if fileExists('%s/NA' % self.path):    
                        pathanimicon3 = '%s/NA/a' % self.path
                        path3 = '%s/NA'  % self.path
                        dir_work3 = os.listdir(path3)
                        total3 = len(dir_work3)
                        self.slideicon3 = total3
                        animokicon = True
                if animokicon == True:
                    self.picsicon3 = []
                    for x in range(self.slideicon3):
                        self.picsicon3.append(LoadPixmap(pathanimicon3 + str(x) + '.png'))
                    self.timericon3 = eTimer()
                    self.timericon3.callback.append(self.timerEvent3)
                    self.timericon3.start(100, True)
            elif self.date3 == 1:
                if fileExists('%s/%s' % (self.path, name4)):
                    pathanimicon4 = '%s/%s/a' % (self.path, name4)
                    path4 = '%s/%s' % (self.path, name4)
                    dir_work4 = os.listdir(path4)
                    total4 = len(dir_work4)
                    self.slideicon4 = total4
                    animokicon = True
                else:
                    if fileExists('%s/NA' % self.path):    
                        pathanimicon4 = '%s/NA/a' % self.path
                        path4 = '%s/NA'  % self.path
                        dir_work4 = os.listdir(path4)
                        total4 = len(dir_work4)
                        self.slideicon4 = total4
                        animokicon = True
                if animokicon == True:
                    self.picsicon4 = []
                    for x in range(self.slideicon4):
                        self.picsicon4.append(LoadPixmap(pathanimicon4 + str(x) + '.png'))
                    self.timericon4 = eTimer()
                    self.timericon4.callback.append(self.timerEvent4)
                    self.timericon4.start(100, True)     
            elif self.date4 == 1:
                if fileExists('%s/%s' % (self.path, name5)):
                    pathanimicon5 = '%s/%s/a' % (self.path, name5)
                    path5 = '%s/%s' % (self.path, name5)
                    dir_work5 = os.listdir(path5)
                    total5 = len(dir_work5)
                    self.slideicon5 = total5
                    animokicon = True
                else:
                    if fileExists('%s/NA' % self.path):    
                        pathanimicon5 = '%s/NA/a' % self.path
                        path5 = '%s/NA'  % self.path
                        dir_work5 = os.listdir(path5)
                        total5 = len(dir_work5)
                        self.slideicon5 = total5
                        animokicon = True
                if animokicon == True:
                    self.picsicon5 = []
                    for x in range(self.slideicon5):
                        self.picsicon5.append(LoadPixmap(pathanimicon5 + str(x) + '.png'))
                    self.timericon5 = eTimer()
                    self.timericon5.callback.append(self.timerEvent5)
                    self.timericon5.start(100, True)   	        

        def timerEvent(self):
                if self.slideicon == 0:
                        self.slideicon = total
                self.timericon.stop()
                self.instance.setScale(1)
                self.instance.setPixmap(self.picsicon[self.slideicon - 1])
                self.slideicon = self.slideicon - 1
                self.timericon.start(self.pixdelay, True)

        def timerEvent1(self):
                if self.slideicon1 == 0:
                        self.slideicon1 = total1
                self.timericon1.stop()
                self.instance.setScale(1)
                self.instance.setPixmap(self.picsicon1[self.slideicon1 - 1])
                self.slideicon1 = self.slideicon1 - 1
                self.timericon1.start(self.pixdelay, True)

        def timerEvent2(self):
                if self.slideicon2 == 0:
                        self.slideicon2 = total2
                self.timericon2.stop()
                self.instance.setScale(1)
                self.instance.setPixmap(self.picsicon2[self.slideicon2 - 1])
                self.slideicon2 = self.slideicon2 - 1
                self.timericon2.start(self.pixdelay, True)

        def timerEvent3(self):
                if self.slideicon3 == 0:
                        self.slideicon3 = total3
                self.timericon3.stop()
                self.instance.setScale(1)
                self.instance.setPixmap(self.picsicon3[self.slideicon3 - 1])
                self.slideicon3 = self.slideicon3 - 1
                self.timericon3.start(self.pixdelay, True)

        def timerEvent4(self):
                if self.slideicon4 == 0:
                        self.slideicon4 = total4
                self.timericon4.stop()
                self.instance.setScale(1)
                self.instance.setPixmap(self.picsicon4[self.slideicon4 - 1])
                self.slideicon4 = self.slideicon4 - 1
                self.timericon4.start(self.pixdelay, True)

        def timerEvent5(self):
                if self.slideicon5 == 0:
                        self.slideicon5 = total5
                self.timericon5.stop()
                self.instance.setScale(1)
                self.instance.setPixmap(self.picsicon5[self.slideicon5 - 1])
                self.slideicon5 = self.slideicon5 - 1
                self.timericon5.start(self.pixdelay, True)                  
