import os
import json
import pygame as pg
from modules.UI.windowManager import Window
from appUI.systems.nav import addNav
from appUI.systems.main import addMain
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
  global window, userData

  if 'loadReplay' in window.customData and window.customData['loadReplay'] is not None:
    loadRendererWithReplay(window, userData)

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
    window.systems['main'].elements['replaySection'].background = pg.surface.Surface((window.screenWidth, window.screenHeight - window.systems['nav'].elements['topNav'].height))
    window.customData['beatmapRenderer'].updateSurface(window.systems['main'].elements['replaySection'].background, 1)

  window.customData['lastScreenRes'] = (window.screenWidth, window.screenHeight)

  print('update')

def windowCustomEvents(event):
  if event.type == pg.KEYDOWN:
    if event.key == pg.K_SPACE:
      pauseToggle(window)
  # else:
  #   print(event.type)

userData = None
with open('data/userData.json', 'r') as rawData:
  userData = json.load(rawData)

for url in userData['URLs']:
  if not os.path.isdir(userData['URLs'][url]):
    print(f'The {url} : {userData['URLs'][url]} is not a valid url.')
    # do something

window = Window('Replay Veiwer', (800, 450), customLoopProcess=windowCustomLoop, customUpdateProcess=windowCustomUpdate, customEventHandler=windowCustomEvents)

## add systems ##
addNav(window)
addMain(window)
addReplayList(window, userData)
addSettings(window)

## define system z indexes ##
window.setSystemZ('nav', 9)
window.setSystemZ('main', 0)
window.setSystemZ('replayList', 1)
window.setSystemZ('settings', 2)

window.activateSystems(['nav', 'main'])

window.customData['firstUpdate'] = True

window.openWindow()
