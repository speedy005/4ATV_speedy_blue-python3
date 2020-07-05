# Embedded file name: /usr/lib/enigma2/python/Components/Converter/VtiInfo.py
from Components.config import config
from Components.Converter.Converter import Converter
from enigma import iServiceInformation, iPlayableService, eServiceCenter, eServiceReference, iServiceInformation
from Components.Element import cached
from Poll import Poll
from xml.etree.cElementTree import parse
from Screens.InfoBar import InfoBar
from ServiceReference import ServiceReference
from Components.ServiceEventTracker import ServiceEventTracker

class speedyInfo(Poll, Converter, object):
    NUMBER = 0
    ECMINFO = 1
    IRDCRYPT = 2
    SECACRYPT = 3
    NAGRACRYPT = 4
    VIACRYPT = 5
    CONAXCRYPT = 6
    BETACRYPT = 7
    CRWCRYPT = 8
    DREAMCRYPT = 9
    NDSCRYPT = 10
    IRDECM = 11
    SECAECM = 12
    NAGRAECM = 13
    VIAECM = 14
    CONAXECM = 15
    BETAECM = 16
    CRWECM = 17
    DREAMECM = 18
    NDSECM = 19
    CAIDINFO = 20
    ONLINETEST = 21
    ALL = 22

    def __init__(self, type):
        Poll.__init__(self)
        Converter.__init__(self, type)
        self.type = type
        self.getLists()
        self.systemCaids = {'06': 'I',
         '01': 'S',
         '18': 'N',
         '05': 'V',
         '0B': 'CO',
         '17': 'BC',
         '0D': 'CW',
         '4A': 'DC',
         '55': 'BG',
         '09': 'NDS'}
        self.poll_interval = 2000
        self.poll_enabled = True
        if type == 'Number':
            self.type = self.NUMBER
        elif type == 'EcmInfo':
            self.type = self.ECMINFO
        elif type == 'IrdCrypt':
            self.type = self.IRDCRYPT
        elif type == 'SecaCrypt':
            self.type = self.SECACRYPT
        elif type == 'NagraCrypt':
            self.type = self.NAGRACRYPT
        elif type == 'ViaCrypt':
            self.type = self.VIACRYPT
        elif type == 'ConaxCrypt':
            self.type = self.CONAXCRYPT
        elif type == 'BetaCrypt':
            self.type = self.BETACRYPT
        elif type == 'CrwCrypt':
            self.type = self.CRWCRYPT
        elif type == 'DreamCrypt':
            self.type = self.DREAMCRYPT
        elif type == 'NdsCrypt':
            self.type = self.NDSCRYPT
        elif type == 'IrdEcm':
            self.type = self.IRDECM
        elif type == 'SecaEcm':
            self.type = self.SECAECM
        elif type == 'NagraEcm':
            self.type = self.NAGRAECM
        elif type == 'ViaEcm':
            self.type = self.VIAECM
        elif type == 'ConaxEcm':
            self.type = self.CONAXECM
        elif type == 'BetaEcm':
            self.type = self.BETAECM
        elif type == 'CrwEcm':
            self.type = self.CRWECM
        elif type == 'DreamEcm':
            self.type = self.DREAMECM
        elif type == 'NdsEcm':
            self.type = self.NDSECM
        elif type == 'OnlineTest':
            self.type = self.ONLINETEST
        else:
            self.type = self.ALL

    @cached
    def get_caidlist(self):
        caidlist = {}
        service = self.source.service
        if service:
            if service:
                info = service.info()
                if info:
                    caids = info.getInfoObject(iServiceInformation.sCAIDs)
                    if caids:
                        for cs in self.systemCaids:
                            caidlist[cs] = (self.systemCaids.get(cs), 0)

                        for caid in caids:
                            c = '%x' % int(caid)
                            if len(c) == 3:
                                c = '0%s' % c
                            c = c[:2].upper()
                            if self.systemCaids.has_key(c):
                                caidlist[c] = (self.systemCaids.get(c), 1)

                        ecm_info = self.ecmfile()
                        if ecm_info:
                            emu_caid = ecm_info.get('caid', '')
                            if emu_caid and emu_caid != '0x000':
                                c = emu_caid.lstrip('0x')
                                c = len(c) == 3 and '0%s' % c
                            c = c[:2].upper()
                            caidlist[c] = (self.systemCaids.get(c), 2)
        return caidlist

    getCaidlist = property(get_caidlist)

    @cached
    def getText(self):
        textvalue = ''
        service = self.source.service
        if service and service:
            info = service.info()
            SelChannel = InfoBar.instance.servicelist
            BouquetRootIdx = SelChannel.getBouquetNumOffset(SelChannel.getRoot())
            number = self.getServiceNumber(BouquetRootIdx, info.getInfoString(iServiceInformation.sServiceref))
            if self.type == self.NUMBER:
                textvalue = number
            elif self.type == self.ECMINFO:
                if info:
                    if info.getInfoObject(iServiceInformation.sCAIDs):
                        ecm_info = self.ecmfile()
                        if ecm_info:
                            caid = ecm_info.get('caid', '')
                            caid = caid.lstrip('0x')
                            caid = caid.upper()
                            caid = caid.zfill(4)
                            caid = 'CAID: %s' % caid
                            hops = ecm_info.get('hops', None)
                            hops = 'HOPS: %s' % hops
                            ecm_time = ecm_info.get('ecm time', None)
                            if ecm_time:
                                if 'msec' in ecm_time:
                                    ecm_time = 'ECM: %s ms' % ecm_time
                                else:
                                    ecm_time = 'ECM: %s s' % ecm_time
                            address = ecm_info.get('address', '')
                            using = ecm_info.get('using', '')
                            if using:
                                if using == 'emu':
                                    textvalue = '(EMU) %s - %s' % (caid, ecm_time)
                                elif using == 'CCcam-s2s':
                                    textvalue = '(NET) %s - %s - %s - %s' % (caid,
                                     address,
                                     hops,
                                     ecm_time)
                                else:
                                    textvalue = '%s - %s - %s - %s' % (caid,
                                     address,
                                     hops,
                                     ecm_time)
                            else:
                                source = ecm_info.get('source', None)
                                if source:
                                    if source == 'emu':
                                        textvalue = '(EMU) %s' % caid
                                    else:
                                        textvalue = '%s - %s - %s' % (caid, source, ecm_time)
                                oscsource = ecm_info.get('from', None)
                                if oscsource:
                                    textvalue = '%s - %s - %s - %s' % (caid,
                                     oscsource,
                                     hops,
                                     ecm_time)
                                decode = ecm_info.get('decode', None)
                                if decode:
                                    if decode == 'Internal':
                                        textvalue = '(EMU) %s' % caid
                                    else:
                                        textvalue = '%s - %s' % (caid, decode)
        return textvalue

    text = property(getText)

    @cached
    def getBoolean(self):
        service = self.source.service
        if service:
            info = service.info()
            if not info:
                return False
            if self.type == self.IRDCRYPT:
                caemm = self.possiblecaid('06')
                return caemm
            if self.type == self.SECACRYPT:
                caemm = self.possiblecaid('01')
                return caemm
            if self.type == self.NAGRACRYPT:
                caemm = self.possiblecaid('18')
                return caemm
            if self.type == self.VIACRYPT:
                caemm = self.possiblecaid('05')
                return caemm
            if self.type == self.CONAXCRYPT:
                caemm = self.possiblecaid('0B')
                return caemm
            if self.type == self.BETACRYPT:
                caemm = self.possiblecaid('17')
                return caemm
            if self.type == self.CRWCRYPT:
                caemm = self.possiblecaid('0D')
                return caemm
            if self.type == self.DREAMCRYPT:
                caemm = self.possiblecaid('4A')
                return caemm
            if self.type == self.NDSCRYPT:
                caemm = self.possiblecaid('09')
                return caemm
            if self.type == self.IRDECM:
                caemm = self.usedcaid('06')
                return caemm
            if self.type == self.SECAECM:
                caemm = self.usedcaid('01')
                return caemm
            if self.type == self.NAGRAECM:
                caemm = self.usedcaid('18')
                return caemm
            if self.type == self.VIAECM:
                caemm = self.usedcaid('05')
                return caemm
            if self.type == self.CONAXECM:
                caemm = self.usedcaid('0B')
                return caemm
            if self.type == self.BETAECM:
                caemm = self.usedcaid('17')
                return caemm
            if self.type == self.CRWECM:
                caemm = self.usedcaid('0D')
                return caemm
            if self.type == self.DREAMECM:
                caemm = self.usedcaid('4A')
                return caemm
            if self.type == self.NDSECM:
                caemm = self.usedcaid('09')
                return caemm
            onlinecheck = self.type == self.ONLINETEST and self.pingtest()
            return onlinecheck
        return False

    boolean = property(getBoolean)

    def ecmfile(self):
        ecm = None
        info = {}
        service = self.source.service
        if service:
            frontendInfo = service.frontendInfo()
            if frontendInfo:
                try:
                    ecmpath = '/tmp/ecm%s.info' % frontendInfo.getAll(False).get('tuner_number')
                    ecm = open(ecmpath, 'rb').readlines()
                except:
                    try:
                        ecm = open('/tmp/ecm.info', 'rb').readlines()
                    except:
                        pass

            if ecm:
                for line in ecm:
                    x = line.lower().find('msec')
                    if x != -1:
                        info['ecm time'] = line[0:x + 4]
                    else:
                        item = line.split(':', 1)
                        if len(item) > 1:
                            info[item[0].strip().lower()] = item[1].strip()
                        elif not info.has_key('caid'):
                            x = line.lower().find('caid')
                            if x != -1:
                                y = line.find(',')
                                if y != -1:
                                    info['caid'] = line[x + 5:y]

        return info

    def changed(self, what):
        if what[0] == self.CHANGED_SPECIFIC and what[1] == iPlayableService.evUpdatedInfo or what[0] == self.CHANGED_POLL:
            Converter.changed(self, what)

    def getListFromRef(self, ref):
        list = []
        serviceHandler = eServiceCenter.getInstance()
        services = serviceHandler.list(ref)
        bouquets = services and services.getContent('SN', True)
        for bouquet in bouquets:
            services = serviceHandler.list(eServiceReference(bouquet[0]))
            channels = services and services.getContent('SN', True)
            for channel in channels:
                if not channel[0].startswith('1:64:'):
                    list.append(str(channel[0]))

        return list

    def getLists(self):
        self.tv_list = self.getListFromRef(eServiceReference('1:7:1:0:0:0:0:0:0:0:(type == 1) || (type == 17) || (type == 195) || (type == 211) || (type == 25) FROM BOUQUET "bouquets.tv" ORDER BY bouquet'))
        self.radio_list = self.getListFromRef(eServiceReference('1:7:2:0:0:0:0:0:0:0:(type == 2) FROM BOUQUET "bouquets.radio" ORDER BY bouquet'))

    def getServiceNumber(self, BouquetRootIdx, ref):
        list = []
        if ref.startswith('1:0:2'):
            list = self.radio_list
        elif ref.startswith('1:0:1') or ref.startswith('1:0:D'):
            list = self.tv_list
        number = ''
        if ref in list:
            for idx in range(1, len(list) + 1):
                if BouquetRootIdx == len(list):
                    if ref == list[idx - 1]:
                        number = str(idx)
                        break
                elif ref == list[idx - 1] and idx >= BouquetRootIdx:
                    number = str(idx)
                    break

        return number

    def usedcaid(self, caidnow):
        caidlist = self.getCaidlist
        for key in caidlist:
            if caidlist[key][1] == 2:
                if key == caidnow:
                    return True

        return False

    def possiblecaid(self, caidnow):
        caidlist = self.getCaidlist
        for key in caidlist:
            if caidlist[key][1] == 1:
                if key == caidnow:
                    return True

        return False

    def pingtest(self):
        pingpath = '/tmp/.pingtest.info'
        try:
            pingtestresult = open(pingpath, 'rb').readlines()
            for line in pingtestresult:
                x = line.lower().find('0')
                print x
                if x == 0:
                    pingtestresult = 0
                else:
                    pingtestresult = 1

            if pingtestresult == 0:
                return True
        except:
            pass

        return False