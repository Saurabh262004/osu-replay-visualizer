from typing import Iterable
import os
import pygame as pg
from appUI.colors import AppColors
from modules.UI.UIElements import DynamicValue as DV, Section, Button, TextBox, System, Slider
from modules.UI.windowManager import Window
import sharedWindow

def getReplayElementY(params):
  window: Window = sharedWindow.window
  system: System = params[0]
  replayNum: int = params[1]

  mainHeight = system.elements['mainSection'].height
  scrollOffset = system.elements['scrollBar'].value
  relativePadding = 5
  absolutePadding = window.systems['nav'].elements['topNav'].height * .5

  return ((mainHeight * .05 * (replayNum - scrollOffset)) + (replayNum * relativePadding)) + absolutePadding

def setLoadReplay(replayName: str):
  window: Window = sharedWindow.window
  window.customData['loadReplay'] = replayName

def scrollReplayList(system: System):
  window: Window = sharedWindow.window

  system.update()

  for elementID in window.systems['replayList'].elements:
    if elementID.startswith('replayList-'):
      element = window.systems['replayList'].elements[elementID]
      if element.section.y > (window.screenHeight + element.section.height) or (element.section.height + element.section.y) < window.systems['nav'].elements['topNav'].height:
        element.activeEvents = False
        element.activeDraw = False
      else:
        element.activeDraw = True
        element.activeEvents = True

  system.update()

def getReplayElements(replayNames: Iterable[str], system: System):
  replayNum = 1

  for replayName in replayNames:
    replaySection = Button(
      Section(
      {
        'x': DV('classPer', system.elements['mainSection'], classAttr='width', percent=2),
        'y': DV('customCallable', getReplayElementY, callableParameters=(system, replayNum)),
        'width': DV('classPer', system.elements['mainSection'], classAttr='width', percent=96),
        'height': DV('classPer', system.elements['mainSection'], classAttr='height', percent=5)
      },
      AppColors.listElement1Heighlight2,
      borderRadius=5
      ),
      text = replayName,
      fontPath = 'Helvetica',
      textColor = AppColors.gray,
      pressedBackground = AppColors.listElement1Heighlight1,
      onClick = setLoadReplay,
      onClickParams = replayName
    )

    system.addElement(replaySection, f'replayList-{replayNum}')

    replayNum += 1

def addReplayList(system: System = None):
  window: Window = sharedWindow.window

  replayFolderURL = os.path.join(window.customData['userData']['URLs']['osuFolder'], 'Replays')

  dirList = os.listdir(replayFolderURL)

  replayFiles = [file for file in dirList if file.endswith('.osr')]

  replayFiles.sort(key=lambda file: os.path.getmtime(os.path.join(replayFolderURL, file)), reverse=True)

  replayNames = [file[:-4] for file in replayFiles]

  if system is None:
    system = System(preLoadState=True)

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
    -2,
    AppColors.listElement1,
    {
      'callable': scrollReplayList,
      'params': system,
      'sendValue': False
    },
    False
  )

  system.addElement(scrollBar, 'scrollBar')

  getReplayElements(replayNames, system)

  if not 'replayList' in window.systems:
    window.addSystem(system, 'replayList')

def refreshReplayList():
  window: Window = sharedWindow.window

  if 'replayList' in window.systems:
    delItems = []

    for elementID in window.systems['replayList'].elements:
      if not elementID == 'mainSection':
        delItems.append(elementID)

    [window.systems['replayList'].removeElement(delItem) for delItem in delItems]

    addReplayList(window.systems['replayList'])

    window.systems['replayList'].update()
