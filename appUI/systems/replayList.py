from typing import Iterable
import os
import pygame as pg
from appUI.colors import AppColors
from modules.UI.UIElements import DynamicValue as DV, Section, Button, TextBox, System, Slider
from modules.UI.windowManager import Window
import sharedWindow

def getReplayElementY(params):
  system: System = params[0]
  replayNum: int = params[1]
  window: Window = params[2]

  mainHeight = system.elements['mainSection'].height
  scrollOffset = system.elements['scrollBar'].value
  relativePadding = 5
  absolutePadding = window.systems['nav'].elements['topNav'].height * .5

  return ((mainHeight * .05 * (replayNum - scrollOffset)) + (replayNum * relativePadding)) + absolutePadding

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
        'y': DV('customCallable', getReplayElementY, callableParameters=(system, replayNum, window)),
        'width': DV('classPer', system.elements['mainSection'], classAttr='width', percent=96),
        'height': DV('classPer', system.elements['mainSection'], classAttr='height', percent=5)
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

def addReplayList():
  window: Window = sharedWindow.window

  replayFolderURL = os.path.join(window.customData['userData']['URLs']['osuFolder'], 'Replays')

  dirList = os.listdir(replayFolderURL)

  system = System(preLoadState=True)

  replayNames = [file[0:len(file)-4] for file in dirList if file.endswith('.osr')]

  mainDim = {
    'x': DV('number', 1),
    'y': DV('number', 1),
    'width': DV('number', 1),
    'height': DV('number', 1)
  }

  system.addElement(Section(mainDim, AppColors.background1), 'mainSection')

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
    (0, len(replayNames)-1),
    -1,
    AppColors.listElement1,
    {
      'callable': system.update,
      'params': None,
      'sendValue': False
    },
    False
  )

  system.addElement(scrollBar, 'scrollBar')

  getReplayElements(replayNames, window, system)

  window.addSystem(system, 'replayList')
