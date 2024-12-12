# a module that helps render stuff on screen with pygame
# import pygame as pg
from typing import Union

numType = Union[int, float]

class Section:
  def __init__(self, x: numType, y: numType, width: numType, height: numType):
    self.x = x
    self.y = y
    self.width = width
    self.height = height


