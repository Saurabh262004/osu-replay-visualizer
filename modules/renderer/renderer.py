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
      self.x, self.y = xRatio, yRatio
      self.width, self.height = widthRatio, heightRatio
      self.rect.update(self.x, self.y, self.width, self.height)
    elif container:
      self.x = container.x + container.width * xRatio
      self.y = container.y + container.height * yRatio
      self.width = container.width * widthRatio
      self.height = container.height * heightRatio
      self.container = container
      self.xRatio = xRatio
      self.yRatio = yRatio
      self.widthRatio = widthRatio
      self.heightRatio = heightRatio
      self.rect.update(self.x, self.y, self.width, self.height)

  def updateDim(self):
    if not self.absolutePositioning:
      self.x = self.container.x + self.container.width * self.xRatio
      self.y = self.container.y + self.container.height * self.yRatio
      self.width = self.container.width * self.widthRatio
      self.height = self.container.height * self.heightRatio
      self.rect.update(self.x, self.y, self.width, self.height)

  def draw(self, surface: pg.Surface):
    if isinstance(self.background, pg.Surface):
      surface.blit(self.background)
    elif isinstance(self.background, pg.Color):
      pg.draw.rect(surface, self.background, self.rect)

class Button:
  def __init__(self, section: Section, text: str, pressedColor: pg.Color, borderColor: pg.Color, borderColorPressed: pg.Color, onClick: Optional[Callable] = None, border: int = 0):
    self.section = section
    self.text = text
    self.onClick = onClick
    self.border = border
    self.pressed = False
    self.defaultBackground = section.background
    self.pressedBackground = pressedColor
    self.borderColor = borderColor
    self.borderColorPressed = borderColorPressed
    self.borderRect = pg.Rect(section.x - border, section.y - border, section.width + (border * 2), section.height + (border * 2))

  def checkEvent(self, event: pg.event.Event):
    if event.type == pg.MOUSEBUTTONDOWN and event.button == 1 and self.section.rect.collidepoint(event.pos):
      self.pressed = True
      self.section.background = self.pressedBackground
      if self.onClick:
        self.onClick()
    elif event.type == pg.MOUSEBUTTONUP and self.pressed:
      self.pressed = False
      self.section.background = self.defaultBackground

  def updateDim(self):
    self.section.updateDim()
    newX, newY = self.section.x - self.border, self.section.y - self.border
    newWidth, newHeight = self.section.width + (self.border * 2), self.section.height + (self.border * 2)
    self.borderRect.update(newX, newY, newWidth, newHeight)

  def draw(self, surface):
    if self.border > 0:
      if self.pressed:
        pg.draw.rect(surface, self.borderColorPressed, self.borderRect)
      else:
        pg.draw.rect(surface, self.borderColor, self.borderRect)
    self.section.draw(surface)
