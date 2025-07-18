from typing import Union
import pygame as pg
from modules.misc.helpers import tintImage
from appUI.colors import AppColors
from modules.UI.UIElements import DynamicValue as DV, Section, TextBox, Button, Slider, System
from modules.UI.windowManager import Window
import sharedWindow
from replayHandlers.playbackHandler import timelineCallback, pauseToggle

def toggleActivation(system: System):
  system.elements['replayListButton'].active = not system.elements['replayListButton'].active

def setUserVolume(volume: Union[int, float], window: Window):
  volume = round(volume, 2)

  if volume < 0:
    volume = 0
  elif volume > 1:
    volume = 1

  window.customData['userData']['volume'] = volume

  audioIndicator = window.systems['main'].elements['audioIndicator']
  audioIndicator.text = f'{volume:.2f}'
  audioIndicator.update()

  pg.mixer.music.set_volume(volume / 2)

  if 'skin' in window.customData:
    for hitsound in window.customData['skin']['hitsounds']:
      window.customData['skin']['hitsounds'][hitsound].set_volume(volume / 3)

def addMain():
  window: Window = sharedWindow.window

  system = System(preLoadState=True)

  mainDim = {
    'x': DV('number', 0),
    'y': DV('number', 0),
    'width': DV('number', 0),
    'height': DV('number', 0)
  }

  system.addElement(
    Section(mainDim, AppColors.background1), 'mainSection'
  )

  # replay screen #
  replaySectionDim = {
    'x': DV('number', 0),
    'y': DV('classNum', window.systems['nav'].elements['topNav'], classAttr='height'),
    'width': DV('classNum', window, classAttr='screenWidth'),
    'height': DV('customCallable', lambda window: window.screenHeight - window.systems['nav'].elements['topNav'].height, window)
  }

  replaySection = Section(replaySectionDim, AppColors.b, backgroundSizeType='none')

  system.addElement(replaySection, 'replaySection')

  # replay timeline #
  replayTimelineDim = {
    'x': DV('classPer', window, classAttr='screenWidth', percent=10),
    'y': DV('classPer', window, classAttr='screenHeight', percent=90),
    'width': DV('classPer', window, classAttr='screenWidth', percent=80),
    'height': DV('number', 6)
  }

  replayTimelineDragDim = {
    'x': DV('number', 0),
    'y': DV('number', 0),
    'width': DV('classPer', window, classAttr='screenWidth', percent=2),
    'height': DV('number', 6)
  }

  replayTimeline = Slider(
    'horizontal',
    Section(replayTimelineDim, AppColors.listElement1, borderRadius=2),
    Section(replayTimelineDragDim, AppColors.cream, 2),
    (0, 100),
    500,
    AppColors.darkGray,
    {
      'callable': timelineCallback,
      'params': None,
      'sendValue': True
    }
  )

  system.addElement(replayTimeline, 'replayTimeline')

  playbackButtonWidth = DV('classPer', window, classAttr='screenWidth', percent=4)
  playbackButtonHeight = DV('classNum', playbackButtonWidth, classAttr='value')

  # pause / play button #
  pausePlayButtonDim = {
    'x': DV('customCallable', lambda params: params[0].x - (params[1].value * 1.5), (replayTimeline.section, playbackButtonWidth)),
    'y': DV('customCallable', lambda params: (params[0].y + (params[0].height / 2)) - (params[1].value / 2), (replayTimeline.section, playbackButtonHeight)),
    'width': playbackButtonWidth,
    'height': playbackButtonHeight
  }

  playButtonIcon = pg.image.load('assets/UI/play-square.png')
  tintImage(playButtonIcon, AppColors.cream)

  playbackButtonSection = Section(
    pausePlayButtonDim,
    playButtonIcon
  )

  playbackButton = Button(
    playbackButtonSection,
    onClick=pauseToggle
  )

  system.addElement(playbackButton, 'playbackButton')

  # timeStamp TextBox #
  timeStampSectionDim = {
    'x': DV('classPer', window, classAttr='screenWidth', percent=10),
    'y': DV('customCallable', lambda timeline: timeline.section.y + 11, replayTimeline),
    'width': DV('number', 200),
    'height': DV('number', 25)
  }

  timeStamp = TextBox(
    Section(
      timeStampSectionDim,
      AppColors.gray
    ),
    '--:-- / --:--',
    'Courier New',
    AppColors.cream
  )

  system.addElement(timeStamp, 'timeStamp')

  # audio control slider #
  audioControlDim = {
    'x': DV('classPer', window, classAttr='screenWidth', percent=97),
    'y': DV('classPer', window, classAttr='screenHeight', percent=80),
    'width': DV('number', 6),
    'height': DV('classPer', window, classAttr='screenHeight', percent=15)
  }

  audioControlDragDim = {
    'x': DV('number', 0),
    'y': DV('number', 0),
    'width': DV('number', 6),
    'height': DV('classPer', window, classAttr='screenHeight', percent=2)
  }

  audioControl = Slider(
    'vertical',
    Section(audioControlDim, AppColors.darkGray, borderRadius=2),
    Section(audioControlDragDim, AppColors.cream, 2),
    (1, 0),
    -0.05,
    AppColors.listElement1,
    {
      'callable': setUserVolume,
      'params': window,
      'sendValue': True
    }
  )

  audioControl.value = window.customData['userData']['volume']

  system.addElement(audioControl, 'audioControl')

  # audio indicator #
  audioIndicatorSectionDim = {
    'x': DV('customCallable', lambda audioControl: audioControl.section.x - 40, audioControl),
    'y': DV('customCallable', lambda audioControl: (audioControl.section.y + audioControl.section.height) - 20, audioControl),
    'width': DV('number', 40),
    'height': DV('number', 20)
  }

  audioIndicator = TextBox(
    Section(
      audioIndicatorSectionDim,
      AppColors.gray
    ),
    f'{audioControl.value:.2f}',
    'Courier New',
    AppColors.cream
  )

  system.addElement(audioIndicator, 'audioIndicator')

  # alerts and error messages #
  UED_X = DV('classPer', window, classAttr='screenWidth', percent=35)
  UED_WIDTH = DV('classPer', window, classAttr='screenWidth', percent=30)
  UED_HEIGHT = DV('classPer', window, classAttr='screenWidth', percent=15)
  UED_Y = DV('customCallable', lambda params: (params[0].screenHeight - params[1].value) / 2, callableParameters=(window, UED_HEIGHT))

  errorDim = {
    'x': UED_X,
    'y': UED_Y,
    'width': UED_WIDTH,
    'height': UED_HEIGHT
  }

  alertBox = Section(errorDim, pg.Color(241, 188, 208), 7, 'fit', 20)

  system.addElement(alertBox, 'alertBox')

  AID_HEIGHT = DV('classPer', UED_HEIGHT, classAttr='value', percent=20)
  AID_WIDTH = DV('classNum', AID_HEIGHT, classAttr='value')
  AID_Y = DV('customCallable', lambda params: params[0].value + (params[1].value / 2), callableParameters=(UED_Y, AID_HEIGHT))
  AID_X = DV('customCallable', lambda params: params[0].value + ((params[1].value - params[2].value) / 2), callableParameters=(UED_X, UED_WIDTH, AID_WIDTH))

  alertIconDim = {
    'x': AID_X,
    'y': AID_Y,
    'width': AID_WIDTH,
    'height': AID_HEIGHT
  }

  alertIconImg = pg.image.load(f'assets/UI/alert-circle.png')

  tintImage(alertIconImg, AppColors.background1)

  alertIcon = Section(alertIconDim, alertIconImg)

  system.addElement(alertIcon, 'alertIcon')

  alertTextBox = Section(
    {
      'x': UED_X,
      'y': DV('customCallable', lambda params: params[0].value + (params[1].value * 2.3), callableParameters=(UED_Y, AID_HEIGHT)),
      'width': UED_WIDTH,
      'height': DV('classPer', UED_HEIGHT, classAttr='value', percent=25)
    },
    AppColors.darkGray
  )

  alertText = TextBox(alertTextBox, '-', 'Helvetica', AppColors.background1)

  system.addElement(alertText, 'alertText')

  FPSDim = {
    'x' : DV('number', 5),
    'y' : DV('customCallable', lambda window: window.systems['nav'].elements['topNav'].height + 5, callableParameters=window),
    'width' : DV('number', 20),
    'height' : DV('number', 20)
  }

  FPSBox = TextBox(
    Section(FPSDim, pg.Color(0, 0, 0, 0)),
    '00',
    'Courier New',
    AppColors.cream
  )

  system.addElement(FPSBox, 'FPSBox')

  window.addSystem(system, 'main')
