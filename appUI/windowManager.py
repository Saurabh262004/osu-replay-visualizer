from typing import Iterable, Optional, Union, Dict
import pygame as pg
from modules.renderers.UIElements import *

numType = Union[int, float]

class Window:
  def __init__(self, title: str, screenRes: Iterable[int], minRes: Optional[Iterable[int]] = (480, 270), customLoopProcess: Optional[callable] = None, customUpdateProcess: Optional[callable] = None, customEventHandler: Optional[callable] = None, fps : Optional[int] = 60):
    self.title = title
    self.screenRes = screenRes
    self.customLoopProcess = customLoopProcess
    self.customEventHandler = customEventHandler
    self.customUpdateProcess = customUpdateProcess
    self.minRes = minRes
    self.screenWidth = max(self.screenRes[0], self.minRes[0])
    self.screenHeight = max(self.screenRes[1], self.minRes[1])
    self.fps = fps
    self.running = False
    self.systems: Dict[str, System] = {}
    self.currentSystem = None

  def addSystem(self, system: System, systemID: str) -> bool:
    if systemID in self.systems:
      print(f'A system with ID: {systemID} already exists. please enter a unique ID')
      return False

    if not system.locked:
      print('Provided system is not locked, switching the system to locked state and removing its surface.')
      system.locked = True
      system.surface = None

    if not 'mainSection' in system.elements:
      print('the system must have a section with id \"mainSection\"')
      return False

    self.systems[systemID] = system

    return True

  def openWindow(self, systemID: str):
    if not systemID in self.systems:
      print(f'cannot find a system with ID {systemID}')

    pg.init()

    time = pg.time
    clock = time.Clock()
    pg.display.set_caption(self.title)
    self.screen = pg.display.set_mode((self.screenWidth, self.screenHeight), pg.RESIZABLE)

    self.currentSystem = self.systems[systemID]

    self.currentSystem.initiate(self.screen)

    self.running = True
    self.__resetUI()
    self.currentSystem.draw()
    secondResize = False
    while self.running:
      self.__handleEvents()

      if secondResize or self.__screenResized():
        secondResize = not secondResize
        self.__resetUI()

      if self.customLoopProcess:
        self.customLoopProcess()

      self.screen.fill((0, 0, 0))
      self.currentSystem.draw()

      pg.display.flip()
      clock.tick(self.fps)

  def closeWindow(self):
    self.running = False
    self.currentSystem.locked = True
    self.currentSystem.surface = None
    self.currentSystem = None
    self.screen = None
    pg.quit()

  def switchSystem(self, systemID: str) -> bool:
    if not systemID in self.systems:
      print(f'A system with ID: {systemID} doesn\'t exists. please enter an existing system ID')
      return False

    if self.systems[systemID] == self.currentSystem:
      print(f'The window is already on the system with ID: {systemID}')
      return False

    self.currentSystem.locked = True
    self.currentSystem.surface = None
    self.currentSystem = self.systems[systemID]
    self.currentSystem.initiate(self.screen)
    self.__resetUI()
    self.currentSystem.draw()
    print(f'current system: {systemID}')

  def __handleEvents(self):
    if not self.running:
      return None

    for event in pg.event.get():
      if self.customEventHandler:
        self.customEventHandler(event)

      if event.type == pg.QUIT:
        self.running = False
      elif event.type == pg.VIDEORESIZE:
        new_width = max(self.minRes[0], event.w)
        new_height = max(self.minRes[1], event.h)
        self.screen = pg.display.set_mode((new_width, new_height), pg.RESIZABLE)
      else:
        self.currentSystem.handleEvents(event)

  def __screenResized(self) -> bool:
    if not self.running:
      return None

    tmpSW = self.screen.get_width()
    tmpSH = self.screen.get_height()

    if (self.screenWidth != tmpSW) or (self.screenHeight != tmpSH):
      self.screenWidth, self.screenHeight = self.screen.get_width(), self.screen.get_height()
      return True

    return False

  def __resetUI(self):
    if not self.running:
      return None

    self.currentSystem.elements['mainSection'].dimensions['width'].reference = self.screenWidth
    self.currentSystem.elements['mainSection'].dimensions['height'].reference = self.screenHeight

    if self.customUpdateProcess:
      self.customUpdateProcess()

    self.currentSystem.update()
