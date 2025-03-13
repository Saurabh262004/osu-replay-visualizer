# import pygame as pg
from appUI.colors import AppColors
from modules.UI.UIElements import DynamicValue as DV, Section, Circle, Slider, System
from modules.UI.windowManager import Window
from replayHandlers.playbackHandler import timelineCallback

def toggleActivation(system: System):
  system.elements['replayListButton'].active = not system.elements['replayListButton'].active

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

  replaySectionDim = {
    'x': DV('number', 0),
    'y': DV('classNum', window.systems['nav'].elements['topNav'], classAttr='height'),
    'width': DV('classNum', window, classAttr='screenWidth'),
    'height': DV('customCallable', lambda window: window.screenHeight - window.systems['nav'].elements['topNav'].height, callableParameters=window)
  }

  replaySection = Section(replaySectionDim, AppColors.background1, backgroundSizeType='none')

  system.addElement(replaySection, 'replaySection')

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
    Section(replayTimelineDim, AppColors.listElement1Heighlight2, borderRadius=2),
    Section(replayTimelineDragDim, AppColors.cream, 2),
    (0, 100),
    1,
    AppColors.primary1,
    {
      'callable': timelineCallback,
      'params': window,
      'sendValue': True
    }
  )

  system.addElement(replayTimeline, 'replayTimeline')

  window.addSystem(system, 'main')
