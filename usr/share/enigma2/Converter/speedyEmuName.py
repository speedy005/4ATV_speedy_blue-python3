# Embedded file name: /usr/lib/enigma2/python/Components/Converter/blueEmuName.py
from enigma import iServiceInformation
from Components.Converter.Converter import Converter
from Components.ConfigList import ConfigListScreen
from Components.config import config, getConfigListEntry, ConfigText, ConfigPassword, ConfigClock, ConfigSelection, ConfigSubsection, ConfigYesNo, configfile, NoSave
from Components.Element import cached
from Tools.Directories import fileExists
from Poll import Poll
from cStringIO import StringIO
import os

class speedyEmuName(Poll, Converter, object):

    def __init__(self, type):
        Converter.__init__(self, type)
        Poll.__init__(self)
        self.poll_interval = 2000
        self.poll_enabled = True

    @cached
    def getText(self):
        info = info2 = ''
        nofile = False
        camdname = cardname = camdlist = None
        if fileExists('/usr/lib/enigma2/python/Plugins/Extensions/AlternativeSoftCamManager/plugin.py'):
            if config.plugins.AltSoftcam.actcam.value != 'none':
                camdname = StringIO(config.plugins.AltSoftcam.actcam.value)
            else:
                camdname = None
        elif fileExists('/etc/image-version') and not fileExists('/etc/.emustart') and not fileExists('/etc/init.d/softcam') and not fileExists('/etc/init.d/cardserver'):
            if fileExists('/etc/issue'):
                for line in open('/etc/issue'):
                    if 'openatv' in line.lower():
                        if config.softcam.actCam.value:
                            camdname = StringIO(config.softcam.actCam.value)

        elif fileExists('/tmp/.emu.info'):
            try:
                camdname = open('/tmp/.emu.info', 'r')
            except:
                camdname = None

        elif fileExists('/etc/startcam.sh'):
            try:
                camdname = open('/etc/startcam.sh', 'r')
            except:
                camdname = None

        elif fileExists('/etc/CurrentBhCamName'):
            try:
                camdname = open('/etc/CurrentBhCamName', 'r')
            except:
                camdname = None

        elif fileExists('/etc/active_emu.list'):
            try:
                camdname = open('/etc/active_emu.list', 'r')
            except:
                camdname = None

        elif fileExists('/tmp/cam.info'):
            try:
                camdname = open('/tmp/cam.info', 'r')
            except:
                camdname = None

        elif fileExists('/etc/clist.list'):
            try:
                camdname = open('/etc/clist.list', 'r')
            except:
                camdname = None

        elif fileExists('/usr/lib/enigma2/python/Plugins/Bp/geminimain/lib/libgeminimain.so'):
            try:
                from Plugins.Bp.geminimain.plugin import GETCAMDLIST
                from Plugins.Bp.geminimain.lib import libgeminimain
                camdl = libgeminimain.getPyList(GETCAMDLIST)
                cam = None
                for x in camdl:
                    if x[1] == 1:
                        cam = x[2]

                camdname = cam
                nofile = True
            except:
                camdname = None

        elif fileExists('/etc/init.d/softcam') or fileExists('/etc/init.d/cardserver'):
            try:
                camdname = open('/etc/init.d/softcam', 'r')
            except:
                camdname = None

            try:
                cardname = open('/etc/init.d/cardserver', 'r')
            except:
                cardname = None

        elif fileExists('/etc/.emustart'):
            try:
                camdname = open('/etc/.emustart', 'r')
            except:
                camdname = None

        if cardname:
            for line in cardname:
                if 'oscam' in line.lower():
                    info2 = 'oscam'
                elif 'newcs' in line.lower():
                    info2 = 'newcs'
                elif 'wicard' in line.lower():
                    info2 = 'wicardd'
                elif 'cccam' in line.lower():
                    info2 = 'cccam'
                elif 'mgcamd' in line.lower():
                    info2 = 'mgcamd'

            cardname.close()
        if camdname:
            camdlist = camdname
        if camdlist:
            info = 'unknow'
            if nofile:
                if nofile:
                    line = camdlist
            else:
                for line in camdlist:
                    if 'mgcamd' in line.lower() and 'oscam' in line.lower():
                        info = 'oscammgcamd'
                        break
                    if 'cccam' in line.lower() and 'oscam' in line.lower():
                        info = 'oscamcccam'
                        break
                    elif 'mgcamd' in line.lower():
                        info = 'mgcamd'
                    elif 'oscam' in line.lower():
                        info = 'oscam'
                    elif 'ncam' in line.lower():
                        info = 'ncam'
                    elif 'gcam' in line.lower():
                        info = 'gcam'
                    elif 'wicard' in line.lower():
                        info = 'wicardd'
                    elif 'cccam' in line.lower():
                        info = 'cccam'
                    elif 'camd3' in line.lower():
                        info = 'camd3'
                    elif 'evocamd' in line.lower():
                        info = 'evocamd'
                    elif 'newcs' in line.lower():
                        info = 'newcs'
                    elif 'rqcamd' in line.lower():
                        info = 'rqcamd'
                    elif 'gbox' in line.lower():
                        info = 'gbox'
                    elif 'mpcs' in line.lower():
                        info = 'mpcs'
                    elif 'sbox' in line.lower():
                        info = 'sbox'

        if camdname and not nofile:
            camdname.close()
        return info2 + info

    text = property(getText)

    def changed(self, what):
        Converter.changed(self, (self.CHANGED_POLL,))