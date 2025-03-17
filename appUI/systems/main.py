from typing import Union
import pygame as pg
from appUI.colors import AppColors
from modules.UI.UIElements import DynamicValue as DV, Section, Circle, TextBox, Slider, System
from modules.UI.windowManager import Window
from replayHandlers.playbackHandler import timelineCallback

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

def addMain(window: Window):
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

  replaySection = Section(replaySectionDim, AppColors.background1, backgroundSizeType='none')

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
      'params': window,
      'sendValue': True
    }
  )

  system.addElement(replayTimeline, 'replayTimeline')

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
    -0.1,
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

  window.addSystem(system, 'main')
