import pygame as pg
from typing import Any
from modules.misc.helpers import tintImage
from appUI.colors import AppColors
from modules.UI.UIElements import DynamicValue as DV, Section, Button, System
from modules.UI.windowManager import Window
from appUI.systems.replayList import refreshReplayList
import sharedWindow

def setLoggedSystemSwitch(systemID: str):
  sharedWindow.window.loggedSystemSwitch = systemID

def addNavButton(system: System, iconName: pg.Surface, callback: callable, callbackParams: Any, pos: int, buttonID: str):
  buttonDim = {
    'x': DV('classPer', system.elements['topNav'], classAttr='height', percent=100*pos),
    'y': DV('number', 0),
    'width': DV('classNum', system.elements['topNav'], classAttr='height'),
    'height': DV('classNum', system.elements['topNav'], classAttr='height')
  }

  buttonIcon = pg.image.load(f'assets/UI/{iconName}.png')

  tintImage(buttonIcon, pg.Color(200, 200, 200))

  system.addElement(
    Button(
      Section(buttonDim, buttonIcon, backgroundSizeType='fit', backgroundSizePercent=50),
      onClick = callback,
      onClickParams = callbackParams,
      onClickActuation = 'buttonUp'
    ), buttonID
  )

def addNav():
  window: Window = sharedWindow.window

  system = System(preLoadState=True)

  system.addElement(
    Section({
      'x': DV('number', 0),
      'y': DV('number', 0),
      'width': DV('number', 1),
      'height': DV('number', 1)
    }, pg.Color(200, 200, 200)), 'mainSection'
  )

  system.elements['mainSection'].activeDraw = False

  system.addElement(
    Section({
      'x': DV('number', 0),
      'y': DV('number', 0),
      'width': DV('classNum', system.elements['mainSection'], classAttr='width'),
      'height': DV('classPer', system.elements['mainSection'], classAttr='height', percent=7)
    }, AppColors.listElement1), 'topNav'
  )

  addNavButton(system, 'home', setLoggedSystemSwitch, 'main', 0, 'goToHome')
  addNavButton(system, 'list', setLoggedSystemSwitch, 'replayList', 1, 'goToReplayList')
  addNavButton(system, 'refresh', refreshReplayList, None, 2, 'refreshReplayList')
  addNavButton(system, 'settings', setLoggedSystemSwitch, 'settings', 3, 'goToSettings')

  window.addSystem(system, 'nav')
