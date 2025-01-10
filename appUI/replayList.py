import pygame as pg
from appUI.colors import AppColors
from modules.renderers.UIElements import *
from appUI.windowManager import Window

colors = AppColors()

def addReplayList(window: Window):
  system = System(preLoadState=True)

  system.addElement(
    Section(
      Section.createDimObject(('a', 0, 'a', 0, 'rw', 1, 'rh', 1)),
      colors.background1,
      pg.Rect(0, 0, 100, 100)
    ), 'mainSection'
  )

  system.addElement(
    Button(
      Section(
        Section.createDimObject(('rw', .4, 'rh', .7, 'rw', .2, 'rh', .2)),
        colors.listElement1,
        system.elements['mainSection']
      ),
      colors.listElement1Heighlight1,
      colors.b,
      colors.b,
      onClick = window.switchSystem,
      onClickParams = 'main'
    ), 'dumyButton'
  )

  system.addElement(
    RangeSlider(
      Section(
        Section.createDimObject(('rw', .25, 'rh', .5, 'rw', .5, 'a', 8)),
        colors.background1,
        system.elements['mainSection']
      ),
      (1, 100),
      colors.gray,
      colors.primary1,
      8,
      colors.primary1
    ), 'dummyRange'
  )

  window.addSystem(system, 'replayList')
