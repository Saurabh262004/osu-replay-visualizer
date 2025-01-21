import os
import pygame as pg
from appUI.colors import AppColors
from modules.misc.helpers import tintImage
from modules.UI.UIElements import DynamicValue as DV, Section, TextBox, Button, System, Slider
from modules.UI.windowManager import Window
from typing import Iterable

def getReplayElementY(params):
  window: Window = params[0]
  system: System = params[1]
  replayNum: int = params[2]

  mainHeight = system.elements['mainSection'].height
  navHeight = window.systems['nav'].elements['topNav'].height
  padding = 5

  return (((mainHeight * (15 / 100)) * replayNum) + navHeight) + (replayNum * padding)

def getReplayElement(replayNames: Iterable[str], window: Window, system: System):
  replayNum = 0
  for replayName in replayNames:
    replaySection = Section(
      {
        'x': DV('classPer', system.elements['mainSection'], classAttr='width', percent=2),
        'y': DV('customCallable', getReplayElementY, callableParameters=(window, system, replayNum)),
        'width': DV('classPer', system.elements['mainSection'], classAttr='width', percent=96),
        'height': DV('classPer', system.elements['mainSection'], classAttr='height', percent=15)
      },
      AppColors.listElement1Heighlight2,
      borderRadius=10
    )
    system.addElement(replaySection, f'replayList-{replayNum}')

    textBox = TextBox(
      Section(
      {
        'x': DV('classNum', system.elements[f'replayList-{replayNum}'], classAttr='x'),
        'y': DV('classNum', system.elements[f'replayList-{replayNum}'], classAttr='y'),
        'width': DV('classNum', system.elements[f'replayList-{replayNum}'], classAttr='width'),
        'height': DV('classPer', system.elements[f'replayList-{replayNum}'], classAttr='height', percent=50)
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
    'x': DV('number', 1),
    'y': DV('number', 1),
    'width': DV('number', 1),
    'height': DV('number', 1)
  }

  system.addElement(
    Section(mainDim, AppColors.background1), 'mainSection'
  )

  getReplayElement(replayNames, window, system)

  scrollBarDim = {
    'y': DV('number', 0),
    'width': DV('number', 8),
    'height': DV('classNum', system.elements['mainSection'], classAttr='height')
  }

  scrollBarDim['x'] = DV('customCallable', lambda mainSection: mainSection.width - 8, system.elements['mainSection'])

  window.addSystem(system, 'replayList')
