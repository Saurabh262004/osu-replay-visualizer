import pygame as pg
from appUI.colors import AppColors
from modules.renderers.UIElements import *
from appUI.windowManager import Window

colors = AppColors()

def toggleActivation(system):
  system.elements['replayListButton'].active = not system.elements['replayListButton'].active

def addMain(window: Window):
  system = System(preLoadState=True)

  mainDim = {
    'x': DynamicValue('number', 0),
    'y': DynamicValue('number', 0),
    'width': DynamicValue('number', 0),
    'height': DynamicValue('number', 0)
  }

  system.addElement(
    Section(mainDim, colors.background1), 'mainSection'
  )

  activationButtonDim = {
    'x': DynamicValue('number', 0),
    'y': DynamicValue('number', 0),
    'width': DynamicValue('classPer', system.elements['mainSection'], classAttr='width', percent=10),
    'height': DynamicValue('classPer', system.elements['mainSection'], classAttr='width', percent=10)
  }

  system.addElement(
    Button(
      Section(activationButtonDim, pg.image.load('assets/UI/pfp.png')),
      onClick = toggleActivation,
      onClickParams = system
    ), 'replayListButtonActivation'
  )

  replayListButtonDim = {
    'x': DynamicValue('classPer', system.elements['mainSection'], classAttr='width', percent=90),
    'y': DynamicValue('number', 0),
    'width': DynamicValue('classPer', system.elements['mainSection'], classAttr='width', percent=10),
    'height': DynamicValue('classPer', system.elements['mainSection'], classAttr='width', percent=10)
  }

  system.addElement(
    Button(
      Section(replayListButtonDim, pg.image.load('assets/UI/pfp.png')),
      onClick = window.switchSystem,
      onClickParams = 'replayList',
      onClickActuation = 'buttonUp'
    ), 'replayListButton'
  )

  window.addSystem(system, 'main')
