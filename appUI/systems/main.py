import pygame as pg
from appUI.colors import AppColors
from modules.UI.UIElements import DynamicValue as DV, Section, Circle, Slider, System
from modules.UI.windowManager import Window

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

  replaySection = Section(replaySectionDim, AppColors.primary1, backgroundSizeType='none')

  system.addElement(replaySection, 'replaySection')

  window.addSystem(system, 'main')
