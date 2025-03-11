import os
import json
import pygame as pg
from modules.UI.windowManager import Window
from appUI.systems.nav import addNav
from appUI.systems.main import addMain
from appUI.systems.replayList import addReplayList
from appUI.systems.settings import addSettings
from modules.readers.replayReader import getReplayData
from modules.readers.osudbReader import getMapByMD5
from modules.renderer.beatmapRenderer import MapRenderer

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

def loadReplay():
  global window, userData

  # print(window.customData['loadReplay'])
  window.loggedSystemSwitch = 'main'

  # using an older version of the database file for now because of the recent update #
  # !!! THIS IS A TEMPORARY FIX UPDATE THIS LATTER !!! #

  # osuDbURL = os.path.join(userData['URLs']['osuFolder'], 'osu!.db')
  osuDbURL = 'testFiles/osu!-1.db'
  replayURL = os.path.join(userData['URLs']['osuFolder'], 'Replays', window.customData['loadReplay'] + '.osr')
  window.customData['loadReplay'] = None

  # get replay data #
  try:
    print('getting replay data...')
    replayData = getReplayData(replayURL)
    print('done.')
  except Exception as e:
    print(e)
    return e

  # get beatmap data from the database #
  try:
    print('getting beatmap data...')
    beatmapData = getMapByMD5(osuDbURL, replayData['beatmapMD5Hash'])
    print('done.')
  except Exception as e:
    print(e)
    return e

  # create the beatmap URL and the replay surface #
  beatmapURL = os.path.join(userData['URLs']['osuFolder'], 'Songs', beatmapData['folderName'], beatmapData['osuFileName'])
  window.systems['main'].elements['replaySection'].background = pg.surface.Surface((window.screenWidth, window.screenHeight - window.systems['nav'].elements['topNav'].height))
  window.systems['main'].elements['replaySection'].update()

  # initialize the beatmap renderer #
  try:
    print('initializing beatmap renderer...')
    window.customData['beatmapRenderer'] = MapRenderer(
      userData['URLs']['osuFolder'],
      beatmapURL,
      userData['skin'],
      replayURL,
      window.systems['main'].elements['replaySection'].background,
      1
    )
    print('initializing beatmap renderer done.')
  except Exception as e:
    print(e)
    return e

  window.customData['replayLoaded'] = True

def windowCustomLoop():
  global window, userData

  if 'loadReplay' in window.customData and window.customData['loadReplay'] is not None:
    loadReplay()

  if 'replayLoaded' in window.customData and window.customData['replayLoaded'] and 'main' in window.activeSystems:
    if 'timeStarted' in window.customData and window.customData['timeStarted']:
      currentTime = window.time.get_ticks() - window.customData['startTime']
      # print(currentTime)
      window.customData['beatmapRenderer'].render(currentTime)
    else:
      window.customData['timeStarted'] = True
      window.customData['startTime'] = window.time.get_ticks()
      print('time recorded')

  systemSwitch()

def windowCustomUpdate():
  global window

  if window.customData['firstUpdate']:
    print('first update')
    window.customData['firstUpdate'] = False

  if 'replayLoaded' in window.customData and window.customData['replayLoaded']:
    window.systems['main'].elements['replaySection'].background = pg.surface.Surface((window.screenWidth, window.screenHeight - window.systems['nav'].elements['topNav'].height))
    window.customData['beatmapRenderer'].updateSurface(window.systems['main'].elements['replaySection'].background, 1)

  print('update')

def windowCustomEvents(event):
  pass
  # print(event.type)

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
