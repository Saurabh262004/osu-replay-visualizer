import os
import json
from copy import copy
import easygui
import pygame as pg
from modules.UI.windowManager import Window
from appUI.systems.nav import addNav
from appUI.systems.main import addMain, setUserVolume
from appUI.systems.replayList import addReplayList
from appUI.systems.settings import addSettings
from replayHandlers.loader import loadRendererWithReplay
from replayHandlers.playbackHandler import handleReplayPlayback, pauseToggle

def systemSwitch():
  global window

  if not window.loggedSystemSwitch is None:

    if window.loggedSystemSwitch in window.activeSystems:
      return None

    deavtivateSystemIDs = []

    for activeSystemID in window.activeSystems:
      if activeSystemID != 'nav':
        deavtivateSystemIDs.append(activeSystemID)

    window.deactivateSystems(deavtivateSystemIDs)
    window.activateSystems(window.loggedSystemSwitch)

    window.loggedSystemSwitch = None

def windowCustomLoop():
  global window

  if 'loadReplay' in window.customData and window.customData['loadReplay'] is not None:
    loadRendererWithReplay(window)

  if 'replayLoaded' in window.customData and window.customData['replayLoaded'] and 'main' in window.activeSystems:
    handleReplayPlayback(window)

  systemSwitch()

def windowCustomUpdate():
  global window

  if window.customData['firstUpdate']:
    print('first update')
    window.customData['firstUpdate'] = False

  resChange = False
  if 'lastScreenRes' in window.customData and window.customData['lastScreenRes'] != (window.screenWidth, window.screenHeight):
    resChange = True

  if resChange and 'replayLoaded' in window.customData and window.customData['replayLoaded'] and not window.customData['firstUpdate']:
    defaultHeight = 384

    replaySectionHeight = window.screenHeight - window.systems['nav'].elements['topNav'].height

    resolutionMultiplier = (replaySectionHeight * .8) / defaultHeight

    window.systems['main'].elements['replaySection'].background = pg.surface.Surface((window.screenWidth, replaySectionHeight))

    window.customData['beatmapRenderer'].updateSurface(window.systems['main'].elements['replaySection'].background, resolutionMultiplier)

  window.customData['lastScreenRes'] = (window.screenWidth, window.screenHeight)

  print('update')

def windowCustomEvents(event: pg.event.Event):
  if event.type == pg.KEYDOWN:
    if event.key == pg.K_SPACE:
      pauseToggle(window)
    elif event.key == pg.K_LEFT or event.key == pg.K_RIGHT or event.key == pg.K_COMMA or event.key == pg.K_PERIOD:
      timeline = window.systems['main'].elements['replayTimeline']

      if event.key == pg.K_LEFT:
        newValue = timeline.value - 5000
      elif event.key == pg.K_RIGHT:
        newValue = timeline.value + 5000
      elif event.key == pg.K_COMMA:
        newValue = timeline.value - 15
      elif event.key == pg.K_PERIOD:
        newValue = timeline.value + 15

      if newValue < timeline.valueRange[0]:
        newValue = timeline.valueRange[0]
      elif newValue > timeline.valueRange[1]:
        newValue = timeline.valueRange[1]

      window.customData['timelineTimeLog'] = copy(timeline.value)
      timeline.value = newValue
      timeline.update()
      timeline.callback()
    elif event.key == pg.K_DOWN:
      setUserVolume(userData['volume'] - .1, window)
      window.systems['main'].elements['audioControl'].value = userData['volume']
      window.systems['main'].elements['audioControl'].update()
    elif event.key == pg.K_UP:
      setUserVolume(userData['volume'] + .1, window)
      window.systems['main'].elements['audioControl'].value = userData['volume']
      window.systems['main'].elements['audioControl'].update()

def firstBootSetup():
  folder_path = easygui.diropenbox(title="Please select your osu! folder")
  userData['URLs']['osuFolder'] = folder_path
  print("Selected osu! Folder:", folder_path)

  userData['firstBoot'] = False

def closingSetup():
  print('closing the application...')

  try:
    with open('data/userData.json', 'w') as userDataFile:
      userDataFile.write(json.dumps(userData, indent=2))
  except Exception as e:
    print('Failed to save user data.')
    print(e)

userData = None
try:
  with open('data/userData.json', 'r') as rawData:
    userData = json.load(rawData)
except:
  # create default user data
  userData = {
    "firstBoot": True,
    "skin": "",
    "volume": 0.2,
    "highQualitySliders": False,
    "playfieldBorder": True,
    "renderSkinCursor": True,
    "renerCursorTracker": True,
    "renderHitJudgments": False,
    "URLs": {
      "osuFolder": ""
    }
  }

if userData['firstBoot']:
  firstBootSetup()

for url in userData['URLs']:
  if not os.path.isdir(userData['URLs'][url]):
    print(f'The {url} : {userData['URLs'][url]} is not a valid url.')

window = Window('Replay Veiwer', (800, 450), customLoopProcess=windowCustomLoop, customUpdateProcess=windowCustomUpdate, customEventHandler=windowCustomEvents)

window.customData['firstUpdate'] = True
window.customData['userData'] = userData

# add systems #
addNav(window)
addMain(window)
addReplayList(window)
addSettings(window)

# define system z indexes #
window.setSystemZ('nav', 9)
window.setSystemZ('main', 0)
window.setSystemZ('replayList', 1)
window.setSystemZ('settings', 2)

# define initial active systems #
window.activateSystems(['nav', 'main'])

window.openWindow()

closingSetup()
