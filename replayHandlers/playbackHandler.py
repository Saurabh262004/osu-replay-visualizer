from typing import Union, Optional
import pygame as pg
import sharedWindow
from appUI.colors import AppColors
from modules.misc.helpers import tintImage
from modules.beatmapElements.beatmap import Beatmap
from modules.renderer.beatmapRenderer import BeatmapRenderer
from modules.UI.windowManager import Window
from modules.beatmapElements.hitobjects import Hitcircle, Slider, Spinner

pauseButtonIcon = pg.image.load('assets/UI/pause-square.png')
tintImage(pauseButtonIcon, AppColors.cream)

playButtonIcon = pg.image.load('assets/UI/play-square.png')
tintImage(playButtonIcon, AppColors.cream)

def updateTimeStamp(time: int):
  window: Window = sharedWindow.window

  totalSecs = int(time / 1000)
  currentTimeMS = int(time - (totalSecs * 1000))
  currentTimeSecs = int(totalSecs % 60)
  currentTimeMinutes = int(totalSecs / 60)

  timeStamp = window.systems['main'].elements['timeStamp']

  timeStamp.text = f'{currentTimeMinutes:02d}:{currentTimeSecs:02d}.{currentTimeMS:03d} / {window.customData['timeStampMax']}'
  timeStamp.update()

def updateHitobjectsHitsoundTrigger(time: int):
  window: Window = sharedWindow.window
  renderer: BeatmapRenderer = window.customData['beatmapRenderer']
  time /= renderer.timeDivisor

  for hitobject in renderer.beatmap.hitobjects:
    if isinstance(hitobject, Spinner): continue

    if isinstance(hitobject, Slider):
      for i in range(len(hitobject.triggeredHitSound)):
        edgeTime = hitobject.time + (hitobject.slideTime * i)

        if edgeTime > time: hitobject.triggeredHitSound[i] = False
        else: hitobject.triggeredHitSound[i] = True

    elif isinstance(hitobject, Hitcircle):
      if hitobject.hitTime > time: hitobject.triggeredHitSound = False
      else: hitobject.triggeredHitSound = False

def handleReplayPlayback():
  window: Window = sharedWindow.window

  if window.customData['replayTimeStarted']:
    timeline = window.systems['main'].elements['replayTimeline']

    if not window.customData['replayPaused']:
      currentTotalTime = window.time.get_ticks() - window.customData['startTime']
      newTime = currentTotalTime + window.customData['pauseOffset'] + window.customData['userDragOffset']

      if newTime > timeline.valueRange[1]:
        newTime = timeline.valueRange[1]
        pauseReplay()
      elif newTime < timeline.valueRange[0]:
        newTime = timeline.valueRange[0]

      window.customData['timelineTimeLog'] = newTime
      updateTimeStamp(newTime)

      timeline.value = newTime
      timeline.update()

    renderer: BeatmapRenderer = window.customData['beatmapRenderer']
    renderer.render(timeline.value)

    if window.customData['replayPaused']: return

    currentTimeForHit = timeline.value / renderer.timeDivisor
    beatmap: Beatmap = renderer.beatmap
    lastObj = beatmap.lastObjectAtTimeByHitTime(currentTimeForHit)

    if not lastObj or lastObj.judgment == 0: return

    if isinstance(lastObj, Hitcircle):
      if not window.customData['justTriggeredHitsound'] and not lastObj.triggeredHitSound:
        lastObj.triggeredHitSound = True

        if window.customData['userData']['normalHitsounds']:
          window.customData['skin']['hitsounds'][f'{lastObj.sampleSet}-hitnormal'].play()
        else:
          for hitsound in lastObj.hitsounds:
            hitsound.play()

        window.customData['justTriggeredHitsound'] = True
      else:
        window.customData['justTriggeredHitsound'] = False
    else:
      for i in range(len(lastObj.triggeredHitSound)):
        edgeTrigger = lastObj.triggeredHitSound[i]

        if not edgeTrigger and lastObj.time + (lastObj.slideTime * i) <= currentTimeForHit and not window.customData['justTriggeredHitsound']:
          lastObj.triggeredHitSound[i] = True

          if window.customData['userData']['normalHitsounds']:
            window.customData['skin']['hitsounds'][f'{lastObj.sampleSet}-hitnormal'].play()
          else:
            for hitsound in lastObj.hitsounds:
              hitsound.play()

          window.customData['justTriggeredHitsound'] = True
        else:
          window.customData['justTriggeredHitsound'] = False

  else:
    window.customData['replayTimeStarted'] = True
    window.customData['startTime'] = window.time.get_ticks()

def timelineCallback(value: Union[int, float]):
  window: Window = sharedWindow.window

  if not 'replayLoaded' in window.customData or not window.customData['replayLoaded']:
    return None

  timelineDifference = value - window.customData['timelineTimeLog']

  window.customData['timelineTimeLog'] = value

  window.customData['userDragOffset'] += timelineDifference

  updateTimeStamp(int(value))

  pauseReplay(True)

def pauseReplay(unpauseAfter: Optional[bool] = False):
  global playButtonIcon

  window: Window = sharedWindow.window

  if (not 'replayLoaded' in window.customData or not window.customData['replayLoaded']) or window.customData['replayPaused']:
    return None

  window.customData['replayPaused'] = True

  window.customData['pauseUnpauseTimeList'].append([window.time.get_ticks()])

  pg.mixer.music.pause()

  window.systems['main'].elements['playbackButton'].section.background = playButtonIcon
  window.systems['main'].elements['playbackButton'].section.update()

  if unpauseAfter:
    unpauseReplay()

def unpauseReplay():
  global pauseButtonIcon

  window: Window = sharedWindow.window

  if (not 'replayLoaded' in window.customData or not window.customData['replayLoaded']) or not window.customData['replayPaused']:
    return None

  window.customData['replayPaused'] = False

  window.customData['pauseUnpauseTimeList'][-1].append(window.time.get_ticks())

  window.customData['pauseOffset'] -= (window.customData['pauseUnpauseTimeList'][-1][1] - window.customData['pauseUnpauseTimeList'][-1][0])

  currentTotalTime = window.time.get_ticks() - window.customData['startTime']

  newTime = currentTotalTime + window.customData['pauseOffset'] + window.customData['userDragOffset']

  if newTime < 0:
    newTime = 0
  elif newTime >= window.systems['main'].elements['replayTimeline'].valueRange[1]:
    newTime = window.systems['main'].elements['replayTimeline'].valueRange[1] - 1

  window.systems['main'].elements['replayTimeline'].value = newTime
  window.systems['main'].elements['replayTimeline'].update()

  updateHitobjectsHitsoundTrigger(newTime)
  
  window.systems['main'].elements['playbackButton'].section.background = pauseButtonIcon
  window.systems['main'].elements['playbackButton'].section.update()

  pg.mixer.music.play(start=(newTime/1000))

def pauseToggle():
  window: Window = sharedWindow.window

  if not 'replayLoaded' in window.customData or not window.customData['replayLoaded']:
    return None

  if window.customData['replayPaused']:
    unpauseReplay()
  else:
    pauseReplay()
