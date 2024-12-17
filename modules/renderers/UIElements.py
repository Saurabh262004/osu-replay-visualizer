# a module that helps render stuff on screen with pygame
import pygame as pg
from typing import Union, Optional, Callable, Dict

numType = Union[int, float]
containerType = Union['Section', pg.Rect]
backgroundType = Union[pg.Color, pg.Surface]

DIMENSIONS_ALLOWED_KEYVALS = (
  ('x', 'y', 'w', 'h'),
  ('type', 'value'),
  ('a', 'r')
)

class Section:
  def __init__(self, dimensions: Dict[str, Dict[str, Union[str, int, float]]], container: Optional[containerType], background: backgroundType):
    self.dimensions = dimensions
    self.container = container
    self.background = background
    self.rect = pg.Rect(0, 0, 0, 0)

    if not self.__validDims():
      print('invalid dimension object')
      return None

    if not container:
      dim = self.dimensions
      for d in dim:
        if not dim[d]['type'] == 'a':
          dim[d]['type'] = 'a'

    self.updateDim()

  def updateDim(self):
    dim = self.dimensions
    for d in dim:
      typ = dim[d]['type']
      if typ == 'a':
        dim[d]['calcVal'] = dim[d]['value']
      elif typ[0] == 'r':
        rel = self.__getRel(typ[1])
        val = dim[d]['value']
        padding = self.__getPadding(d)

        dim[d]['calcVal'] = padding + (rel * val)

    self.x = self.dimensions['x']['calcVal']
    self.y = self.dimensions['y']['calcVal']
    self.width = self.dimensions['w']['calcVal']
    self.height = self.dimensions['h']['calcVal']

    self.rect.update(self.x, self.y, self.width, self.height)

  def draw(self, surface: pg.Surface):
    if isinstance(self.background, pg.Surface):
      surface.blit(self.background)
    elif isinstance(self.background, pg.Color):
      pg.draw.rect(surface, self.background, self.rect)

  def __getRel(self, typ):
    if typ == 'x':
      return self.container.x
    if typ == 'y':
      return self.container.y
    if typ == 'w':
      return self.container.width
    if typ == 'h':
      return self.container.height

  def __getPadding(self, key):
    if key == 'x':
      return self.container.x
    if key == 'y':
      return self.container.y
    return 0

  def __validDims(self):
    dim = self.dimensions
    if (set(self.dimensions.keys()) == set(DIMENSIONS_ALLOWED_KEYVALS[0])):
      for d in dim:
        if (set(dim[d].keys()) == set(DIMENSIONS_ALLOWED_KEYVALS[1])):
          if dim[d]['type'][0] in DIMENSIONS_ALLOWED_KEYVALS[2]:
            if dim[d]['type'][0] == 'r':
              if (len(dim[d]['type']) == 2) and dim[d]['type'][1] in DIMENSIONS_ALLOWED_KEYVALS[0]:
                return True
              else: break
            return True
          else: break
        else: break
    return False

  @staticmethod
  def createDimObject(arr):
    return {
      'x': {'type': arr[0], 'value': arr[1]},
      'y': {'type': arr[2], 'value': arr[3]},
      'w': {'type': arr[4], 'value': arr[5]},
      'h': {'type': arr[6], 'value': arr[7]}
    }

class Button:
  def __init__(self, section: Section, text: str, fontPath: str, textColor: pg.Color, pressedColor: pg.Color, borderColor: pg.Color, borderColorPressed: pg.Color, onClick: Optional[Callable] = None, border: int = 0):
    self.section = section
    self.onClick = onClick
    self.border = border
    self.pressed = False
    self.defaultBackground = section.background
    self.pressedBackground = pressedColor
    self.borderColor = borderColor
    self.borderColorPressed = borderColorPressed
    self.borderRect = pg.Rect(section.x - border, section.y - border, section.width + (border * 2), section.height + (border * 2))

    self.text = text
    self.textColor = textColor
    self.fontPath = fontPath

    self.updateDim()

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

    self.fontSize = max(10, int(self.section.height * .6))
    self.font = pg.font.SysFont(self.fontPath, self.fontSize)

    self.textSurface = self.font.render(self.text, True, self.textColor)
    self.textRect = self.textSurface.get_rect(center = self.section.rect.center)

  def draw(self, surface):
    if self.border > 0:
      if self.pressed:
        pg.draw.rect(surface, self.borderColorPressed, self.borderRect)
      else:
        pg.draw.rect(surface, self.borderColor, self.borderRect)

    self.section.draw(surface)

    surface.blit(self.textSurface, self.textRect)

class Toggle:
  def __init__(self, section: Section, toggledColor: pg.Color, borderColor: pg.Color, borderColorToggled: pg.Color, onClick: Optional[Callable] = None, border: int = 0):
    self.section = section
    self.onClick = onClick
    self.border = border
    self.toggled = False
    self.defaultBackground = section.background
    self.toggledBackground = toggledColor
    self.borderColor = borderColor
    self.borderColorToggled = borderColorToggled
    self.borderRect = pg.Rect(section.x - border, section.y - border, section.width + (border * 2), section.height + (border * 2))

  def checkEvent(self, event: pg.event.Event):
    if event.type == pg.MOUSEBUTTONDOWN and event.button == 1 and self.section.rect.collidepoint(event.pos):
      self.toggled = not self.toggled

      if self.toggled:
        self.section.background = self.toggledBackground
      else:
        self.section.background = self.defaultBackground

      if self.onClick:
        self.onClick(self.toggled)

  def updateDim(self):
    self.section.updateDim()

    newX, newY = self.section.x - self.border, self.section.y - self.border
    newWidth, newHeight = self.section.width + (self.border * 2), self.section.height + (self.border * 2)

    self.borderRect.update(newX, newY, newWidth, newHeight)

  def draw(self, surface):
    if self.border > 0:
      if self.toggled:
        pg.draw.rect(surface, self.borderColorToggled, self.borderRect)
      else:
        pg.draw.rect(surface, self.borderColor, self.borderRect)

    self.section.draw(surface)

