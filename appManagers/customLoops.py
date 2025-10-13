import pygame as pg
from copy import copy
from appManagers.manageAlerts import activateAlert
from modules.UI.windowManager import Window
from appUI.systems.replayList import scrollReplayList
from modules.readers.importSkin import importSkin
from replayHandlers.loader import loadRendererWithReplay
from replayHandlers.playbackHandler import handleReplayPlayback, pauseToggle, unpauseReplay, pauseReplay
from appUI.systems.main import setUserVolume
import sharedWindow

def systemSwitch():
  window: Window = sharedWindow.window

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
  window: Window = sharedWindow.window

  if 'loadReplay' in window.customData and window.customData['loadReplay'] is not None:
    loadRendererWithReplay()

  if 'replayLoaded' in window.customData and window.customData['replayLoaded'] and 'main' in window.activeSystems:
    handleReplayPlayback()

  systemSwitch()

  fps = window.clock.get_fps()
  window.systems['main'].elements['FPSBox'].text = f'{fps:.0f}'
  window.systems['main'].elements['FPSBox'].update()

def windowCustomUpdate():
  window: Window = sharedWindow.window
  userData = window.customData['userData']

  ## First Update ##
  if window.customData['firstUpdate']:
    activateAlert('No replay Loaded')

    if window.customData['debug']:
      print('first update')

    window.customData['firstUpdate'] = False

    if userData['skin'] == "":
      activateAlert('No skin selected!')
    else:
      try:
        if userData['skin'] == 'default':
          window.customData['skin'] = importSkin('assets/defaultSkin', 'assets/defaultSkin', userData['URLs']['osuFolder'], True)
        else:
          window.customData['skin'] = importSkin(userData['skin'], 'assets/defaultSkin', userData['URLs']['osuFolder'])

        for hitsound in window.customData['skin']['hitsounds']:
          window.customData['skin']['hitsounds'][hitsound].set_volume(userData['volume'] / 3)
      except:
        activateAlert('Couldn\'t load the skin!')

  ## Update Replay Section On Resolution Change ##
  if ('replayLoaded' in window.customData) and window.customData['replayLoaded'] and (not window.customData['firstUpdate']) and window.secondResize:
    defaultHeight = 384

    replaySectionHeight = window.screenHeight - window.systems['nav'].elements['topNav'].height

    resolutionMultiplier = (replaySectionHeight * .75) / defaultHeight

    window.systems['main'].elements['replaySection'].background = pg.surface.Surface((window.screenWidth, replaySectionHeight))

    window.customData['beatmapRenderer'].updateSurface(window.systems['main'].elements['replaySection'].background, resolutionMultiplier)

  window.customData['lastScreenRes'] = (window.screenWidth, window.screenHeight)

  if not window.systems['replayList'].locked:
    scrollReplayList(window.systems['replayList'])

def windowCustomEvents(event: pg.event.Event):
  window: Window = sharedWindow.window
  userData: dict = window.customData['userData']

  if event.type == pg.KEYDOWN:
    if event.key == pg.K_SPACE:
      pauseToggle()
    elif event.key == pg.K_LEFT or event.key == pg.K_RIGHT or event.key == pg.K_COMMA or event.key == pg.K_PERIOD:
      if 'replayPaused' in window.customData and window.customData['replayPaused']:
        alreadyPaused = True
      else:
        alreadyPaused = False
        pauseReplay()

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

      if not alreadyPaused:
        unpauseReplay()
    elif event.key == pg.K_DOWN:
      setUserVolume(userData['volume'] - .1, window)
      window.systems['main'].elements['audioControl'].value = userData['volume']
      window.systems['main'].elements['audioControl'].update()
    elif event.key == pg.K_UP:
      setUserVolume(userData['volume'] + .1, window)
      window.systems['main'].elements['audioControl'].value = userData['volume']
      window.systems['main'].elements['audioControl'].update()
