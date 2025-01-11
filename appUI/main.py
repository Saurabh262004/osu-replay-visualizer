import pygame as pg
from appUI.colors import AppColors
from modules.renderers.UIElements import *
from appUI.windowManager import Window

colors = AppColors()

def addMain(window: Window):
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
        Section.createDimObject(('rw', .9, 'a', 0, 'rw', .1, 'rw', .1)),
        pg.image.load('assets/UI/pfp.png'),
        system.elements['mainSection']
      ),
      colors.listElement1Heighlight1,
      onClick = window.switchSystem,
      onClickParams = 'replayList'
    ), 'replayListButton'
  )

  window.addSystem(system, 'main')
