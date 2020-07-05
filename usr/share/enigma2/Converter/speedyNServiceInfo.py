from Poll import Poll
from Components.Converter.Converter import Converter
from enigma import iServiceInformation, iPlayableService
from Components.Element import cached

class speedyNServiceInfo(Poll, Converter, object):
	YRESIP = 0

	def __init__(self, type):
		Converter.__init__(self, type)
		Poll.__init__(self)
		self.type, self.interesting_events = {
				"VideoHeightIP": (self.YRESIP, (iPlayableService.evVideoSizeChanged,)),
			}[type]
		self.poll_interval = 1000
		self.poll_enabled = True

	def getServiceInfoString(self, info, what, convert = lambda x: "%d" % x):
		v = info.getInfo(what)
		if v == -1:
			return "N/A"
		if v == -2:
			return info.getInfoString(what)
		return convert(v)

	@cached
	def getText(self):
		service = self.source.service
		info = service and service.info()
		if not info:
			return ""

		if self.type == self.YRESIP:
			return self.getServiceInfoString(info, iServiceInformation.sVideoHeight) + ("i", "p", "")[info.getInfo(iServiceInformation.sProgressive)]
		return ""

	text = property(getText)

	def changed(self, what):
		if what[0] != self.CHANGED_SPECIFIC or what[1] in self.interesting_events:
			Converter.changed(self, what)
		elif what[0] == self.CHANGED_POLL:
			self.downstream_elements.changed(what)
