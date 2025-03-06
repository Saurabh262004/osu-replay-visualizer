from typing import Iterable
import os
import pygame as pg
from appUI.colors import AppColors
from modules.UI.UIElements import DynamicValue as DV, Section, Button, TextBox, System, Slider
from modules.UI.windowManager import Window

def getReplayElementY(params):
  system: System = params[0]
  replayNum: int = params[1]

  mainHeight = system.elements['mainSection'].height
  padding = 5

  return (((mainHeight * (7 / 100)) * replayNum) + (replayNum * padding)) + 15

def setLoadReplay(params):
  window = params[0]
  replayName = params[1]
  window.customData['loadReplay'] = replayName

def getReplayElements(replayNames: Iterable[str], window: Window, system: System):
  replayNum = 1
  for replayName in replayNames:
    replaySection = Button(
      section = Section(
      {
        'x': DV('classPer', system.elements['mainSection'], classAttr='width', percent=2),
        'y': DV('customCallable', getReplayElementY, callableParameters=(system, replayNum)),
        'width': DV('classPer', system.elements['mainSection'], classAttr='width', percent=96),
        'height': DV('classPer', system.elements['mainSection'], classAttr='height', percent=7)
      },
      AppColors.listElement1Heighlight2,
      borderRadius=5
      ),
      pressedBackground = AppColors.listElement1Heighlight1,
      onClick = setLoadReplay,
      onClickParams = (window, replayName)
    )
    system.addElement(replaySection, f'replayList-{replayNum}')

    textBox = TextBox(
      Section(
      {
        'x': DV('classNum', system.elements[f'replayList-{replayNum}'].section, classAttr='x'),
        'y': DV('classNum', system.elements[f'replayList-{replayNum}'].section, classAttr='y'),
        'width': DV('classNum', system.elements[f'replayList-{replayNum}'].section, classAttr='width'),
        'height': DV('classNum', system.elements[f'replayList-{replayNum}'].section, classAttr='height')
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

  system.addElement(Section(mainDim, AppColors.background1), 'mainSection')

  getReplayElements(replayNames, window, system)

  scrollBarDim = {
    'x': DV('customCallable', lambda mainSection: mainSection.width - 8, system.elements['mainSection']),
    'y': DV('classNum', window.systems['nav'].elements['topNav'], classAttr='height'),
    'width': DV('number', 8),
    'height': DV('customCallable', lambda nav: nav.elements['mainSection'].height - nav.elements['topNav'].height, window.systems['nav'])
  }

  scrollBarDragDim = {
    'x': DV('number', 0),
    'y': DV('number', 0),
    'width': DV('number', 8),
    'height': DV('number', 16)
  }

  scrollBar = Slider(
    'vertical',
    Section(scrollBarDim, AppColors.listElement1),
    Section(scrollBarDragDim, AppColors.primary1),
    (0, 99),
    -5,
    AppColors.listElement1,
    {
      'callable': lambda param: print(f'slider value: {param}'),
      'params': None,
      'sendValue': True
    },
    False
  )

  system.addElement(scrollBar, 'scrollBar')

  window.addSystem(system, 'replayList')
