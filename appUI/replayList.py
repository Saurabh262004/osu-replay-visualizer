import pygame as pg
from appUI.colors import AppColors
from modules.renderers.UIElements import *
from appUI.windowManager import Window

colors = AppColors()

def dynamicScrollX(params):
  mainSectionWidth = params[0].width
  scrollbarWidth = params[1].value

  return mainSectionWidth - scrollbarWidth

def addReplayList(window: Window):
  system = System(preLoadState=True)

  mainDim = {
    'x': DynamicValue('number', 1),
    'y': DynamicValue('number', 1),
    'width': DynamicValue('number', 1),
    'height': DynamicValue('number', 1)
  }

  system.addElement(
    Section(mainDim, colors.background1), 'mainSection'
  )
  
  topNavDim = {
    'x': DynamicValue('number', 0),
    'y': DynamicValue('number', 0),
    'width': DynamicValue('classNum', system.elements['mainSection'], classAttr='width'),
    'height': DynamicValue('classPer', system.elements['mainSection'], classAttr='height', percent=10)
  }

  system.addElement(
    Section(topNavDim, colors.listElement1), 'topNav'
  )
  
  goToMainDim = {
    'x': DynamicValue('number', 0),
    'y': DynamicValue('number', 0),
    'width': DynamicValue('classNum', system.elements['topNav'], classAttr='height'),
    'height': DynamicValue('classNum', system.elements['topNav'], classAttr='height')
  }

  system.addElement(
    Button(
      Section(goToMainDim, colors.listElement1Heighlight2),
      onClick = window.switchSystem,
      onClickParams = 'main'
    ), 'goToMainButton'
  )
  
  scrollBarDim = {
    'y': DynamicValue('number', 0),
    'width': DynamicValue('classPer', system.elements['mainSection'], classAttr='width', percent=1),
    'height': DynamicValue('classNum', system.elements['mainSection'], classAttr='height')
  }

  scrollBarDim['x'] = DynamicValue('customCallable', dynamicScrollX, (system.elements['mainSection'], scrollBarDim['width']))

  system.addElement(
    RangeSliderVertical(
      Section(scrollBarDim, colors.background1),
      (1, 100),
      colors.listElement1,
      colors.listElement1,
      4,
      colors.primary1,
      hoverToScroll=False,
      scrollSpeed=-10
    ), 'scrollBar'
  )

  window.addSystem(system, 'replayList')
 