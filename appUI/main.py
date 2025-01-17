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
      Section(activationButtonDim, pg.image.load('assets/UI/alert-circle.png')),
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
      Section(replayListButtonDim, pg.image.load('assets/UI/alert-circle.png')),
      onClick = window.switchSystem,
      onClickParams = 'replayList',
      onClickActuation = 'buttonUp'
    ), 'replayListButton'
  )

  slider1 = Slider(
    'horizontal',
    Section(
      {
        'x': DynamicValue('classPer', system.elements['mainSection'], classAttr='width', percent=25),
        'y': DynamicValue('classPer', system.elements['mainSection'], classAttr='height', percent=70),
        'width': DynamicValue('classPer', system.elements['mainSection'], classAttr='width', percent=50),
        'height': DynamicValue('number', 8)
      }, colors.listElement1Heighlight1, 5
    ),
    Circle(
      {
        'x': DynamicValue('number', 0),
        'y': DynamicValue('number', 0),
        'radius': DynamicValue('number', 8)
      }, colors.primary1
    ),
    (0, 99),
    5,
    colors.primary1,
    {
      'callable': lambda param: print(f'slider value: {param}'),
      'params': None,
      'sendValue': True
    }
  )
  
  slider2 = Slider(
    'vertical',
    Section(
      {
        'x': DynamicValue('classPer', system.elements['mainSection'], classAttr='width', percent=90),
        'y': DynamicValue('classPer', system.elements['mainSection'], classAttr='height', percent=20),
        'width': DynamicValue('number', 8),
        'height': DynamicValue('classPer', system.elements['mainSection'], classAttr='height', percent=60)
      }, colors.listElement1Heighlight1
    ),
    Section(
      {
        'x': DynamicValue('number', 0),
        'y': DynamicValue('number', 0),
        'width': DynamicValue('number', 8),
        'height': DynamicValue('number', 12)
      }, colors.primary1, 5
    ),
    (0, 99),
    -5,
    colors.listElement1Heighlight1,
    {
      'callable': lambda param: print(f'slider value: {param}'),
      'params': None,
      'sendValue': True
    }
  )

  system.addElement(slider1, 'newTestSlider1')
  system.addElement(slider2, 'newTestSlider2')

  window.addSystem(system, 'main')
