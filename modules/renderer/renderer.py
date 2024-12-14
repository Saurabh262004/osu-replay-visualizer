# a module that helps render stuff on screen with pygame
import pygame as pg
from typing import Union, Optional, Callable

numType = Union[int, float]
containerType = Union['Section', pg.Rect]
backgroundType = Union[pg.Color, pg.Surface]

def draw_text(screen, text, font, textCol, x, y):
  img = font.render(text, True, textCol)
  screen.blit(img, (x, y))

class Section:
  def __init__(self, xRatio: numType, yRatio: numType, widthRatio: numType, heightRatio: numType, container: Optional[containerType], background: backgroundType, absolutePositioning: Optional[bool] = True):
    self.absolutePositioning = absolutePositioning
    self.background = background
    self.rect = pg.Rect(0, 0, 0, 0)

    if not container:
      self.absolutePositioning = True

    if absolutePositioning:
      self.rect.x = self.x = xRatio
      self.rect.y = self.y = yRatio
      self.rect.width = self.width = widthRatio
      self.rect.height = self.height = heightRatio
    elif container:
      self.rect.x = self.x = container.x + container.width * xRatio
      self.rect.y = self.y = container.y + container.height * yRatio
      self.rect.width = self.width = container.width * widthRatio
      self.rect.height = self.height = container.height * heightRatio
      self.container = container
      self.xRatio = xRatio
      self.yRatio = yRatio
      self.widthRatio = widthRatio
      self.heightRatio = heightRatio

  def updateDim(self):
    if not self.absolutePositioning:
      self.rect.x = self.x = self.container.x + self.container.width * self.xRatio
      self.rect.y = self.y = self.container.y + self.container.height * self.yRatio
      self.rect.width = self.width = self.container.width * self.widthRatio
      self.rect.height = self.height = self.container.height * self.heightRatio
  
  def draw(self, surface: pg.Surface):
    if isinstance(self.background, pg.Surface):
      surface.blit(self.background)
    elif isinstance(self.background, pg.Color):
      pg.draw.rect(surface, self.background, self.rect)

class Button:
  def __init__(self, section: Section, text: str, onClick: Optional[Callable] = None, border: int = 0):
    self.section = section
    self.text = text
    self.onClick = onClick
    self.border = border
