import os
import traceback
import sharedWindow
from pydub import AudioSegment
from tempfile import mkstemp
from appManagers.manageAlerts import *
from appUI.colors import AppColors
from modules.UI.windowManager import Window
from modules.readers.replayReader import getReplayData
from modules.readers.osudbReader import getMapByMD5
from modules.renderer.beatmapRenderer import BeatmapRenderer
import pygame as pg

def loadPgMusicAtSpeed(audio: AudioSegment, speed: float):
  window: Window = sharedWindow.window

  if 'tmpAudioPath' in window.customData and os.path.exists(window.customData['tmpAudioPath']):
    pg.mixer.music.unload()
    os.remove(window.customData['tmpAudioPath'])
    del window.customData['tmpAudioPath']

  newFrameRate = int(audio.frame_rate * speed)

  newAudio = audio._spawn(audio.raw_data, overrides={'frame_rate': newFrameRate}).set_frame_rate(audio.frame_rate)

  fd, tmpAudioPath = mkstemp(suffix=".mp3", text=False)

  os.close(fd)

  newAudio.export(tmpAudioPath, format="mp3")

  pg.mixer.music.load(tmpAudioPath)

  window.customData['tmpAudioPath'] = tmpAudioPath

def loadRendererWithReplay(customURL: str = None):
  window: Window = sharedWindow.window
  window.loggedSystemSwitch = 'main'
  userData = window.customData['userData']

  osuDbURL = os.path.join(userData['URLs']['osuFolder'], 'osu!.db')

  if customURL is None:
    replayURL = os.path.join(userData['URLs']['osuFolder'], 'Replays', window.customData['loadReplay'] + '.osr')
  else:
    replayURL = customURL

  window.customData['loadReplay'] = None

  # get replay data #
  try:
    # print('getting replay data...')
    replayData = getReplayData(replayURL)
    # print('done.')
  except Exception as e:
    activateAlert('Couldn\'t read osu database!')

    traceback.print_exc()
    print(e)
    return e

  # get beatmap data from the database #
  try:
    # print('getting beatmap data...')
    beatmapData = getMapByMD5(osuDbURL, replayData['beatmapMD5Hash'])

    if beatmapData is None:
      activateAlert('You don\'t have the beatmap!')
      return False

    # print('done.')
  except Exception as e:
    activateAlert('Couldn\'t get map!')

    traceback.print_exc()
    print(e)
    return e

  # create the beatmap URL and the replay surface #
  beatmapURL = os.path.join(userData['URLs']['osuFolder'], 'Songs', beatmapData['folderName'], beatmapData['osuFileName'])
  mapFolderURL = os.path.dirname(beatmapURL)
  audioFileURL = os.path.join(mapFolderURL, beatmapData['audioFileName'])

  defaultHeight = 384
  replaySectionHeight = window.screenHeight - window.systems['nav'].elements['topNav'].height

  resolutionMultiplier = (replaySectionHeight * .75) / defaultHeight

  # set the replay section background to a new pg surface #
  replaySection = window.systems['main'].elements['replaySection']
  replaySection.background = pg.surface.Surface((window.screenWidth, replaySectionHeight), pg.SRCALPHA)
  replaySection.update()

  # initialize the beatmap renderer #
  try:
    # print('initializing beatmap renderer...')
    window.customData['beatmapRenderer'] = BeatmapRenderer(
      beatmapURL,
      replayURL,
      replaySection.background,
      resolutionMultiplier
    )
    # print('initializing beatmap renderer done.')
  except Exception as e:
    replaySection.background = AppColors.background1

    activateAlert('Error initializing the renderer!')

    traceback.print_exc()
    print(e)
    return e

  mods = window.customData['beatmapRenderer'].beatmap.replay['mods']

  # load the audio file #
  try:
    audio = AudioSegment.from_file(audioFileURL)
    audioDurationMS = len(audio)

    print(f"Audio duration: {audioDurationMS} ms")

    if 'DT' in mods or 'NC' in mods:
      loadPgMusicAtSpeed(audio, 1.5)
    elif 'HT' in mods:
      loadPgMusicAtSpeed(audio, .75)
    else:
      if 'tmpAudioPath' in window.customData and os.path.exists(window.customData['tmpAudioPath']):
        pg.mixer.music.unload()
        os.remove(window.customData['tmpAudioPath'])
        del window.customData['tmpAudioPath']

      pg.mixer.music.load(audioFileURL)

    pg.mixer.music.set_volume(userData['volume'] / 2)
  except Exception as e:
    activateAlert('Couldn\'t load the audio!')

    traceback.print_exc()
    print(e)
    return e

  if 'DT' in mods or 'NC' in mods:
    audioDurationMS *= (2/3)
  elif 'HT' in mods:
    audioDurationMS *= (4/3)

  timelineRange = (0, audioDurationMS)

  timeline = window.systems['main'].elements['replayTimeline']
  timeline.valueRange = timelineRange
  timeline.value = timelineRange[0]

  timeStamp = window.systems['main'].elements['timeStamp']

  totalSecs = int(audioDurationMS / 1000)
  timeMS = int(audioDurationMS - (totalSecs * 1000))
  timeSecs = int(totalSecs % 60)
  timeMinutes = int(totalSecs / 60)

  timeStampMax = f'{timeMinutes:02d}:{timeSecs:02d}.{timeMS:03d}'

  timeStamp.text = f'00:00.000 / {timeStampMax}'

  window.customData['replayTimeStarted'] = False
  window.customData['replayPaused'] = True
  window.customData['pauseUnpauseTimeList'] = [[window.time.get_ticks()]]
  window.customData['pauseOffset'] = 0
  window.customData['userDragOffset'] = 0
  window.customData['timelineTimeLog'] = 0
  window.customData['replayLoaded'] = True
  window.customData['timeStampMax'] = timeStampMax

  deactivateAlert()

def loadRendererWithoutReplay():
  window: Window = sharedWindow.window
  pass
