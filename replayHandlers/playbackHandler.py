from typing import Union
from modules.UI.windowManager import Window

def handleReplayPlayback(window: Window):
  if window.customData['replayTimeStarted']:
    timeline = window.systems['main'].elements['replayTimeline']

    if not window.customData['replayPaused']:
      currentTotalTime = window.time.get_ticks() - window.customData['startTime']
      newTime = currentTotalTime + window.customData['pauseOffset'] + window.customData['userDragOffset']

      if newTime > timeline.valueRange[1]:
        newTime = timeline.valueRange[1]

      timeline.value = newTime
      timeline.update()

    window.customData['beatmapRenderer'].render(timeline.value)
  else:
    window.customData['replayTimeStarted'] = True
    window.customData['startTime'] = window.time.get_ticks()

def timelineCallback(value: Union[int, float], window: Window):
  if not 'replayLoaded' in window.customData or not window.customData['replayLoaded']:
    return None

  currentTotalTime = window.time.get_ticks() - window.customData['startTime']
  currentReplayTime = currentTotalTime + window.customData['pauseOffset'] + window.customData['userDragOffset']
  timelineDifference = value - currentReplayTime

  window.customData['userDragOffset'] += timelineDifference

def pauseReplay(window: Window):
  if (not 'replayLoaded' in window.customData or not window.customData['replayLoaded']) or window.customData['replayPaused']:
    return None

  window.customData['replayPaused'] = True
  window.customData['pauseUnpauseTimeList'].append([window.time.get_ticks()])

def unpauseReplay(window: Window):
  if (not 'replayLoaded' in window.customData or not window.customData['replayLoaded']) or not window.customData['replayPaused']:
    return None

  window.customData['replayPaused'] = False

  window.customData['pauseUnpauseTimeList'][-1].append(window.time.get_ticks())

  window.customData['pauseOffset'] -= (window.customData['pauseUnpauseTimeList'][-1][1] - window.customData['pauseUnpauseTimeList'][-1][0])

def pauseToggle(window: Window):
  if window.customData['replayPaused']:
    unpauseReplay(window)
  else:
    pauseReplay(window)
