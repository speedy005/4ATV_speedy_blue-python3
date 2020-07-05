# Embedded file name: /usr/lib/enigma2/python/Components/Converter/blueBase.py
from Components.Converter.Converter import Converter
from Components.Element import cached
from Poll import Poll
import NavigationInstance
from ServiceReference import ServiceReference, resolveAlternate
from enigma import iServiceInformation, iPlayableService, iPlayableServicePtr, eServiceCenter
from string import upper
from Tools.Transponder import ConvertToHumanReadable
from Components.config import config
from Tools.Directories import fileExists

def sp(text):
    if text:
        text += ' '
    return text


codecs = {-1: 'N/A',
 0: 'MPEG2',
 1: 'AVC',
 2: 'H263',
 3: 'VC1',
 4: 'MPEG4-VC',
 5: 'VC1-SM',
 6: 'MPEG1',
 7: 'HEVC',
 8: 'VP8',
 9: 'VP9',
 10: 'XVID',
 11: 'N/A 11',
 12: 'N/A 12',
 13: 'DIVX 3.11',
 14: 'DIVX 4',
 15: 'DIVX 5',
 16: 'AVS',
 17: 'N/A 17',
 18: 'VP6',
 19: 'N/A 19',
 20: 'N/A 20',
 21: 'SPARK'}

class speedyBase(Poll, Converter, object):
    FREQINFO = 0
    RESCODEC = 1
    PIDINFO = 2
    PIDHEXINFO = 3
    VIDEOCODEC = 4
    FPS = 5
    VIDEOSIZE = 6
    IS1080 = 7
    IS720 = 8
    IS576 = 9
    IS1440 = 10
    IS2160 = 11
    IS480 = 12
    IS360 = 13
    ISPROGRESSIVE = 14
    ISINTERLACED = 15
    STREAMURL = 16
    STREAMTYPE = 17
    ISSTREAMING = 18
    HASMPEG2 = 19
    HASAVC = 20
    HASH263 = 21
    HASVC1 = 22
    HASMPEG4VC = 23
    HASHEVC = 24
    HASMPEG1 = 25
    HASVP8 = 26
    HASVP9 = 27
    HASVP6 = 28
    HASDIVX = 29
    HASXVID = 30
    HASSPARK = 31
    HASAVS = 32
    ISSDR = 33
    ISHDR = 34
    ISHDR10 = 35
    ISHLG = 36
    HDRINFO = 37

    def __init__(self, type):
        Converter.__init__(self, type)
        self.type = type
        self.short_list = True
        Poll.__init__(self)
        self.poll_interval = 1000
        self.poll_enabled = True
        self.list = []
        if 'FreqInfo' in type:
            self.type = self.FREQINFO
        elif 'ResCodec' in type:
            self.type = self.RESCODEC
        elif 'VideoCodec' in type:
            self.type = self.VIDEOCODEC
        elif 'Fps' in type:
            self.type = self.FPS
        elif 'VideoSize' in type:
            self.type = self.VIDEOSIZE
        elif 'PidInfo' in type:
            self.type = self.PIDINFO
        elif 'PidHexInfo' in type:
            self.type = self.PIDHEXINFO
        elif 'Is1080' in type:
            self.type = self.IS1080
        elif 'Is720' in type:
            self.type = self.IS720
        elif 'Is576' in type:
            self.type = self.IS576
        elif 'Is1440' in type:
            self.type = self.IS1440
        elif 'Is2160' in type:
            self.type = self.IS2160
        elif 'Is480' in type:
            self.type = self.IS480
        elif 'Is360' in type:
            self.type = self.IS360
        elif 'IsProgressive' in type:
            self.type = self.ISPROGRESSIVE
        elif 'IsInterlaced' in type:
            self.type = self.ISINTERLACED
        elif 'StreamUrl' in type:
            self.type = self.STREAMURL
        elif 'StreamType' in type:
            self.type = self.STREAMTYPE
        elif 'IsStreaming' in type:
            self.type = self.ISSTREAMING
        elif 'HasMPEG2' in type:
            self.type = self.HASMPEG2
        elif 'HasAVC' in type:
            self.type = self.HASAVC
        elif 'HasH263' in type:
            self.type = self.HASH263
        elif 'HasVC1' in type:
            self.type = self.HASVC1
        elif 'HasMPEG4VC' in type:
            self.type = self.HASMPEG4VC
        elif 'HasHEVC' in type:
            self.type = self.HASHEVC
        elif 'HasMPEG1' in type:
            self.type = self.HASMPEG1
        elif 'HasVP8' in type:
            self.type = self.HASVP8
        elif 'HasVP9' in type:
            self.type = self.HASVP9
        elif 'HasVP6' in type:
            self.type = self.HASVP6
        elif 'HasDIVX' in type:
            self.type = self.HASDIVX
        elif 'HasXVID' in type:
            self.type = self.HASXVID
        elif 'HasSPARK' in type:
            self.type = self.HASSPARK
        elif 'HasAVS' in type:
            self.type = self.HASAVS
        elif 'IsSDR' in type:
            self.type = self.ISSDR
        elif 'IsHDR' in type:
            self.type = self.ISHDR
        elif 'IsHDR10' in type:
            self.type = self.ISHDR10
        elif 'IsHLG' in type:
            self.type = self.ISHLG
        elif 'HDRInfo' in type:
            self.type = self.HDRINFO

    def videosize(self, info):
        xresol = info.getInfo(iServiceInformation.sVideoWidth)
        yresol = info.getInfo(iServiceInformation.sVideoHeight)
        progrs = ('i', 'p', '', ' ')[info.getInfo(iServiceInformation.sProgressive)]
        if xresol > 0:
            videosize = str(xresol) + 'x' + str(yresol) + str(progrs)
            return videosize
        else:
            return ''

    def framerate(self, info):
        fps = info.getInfo(iServiceInformation.sFrameRate)
        if fps < 0 or fps == -1:
            return ''
        fps = '%6.3f' % (fps / 1000.0)
        return str(fps.replace('.000', '')) + ' fps '

    def videocodec(self, info):
        vcodec = codecs.get(info.getInfo(iServiceInformation.sVideoType), 'N/A')
        return str(vcodec)

    def hdr(self, info):
        try:
            gamma = ('SDR', 'HDR', 'HDR10', 'HLG', '')[info.getInfo(iServiceInformation.sGamma)]
        except:
            gamma = None

        if gamma:
            return str(gamma)
        else:
            return ''
            return

    def frequency(self, tp):
        freq = tp.get('frequency') + 500
        if freq:
            frequency = str(int(freq) / 1000)
            return frequency
        else:
            return ''

    def terrafreq(self, tp):
        return str(int(tp.get('frequency') + 1) / 1000000)

    def channel(self, tpinfo):
        return str(tpinfo.get('channel')) or ''

    def symbolrate(self, tp):
        return str(int(tp.get('symbol_rate', 0) / 1000))

    def polarization(self, tpinfo):
        return str(tpinfo.get('polarization_abbreviation')) or ''

    def fecinfo(self, tpinfo):
        return str(tpinfo.get('fec_inner')) or ''

    def tunernumber(self, tpinfo):
        return str(tpinfo.get('tuner_number')) or ''

    def system(self, tpinfo):
        return str(tpinfo.get('system')) or ''

    def modulation(self, tpinfo):
        return str(tpinfo.get('modulation')) or ''

    def constellation(self, tpinfo):
        return str(tpinfo.get('constellation'))

    def tunersystem(self, tpinfo):
        return str(tpinfo.get('system')) or ''

    def tunertype(self, tp):
        return str(tp.get('tuner_type')) or ''

    def terrafec(self, tpinfo):
        return sp('LP:') + sp(str(tpinfo.get('code_rate_lp'))) + sp('HP:') + sp(str(tpinfo.get('code_rate_hp'))) + sp('GI:') + sp(str(tpinfo.get('guard_interval')))

    def plpid(self, tpinfo):
        plpid = str(tpinfo.get('plp_id', 0))
        if plpid == 'None' or plpid == '-1':
            return ''
        else:
            return 'PLP ID:' + plpid

    def t2mi_info(self, tpinfo):
        try:
            t2mi_id = str(tpinfo.get('t2mi_plp_id'))
            if fileExists('/etc/image-version'):
                if t2mi_id == 'None' or t2mi_id == '-1' or t2mi_id == '0':
                    return ''
                else:
                    return 'T2MI PLP:' + t2mi_id
            else:
                if t2mi_id == 'None' or t2mi_id == '-1':
                    return ''
                return 'T2MI PLP:' + t2mi_id
        except:
            return ''

    def multistream(self, tpinfo):
        isid = str(tpinfo.get('is_id', 0))
        plscode = str(tpinfo.get('pls_code', 0))
        plsmode = str(tpinfo.get('pls_mode', None))
        if plsmode == 'None' or plsmode == 'Unknown' or plsmode is not 'None' and plscode == '0':
            plsmode = ''
        if isid == 'None' or isid == '-1' or isid == '0':
            isid = ''
        else:
            isid = 'IS:' + isid
        if plscode == 'None' or plscode == '-1' or plscode == '0':
            plscode = ''
        if plscode == '0' and plsmode == 'Gold' or plscode == '1' and plsmode == 'Root':
            return isid
        else:
            return sp(isid) + sp(plsmode) + sp(plscode)
            return

    def reference(self):
        playref = NavigationInstance.instance.getCurrentlyPlayingServiceReference()
        if playref:
            refstr = playref.toString() or ''
            return refstr

    def streamtype(self):
        playref = NavigationInstance.instance.getCurrentlyPlayingServiceReference()
        if playref:
            refstr = playref.toString()
            strtype = refstr.replace('%3a', ':')
            if '0.0.0.0:' in strtype and strtype.startswith('1:0:') or '127.0.0.1:' in strtype and strtype.startswith('1:0:') or 'localhost:' in strtype and strtype.startswith('1:0:'):
                return 'Internal TS Relay'
            elif not strtype.startswith('1:0:'):
                return 'IPTV/Non-TS Stream'
            elif '%3a/' in refstr and strtype.startswith('1:0:'):
                return 'IPTV/TS Stream'
            elif strtype.startswith('1:134:'):
                return 'Alternative'
            else:
                return ''

    def streamurl(self):
        playref = NavigationInstance.instance.getCurrentlyPlayingServiceReference()
        if playref:
            refstr = playref.toString()
            if '%3a/' in refstr or ':/' in refstr:
                strurl = refstr.split(':')
                streamurl = strurl[10].replace('%3a', ':')
                return streamurl
            else:
                return ''

    def pidstring(self, info):
        vpid = info.getInfo(iServiceInformation.sVideoPID)
        if vpid < 0:
            vpid = ''
        else:
            vpid = 'VPID:' + str(vpid).zfill(4)
        apid = info.getInfo(iServiceInformation.sAudioPID)
        if apid < 0:
            apid = ''
        else:
            apid = 'APID:' + str(apid).zfill(4)
        sid = info.getInfo(iServiceInformation.sSID)
        if sid < 0:
            sid = ''
        else:
            sid = 'SID:' + str(sid).zfill(4)
        pcrpid = info.getInfo(iServiceInformation.sPCRPID)
        if pcrpid < 0:
            pcrpid = ''
        else:
            pcrpid = 'PCR:' + str(pcrpid).zfill(4)
        pmtpid = info.getInfo(iServiceInformation.sPMTPID)
        if pmtpid < 0:
            pmtpid = ''
        else:
            pmtpid = 'PMT:' + str(pmtpid).zfill(4)
        tsid = info.getInfo(iServiceInformation.sTSID)
        if tsid < 0:
            tsid = ''
        else:
            tsid = 'TSID:' + str(tsid).zfill(4)
        onid = info.getInfo(iServiceInformation.sONID)
        if onid < 0:
            onid = ''
        else:
            onid = 'ONID:' + str(onid).zfill(4)
        if vpid >= 0 or apid >= 0 or sid >= 0 or tsid >= 0 or onid >= 0:
            pidinfo = sp(vpid) + sp(apid) + sp(sid) + sp(pcrpid) + sp(pmtpid) + sp(tsid) + onid
            return pidinfo
        else:
            return ''

    def pidhexstring(self, info):
        vpid = info.getInfo(iServiceInformation.sVideoPID)
        if vpid < 0:
            vpid = ''
        else:
            vpid = 'VPID:' + str(hex(vpid)[2:]).upper().zfill(4)
        apid = info.getInfo(iServiceInformation.sAudioPID)
        if apid < 0:
            apid = ''
        else:
            apid = 'APID:' + str(hex(apid)[2:]).upper().zfill(4)
        sid = info.getInfo(iServiceInformation.sSID)
        if sid < 0:
            sid = ''
        else:
            sid = 'SID:' + str(hex(sid)[2:]).upper().zfill(4)
        pcrpid = info.getInfo(iServiceInformation.sPCRPID)
        if pcrpid < 0:
            pcrpid = ''
        else:
            pcrpid = 'PCR:' + str(hex(pcrpid)[2:]).upper().zfill(4)
        pmtpid = info.getInfo(iServiceInformation.sPMTPID)
        if pmtpid < 0:
            pmtpid = ''
        else:
            pmtpid = 'PMT:' + str(hex(pmtpid)[2:]).upper().zfill(4)
        tsid = info.getInfo(iServiceInformation.sTSID)
        if tsid < 0:
            tsid = ''
        else:
            tsid = 'TSID:' + str(hex(tsid)[2:]).upper().zfill(4)
        onid = info.getInfo(iServiceInformation.sONID)
        if onid < 0:
            onid = ''
        else:
            onid = 'ONID:' + str(hex(onid)[2:]).upper().zfill(4)
        if vpid >= 0 or apid >= 0 or sid >= 0 or tsid >= 0 or onid >= 0:
            pidhexinfo = sp(vpid) + sp(apid) + sp(sid) + sp(pcrpid) + sp(pmtpid) + sp(tsid) + onid
            return pidhexinfo
        else:
            return ''

    @cached
    def getText(self):
        service = self.source.service
        info = service and service.info()
        if not info:
            return ''
        feinfo = service.frontendInfo()
        if feinfo:
            tp = feinfo.getAll(config.usage.infobar_frontend_source.value == 'settings')
            if tp:
                tpinfo = ConvertToHumanReadable(tp)
            if not tp:
                tp = info.getInfoObject(iServiceInformation.sTransponderData)
                tpinfo = ConvertToHumanReadable(tp)
        if self.type == self.FREQINFO:
            refstr = str(self.reference())
            if '%3a/' in refstr or ':/' in refstr:
                return self.streamurl()
            else:
                if 'DVB-S' in self.tunertype(tp):
                    satf = sp(self.system(tpinfo)) + sp(self.modulation(tpinfo)) + sp(self.frequency(tp)) + sp(self.polarization(tpinfo)) + sp(self.symbolrate(tp)) + sp(self.fecinfo(tpinfo))
                    if 'is_id' in tpinfo or 'pls_code' in tpinfo or 'pls_mode' in tpinfo or 't2mi_plp_id' in tp:
                        return satf + self.multistream(tpinfo) + self.t2mi_info(tpinfo)
                    else:
                        return satf
                else:
                    if 'DVB-C' in self.tunertype(tp):
                        return sp(self.frequency(tp)) + sp('Mhz') + sp(self.modulation(tpinfo)) + sp('SR:') + sp(self.symbolrate(tp)) + sp('FEC:') + self.fecinfo(tpinfo)
                    if self.tunertype(tp) == 'DVB-T':
                        terf = sp(self.channel(tpinfo)) + '(' + sp(self.terrafreq(tp)) + sp('Mhz)') + sp(self.constellation(tpinfo)) + sp(self.terrafec(tpinfo))
                        return terf
                    if self.tunertype(tp) == 'DVB-T2':
                        return terf + self.plpid(tpinfo)
                    if 'ATSC' in self.tunertype(tp):
                        return sp(self.terrafreq(tp)) + sp('Mhz') + self.modulation(tpinfo)
                return ''
        else:
            if self.type == self.VIDEOCODEC:
                return self.videocodec(info)
            if self.type == self.FPS:
                return self.framerate(info)
            if self.type == self.VIDEOSIZE:
                return self.videosize(info)
            if self.type == self.RESCODEC:
                vidsize = self.videosize(info)
                fps = self.framerate(info)
                vidcodec = self.videocodec(info)
                return vidsize + '   ' + fps + '   ' + vidcodec
            if self.type == self.PIDINFO:
                return self.pidstring(info)
            if self.type == self.PIDHEXINFO:
                return self.pidhexstring(info)
            if self.type == self.STREAMURL:
                return str(self.streamurl())
            if self.type == self.PIDHEXINFO:
                return str(self.streamtype())
            if self.type == self.HDRINFO:
                return self.hdr(info)

    text = property(getText)

    @cached
    def getBoolean(self):
        service = self.source.service
        info = service and service.info()
        if not info:
            return False
        xresol = info.getInfo(iServiceInformation.sVideoWidth)
        yresol = info.getInfo(iServiceInformation.sVideoHeight)
        progrs = ('i', 'p', '', ' ')[info.getInfo(iServiceInformation.sProgressive)]
        vcodec = self.videocodec(info)
        streamurl = self.streamurl()
        gamma = self.hdr(info)
        if self.type == self.IS1080:
            if xresol >= 1880 and xresol <= 2000 or yresol >= 900 and yresol <= 1090:
                return True
            return False
        if self.type == self.IS720:
            if yresol >= 601 and yresol <= 800:
                return True
            return False
        if self.type == self.IS576:
            if yresol >= 501 and yresol <= 600:
                return True
            return False
        if self.type == self.IS1440:
            if xresol >= 2500 and xresol <= 2600 or yresol >= 1300 and yresol <= 1500:
                return True
            return False
        if self.type == self.IS2160:
            if xresol >= 3820 and xresol <= 4100 or yresol >= 2150 and yresol <= 2170:
                return True
            return False
        if self.type == self.IS480:
            if yresol >= 380 and yresol <= 500:
                return True
            return False
        if self.type == self.IS360:
            if yresol >= 200 and yresol <= 379:
                return True
            return False
        if self.type == self.ISPROGRESSIVE:
            if progrs == 'p':
                return True
            return False
        if self.type == self.ISINTERLACED:
            if progrs == 'i':
                return True
            return False
        if self.type == self.ISSTREAMING:
            if streamurl:
                return True
            return False
        if self.type == self.HASMPEG2:
            if vcodec == 'MPEG2':
                return True
            return False
        if self.type == self.HASAVC:
            if vcodec == 'AVC' or vcodec == 'MPEG4':
                return True
            return False
        if self.type == self.HASH263:
            if vcodec == 'H263':
                return True
            return False
        if self.type == self.HASVC1:
            if 'VC1' in vcodec:
                return True
            return False
        if self.type == self.HASMPEG4VC:
            if vcodec == 'MPEG4-VC':
                return True
            return False
        if self.type == self.HASHEVC:
            if vcodec == 'HEVC' or vcodec == 'H265':
                return True
            return False
        if self.type == self.HASMPEG1:
            if vcodec == 'MPEG1':
                return True
            return False
        if self.type == self.HASVP8:
            if vcodec == 'VB8' or vcodec == 'VP8':
                return True
            return False
        if self.type == self.HASVP9:
            if vcodec == 'VB9' or vcodec == 'VP9':
                return True
            return False
        if self.type == self.HASVP6:
            if vcodec == 'VB6' or vcodec == 'VP6':
                return True
            return False
        if self.type == self.HASDIVX:
            if 'DIVX' in vcodec:
                return True
            return False
        if self.type == self.HASXVID:
            if 'XVID' in vcodec:
                return True
            return False
        if self.type == self.HASSPARK:
            if vcodec == 'SPARK':
                return True
            return False
        if self.type == self.HASAVS:
            if 'AVS' in vcodec:
                return True
            return False
        if self.type == self.ISSDR:
            if 'SDR' in gamma:
                return True
            return False
        if self.type == self.ISHDR:
            if gamma == 'HDR':
                return True
            return False
        if self.type == self.ISHDR10:
            if gamma == 'HDR10':
                return True
            return False
        if self.type == self.ISHLG:
            if 'HLG' in gamma:
                return True
            return False

    boolean = property(getBoolean)

    def changed(self, what):
        if what[0] == self.CHANGED_SPECIFIC and what[1] == iPlayableService.evUpdatedInfo or what[0] == self.CHANGED_POLL:
            Converter.changed(self, what)