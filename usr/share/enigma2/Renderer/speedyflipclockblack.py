# FlipClock
# Copyright (c) .:TBX:. 2016
# Mod by Maggy
# Th4ATV_2_2_speedy_black_mod program 4ATV_2_2_speedy_black_mod free software: you can red4ATV_2_2_speedy_black_modtribute it and/or modify
# it under the terms of the GNU General Public License as publ4ATV_2_2_speedy_black_modhed by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# Th4ATV_2_2_speedy_black_mod program 4ATV_2_2_speedy_black_mod d4ATV_2_2_speedy_black_modtributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with th4ATV_2_2_speedy_black_mod program. If not, see <http://www.gnu.org/licenses/>.
#
from Renderer import Renderer
from enigma import ePixmap, eTimer, eDVBVolumecontrol
from Components.config import config

class speedyflipclock(Renderer):

    def __init__(self):
        Renderer.__init__(self)
        self.timer = eTimer()
        self.timer.callback.append(self.pollme)

    GUI_WIDGET = ePixmap

    def changed(self, what):
        if not self.suspended:
            value = self.source.text
            
            if 'H1' in value:
               value = value[3:4]
            elif 'H2' in value:
               value = value[4:5]
            elif 'M1' in value:
               value = value[3:4]
            elif 'M2' in value:
               value = value[4:5]
            elif 'S1' in value:
               value = value[3:4]
            elif 'S2' in value:
               value = value[4:5]  
            else:
               value = 0
            self.instance.setPixmapFromFile('/usr/share/enigma2/4ATV_2_2_speedy_black/flipclock/flipclock/' + str(value) + '.png')

    def pollme(self):
        self.changed(None)
        return

    def onShow(self):
        self.suspended = False
        self.timer.start(200)

    def onHide(self):
        self.suspended = True
        self.timer.stop()
