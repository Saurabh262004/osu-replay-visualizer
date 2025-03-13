import os
import traceback
from modules.UI.windowManager import Window
from modules.readers.replayReader import getReplayData
from modules.readers.osudbReader import getMapByMD5
from modules.beatmapElements.hitobjects import Hitcircle, Slider, Spinner
from modules.renderer.beatmapRenderer import MapRenderer
import pygame as pg

def loadRendererWithReplay(window: Window, userData: dict):
  window.loggedSystemSwitch = 'main'

  osuDbURL = os.path.join(userData['URLs']['osuFolder'], 'osu!.db')
  replayURL = os.path.join(userData['URLs']['osuFolder'], 'Replays', window.customData['loadReplay'] + '.osr')
  window.customData['loadReplay'] = None

  # get replay data #
  try:
    # print('getting replay data...')
    replayData = getReplayData(replayURL)
    # print('done.')
  except Exception as e:
    traceback.print_exc()
    print(e)
    return e

  # get beatmap data from the database #

  try:
    # print('getting beatmap data...')
    beatmapData = getMapByMD5(osuDbURL, replayData['beatmapMD5Hash'])
    # print('done.')
  except Exception as e:
    traceback.print_exc()
    print(e)
    return e

  # create the beatmap URL and the replay surface #
  beatmapURL = os.path.join(userData['URLs']['osuFolder'], 'Songs', beatmapData['folderName'], beatmapData['osuFileName'])
  window.systems['main'].elements['replaySection'].background = pg.surface.Surface((window.screenWidth, window.screenHeight - window.systems['nav'].elements['topNav'].height))
  window.systems['main'].elements['replaySection'].update()

  # initialize the beatmap renderer #
  try:
    # print('initializing beatmap renderer...')
    window.customData['beatmapRenderer'] = MapRenderer(
      userData['URLs']['osuFolder'],
      beatmapURL,
      userData['skin'],
      replayURL,
      window.systems['main'].elements['replaySection'].background,
      1
    )
    # print('initializing beatmap renderer done.')
  except Exception as e:
    traceback.print_exc()
    print(e)
    return e

  beatmap = window.customData['beatmapRenderer'].beatmap
  startTime = 0
  endTime = 0
  lastElement = beatmap.hitobjects[-1]

  if isinstance(lastElement, Hitcircle):
    endTime = lastElement.time + beatmap.objectFadeout
  elif isinstance(lastElement, Slider):
    sliderDuration = lastElement.slideTime * lastElement.slides
    endTime = lastElement.time + sliderDuration + beatmap.objectFadeout
  elif isinstance(lastElement, Spinner):
    endTime = lastElement.endTime + beatmap.objectFadeout
  else:
    # we should never get here but just in case... #
    # change the endTime to the length of the audio file #
    print('how did you get here?')
    endTime = 0

  timelineRange = (startTime, endTime)

  window.systems['main'].elements['replayTimeline'].valueRange = timelineRange

  window.customData['replayTimeStarted'] = False
  window.customData['replayPaused'] = True
  window.customData['pauseUnpauseTimeList'] = [[window.time.get_ticks()]]
  window.customData['pauseOffset'] = 0
  window.customData['userDragOffset'] = 0
  window.customData['replayLoaded'] = True

def loadRendererWithoutReplay(window: Window, userData: dict):
  pass

