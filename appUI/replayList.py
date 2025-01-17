import os
import pygame as pg
from appUI.colors import AppColors
from modules.misc.helpers import tintImage
from modules.renderers.UIElements import *
from appUI.windowManager import Window
from typing import Iterable

colors = AppColors()

def getReplayElementY(params):
  system = params[0]
  mainHeight = system.elements['mainSection'].height
  navHeight = system.elements['topNav'].height
  replayNum = params[1]
  padding = 5

  return (((mainHeight * (15 / 100)) * replayNum) + navHeight) + (replayNum * padding)

def getReplayElement(replayNames: Iterable[str], system: System):
  replayNum = 0
  for replayName in replayNames:
    replaySection = Section(
      {
        'x': DynamicValue('classPer', system.elements['mainSection'], classAttr='width', percent=2),
        'y': DynamicValue('customCallable', getReplayElementY, callableParameters=(system, replayNum)),
        'width': DynamicValue('classPer', system.elements['mainSection'], classAttr='width', percent=96),
        'height': DynamicValue('classPer', system.elements['mainSection'], classAttr='height', percent=15)
      },
      colors.listElement1Heighlight2,
      borderRadius=10
    )
    system.addElement(replaySection, f'replayList-{replayNum}')

    textBox = TextBox(
      Section(
      {
        'x': DynamicValue('classNum', system.elements[f'replayList-{replayNum}'], classAttr='x'),
        'y': DynamicValue('classNum', system.elements[f'replayList-{replayNum}'], classAttr='y'),
        'width': DynamicValue('classNum', system.elements[f'replayList-{replayNum}'], classAttr='width'),
        'height': DynamicValue('classPer', system.elements[f'replayList-{replayNum}'], classAttr='height', percent=50)
      },
      pg.Color(0, 0, 0)
      ), replayName, 'Helvetica', pg.Color(200, 200, 200)
    )

    system.addElement(textBox, f'replayListText-{replayNum}')
    replayNum += 1

def addReplayList(window: Window, userData: dict):
  replayFolderURL = os.path.join(userData['URLs']['osuURL'], 'Replays')

  dirList = os.listdir(replayFolderURL)

  replayNames = []

  for file in dirList:
    if file.endswith('.osr'):
      replayNames.append(file[0:len(file)-4])

  print(replayNames)

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

  tintImage(homeIcon, pg.Color(200, 200, 200))

  system.addElement(
    Button(
      Section(goToMainDim, homeIcon, backgroundSizeType='fit', backgroundSizePercent=50),
      onClick = window.switchSystem,
      onClickParams = 'main',
      onClickActuation = 'buttonUp'
    ), 'goToMainButton'
  )

  getReplayElement(replayNames, system)

  scrollBarDim = {
    'y': DynamicValue('number', 0),
    'width': DynamicValue('number', 8),
    'height': DynamicValue('classNum', system.elements['mainSection'], classAttr='height')
  }

  scrollBarDim['x'] = DynamicValue('customCallable', lambda mainSection: mainSection.width - 8, system.elements['mainSection'])

  window.addSystem(system, 'replayList')
