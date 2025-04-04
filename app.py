import os
import json
import sharedWindow
from pydub import AudioSegment
from appManagers.openCloseSeq import *
from appManagers.customLoops import *
from modules.UI.windowManager import Window
from appUI.systems.nav import addNav
from appUI.systems.main import addMain
from appUI.systems.replayList import addReplayList
from appUI.systems.settings import addSettings

userData = None

try:
  with open('data/userData.json', 'r') as rawData:
    userData = json.load(rawData)
except:
  # create default user data
  userData = {
    'firstBoot': True,
    'skin': '',
    'volume': 0.1,
    'highQualitySliders': False,
    'playfieldBorder': True,
    'sliderAnchors': False,
    'renderSkinCursor': True,
    'renderCursorTracker': False,
    'renderHitJudgments': False,
    'renderKeyOverlay': True,
    'renderModsDisplay': True,
    'normalHitsounds': True,
    'URLs': {
      'osuFolder': ''
    }
  }

if userData['firstBoot']:
  firstBootSetup(userData)

ffmpegPath = os.path.join(os.path.dirname(__file__), 'ffmpeg', 'bin', 'ffmpeg.exe')
AudioSegment.converter = ffmpegPath

ffmpegBinDir = os.path.join(os.path.dirname(__file__), 'ffmpeg', 'bin')
os.environ['PATH'] += os.pathsep + ffmpegBinDir

AudioSegment.ffprobe = ffmpegPath.replace('ffmpeg', 'ffprobe')

for url in userData['URLs']:
  if not os.path.isdir(userData['URLs'][url]):
    print(f'The {url} : {userData['URLs'][url]} is not a valid url.')
    firstBootSetup(userData)
    break

window = sharedWindow.window = Window('Replay Veiwer', (800, 450), customLoopProcess=windowCustomLoop, customUpdateProcess=windowCustomUpdate, customEventHandler=windowCustomEvents)

window.customData['firstUpdate'] = True
window.customData['userData'] = userData

# add systems #
addNav()
addMain()
addReplayList()
addSettings()

# define system z indexes #
window.setSystemZ('nav', 9)
window.setSystemZ('main', 0)
window.setSystemZ('replayList', 1)
window.setSystemZ('settings', 2)

# define initial active systems #
window.activateSystems(['nav', 'main'])

window.openWindow()

closingSetup(userData)
