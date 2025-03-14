from typing import Union
import pygame as pg
from modules.UI.windowManager import Window

def handleReplayPlayback(window: Window):
  if window.customData['replayTimeStarted']:
    timeline = window.systems['main'].elements['replayTimeline']

    if not window.customData['replayPaused']:
      currentTotalTime = window.time.get_ticks() - window.customData['startTime']
      newTime = currentTotalTime + window.customData['pauseOffset'] + window.customData['userDragOffset']

      if newTime > timeline.valueRange[1]:
        newTime = timeline.valueRange[1]
        pauseReplay(window)
      elif newTime < timeline.valueRange[0]:
        newTime = timeline.valueRange[0]

      window.customData['timelineTimeLog'] = newTime

      timeline.value = newTime
      timeline.update()

    window.customData['beatmapRenderer'].render(timeline.value)
  else:
    window.customData['replayTimeStarted'] = True
    window.customData['startTime'] = window.time.get_ticks()

def timelineCallback(value: Union[int, float], window: Window):
  if not 'replayLoaded' in window.customData or not window.customData['replayLoaded'] or not window.customData['replayPaused']:
    return None

  timelineDifference = value - window.customData['timelineTimeLog']

  window.customData['timelineTimeLog'] = value

  window.customData['userDragOffset'] += timelineDifference

def pauseReplay(window: Window):
  if (not 'replayLoaded' in window.customData or not window.customData['replayLoaded']) or window.customData['replayPaused']:
    return None

  window.customData['replayPaused'] = True

  window.customData['pauseUnpauseTimeList'].append([window.time.get_ticks()])

  pg.mixer.music.pause()

def unpauseReplay(window: Window):
  if (not 'replayLoaded' in window.customData or not window.customData['replayLoaded']) or not window.customData['replayPaused']:
    return None

  window.customData['replayPaused'] = False

  window.customData['pauseUnpauseTimeList'][-1].append(window.time.get_ticks())

  window.customData['pauseOffset'] -= (window.customData['pauseUnpauseTimeList'][-1][1] - window.customData['pauseUnpauseTimeList'][-1][0])

  currentTotalTime = window.time.get_ticks() - window.customData['startTime']

  newTime = currentTotalTime + window.customData['pauseOffset'] + window.customData['userDragOffset']

  if newTime < 0:
    newTime = 0

  window.systems['main'].elements['replayTimeline'].value = newTime
  window.systems['main'].elements['replayTimeline'].update()

  pg.mixer.music.play(start=(newTime/1000))

def pauseToggle(window: Window):
  if not 'replayLoaded' in window.customData or not window.customData['replayLoaded']:
    return None

  if window.customData['replayPaused']:
    unpauseReplay(window)
  else:
    pauseReplay(window)
