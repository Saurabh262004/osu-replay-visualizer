import pygame as pg
from appUI.colors import AppColors
from modules.misc.helpers import tintImage
from modules.renderers.UIElements import *
from appUI.windowManager import Window

colors = AppColors()

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

  homeIcon = pg.image.load('assets/UI/home.png')

  tintImage(homeIcon, pg.Color(255, 255, 255))

  system.addElement(
    Button(
      Section(goToMainDim, homeIcon, backgroundSizeType='fit', backgroundSizePercent=50),
      onClick = window.switchSystem,
      onClickParams = 'main',
      onClickActuation = 'buttonUp'
    ), 'goToMainButton'
  )

  scrollBarDim = {
    'y': DynamicValue('number', 0),
    'width': DynamicValue('number', 8),
    'height': DynamicValue('classNum', system.elements['mainSection'], classAttr='height')
  }

  scrollBarDim['x'] = DynamicValue('customCallable', lambda mainSection: mainSection.width - 8, system.elements['mainSection'])

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
