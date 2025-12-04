import os
import platform
import json
import sharedWindow
from pydub import AudioSegment
import pygame as pg
from appManagers.openCloseSeq import *
from appManagers.customLoops import *
from modules.UI.windowManager import Window
from appUI.systems.nav import addNav
from appUI.systems.main import addMain
from appUI.systems.replayList import addReplayList
from appUI.systems.settings import addSettings

pg.mixer.pre_init(44100, -16, 2, 256)
pg.init()

userData = None

try:
  with open('data/userData.json', 'r') as rawData:
    userData = json.load(rawData)
except:
  print('failed to load userdata file')

  # create default user data
  userData = {
    'firstBoot': True,
    'skin': 'default',
    'volume': 0.1,
    'highQualitySliders': False,
    'playfieldBorder': True,
    'sliderAnchors': False,
    'renderSkinCursor': True,
    'renderCursorTracker': False,
    'renderHitJudgments': False,
    'renderKeyOverlay': True,
    'renderModsDisplay': True,
    'normalHitsounds': False,
    'disableHidden': False,
    'URLs': {
      'osuFolder': ''
    }
  }

if userData['firstBoot']:
  firstBootSetup(userData)

def setupFFMPEG():
  system = platform.system().lower()
  machine = platform.machine().lower()

  if machine in ("x86_64", "amd64"):
    arch = "amd64"
  elif machine in ("aarch64", "arm64"):
    arch = "arm64"
  elif machine in ("i386", "i686"):
    arch = "i686"
  else:
    arch = machine

  binary_name = "ffmpeg.exe" if system == "windows" else "ffmpeg"

  base_dir = os.path.dirname(__file__)
  ffmpeg_dir = os.path.join(base_dir, "ffmpeg", f"{system}-{arch}")
  ffmpeg_path = os.path.join(ffmpeg_dir, binary_name)

  if not os.path.exists(ffmpeg_path):
    from pydub.utils import which
    ffmpeg_path = which("ffmpeg")

  AudioSegment.converter = ffmpeg_path

  if ffmpeg_dir not in os.environ["PATH"]:
    os.environ["PATH"] += os.pathsep + ffmpeg_dir

setupFFMPEG()

for url in userData['URLs']:
  if not os.path.isdir(userData['URLs'][url]):
    print(f'The {url} : {userData['URLs'][url]} is not a valid url.')
    firstBootSetup(userData)
    break

window = sharedWindow.window = Window('Replay Veiwer', (800, 450), customLoopProcess=windowCustomLoop, customUpdateProcess=windowCustomUpdate, customEventHandler=windowCustomEvents)

window.customData['firstUpdate'] = True
window.customData['userData'] = userData
window.customData['debug'] = True

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
