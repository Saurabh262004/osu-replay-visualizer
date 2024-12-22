# a module that helps render stuff on screen with pygame
# reusing code is not something I know
import pygame as pg
from modules.misc.helpers import mapRange, allIn
from typing import Union, Optional, Callable, Dict, Iterable

numType = Union[int, float]
containerType = Union['Section', pg.Rect]
backgroundType = Union[pg.Color, pg.Surface]
elementType = Union['Section', 'Circle', 'Button', 'Toggle', 'RangeSlider']

ALLOWED_DIMENSIONS_KEYVALS = (
  ('x', 'y', 'w', 'h'),
  ('x', 'y', 'r'),
  ('type', 'value'),
  ('a', 'r')
)

class Section:
  def __init__(self, dimensions: Dict[str, Dict[str, Union[str, int, float]]], background: backgroundType, container: Optional[containerType] = None):
    self.dimensions = dimensions
    self.background = background
    self.container = container
    self.rect = pg.Rect(0, 0, 0, 0)

    if not self.__validDims():
      print('invalid dimension object')
      return None

    if self.container == None:
      dim = self.dimensions
      for d in dim:
        if not dim[d]['type'] == 'a':
          dim[d]['type'] = 'a'

    self.update()

  def update(self):
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
      surface.blit(self.background, self.rect)
    elif isinstance(self.background, pg.Color):
      pg.draw.rect(surface, self.background, self.rect)

  def __getRel(self, typ: str):
    if typ == 'x':
      return self.container.x
    if typ == 'y':
      return self.container.y
    if typ == 'w':
      return self.container.width
    if typ == 'h':
      return self.container.height

  def __getPadding(self, key: str):
    if key == 'x':
      return self.container.x
    if key == 'y':
      return self.container.y
    return 0

  def __validDims(self):
    dim = self.dimensions
    if (set(self.dimensions.keys()) == set(ALLOWED_DIMENSIONS_KEYVALS[0])):
      for d in dim:
        if ((set(dim[d].keys()) == set(ALLOWED_DIMENSIONS_KEYVALS[2])) and (dim[d]['type'][0] in ALLOWED_DIMENSIONS_KEYVALS[3])):
          if dim[d]['type'][0] == 'r':
            if (len(dim[d]['type']) == 2) and dim[d]['type'][1] in ALLOWED_DIMENSIONS_KEYVALS[0]:
              return True
            else: break
          return True
        else: break
    return False

  @staticmethod
  def createDimObject(arr: Iterable):
    return {
      'x': {'type': arr[0], 'value': arr[1]},
      'y': {'type': arr[2], 'value': arr[3]},
      'w': {'type': arr[4], 'value': arr[5]},
      'h': {'type': arr[6], 'value': arr[7]}
    }

class Circle:
  def __init__(self, dimensions: Dict[str, Dict[str, Union[str, int, float]]], background: backgroundType, container: Optional[containerType] = None):
    self.dimensions = dimensions
    self.background = background
    self.container = container

    if not self.__validDims():
      print('invalid dimension object')
      return None

    if self.container == None:
      dim = self.dimensions
      for d in dim:
        if not dim[d]['type'] == 'a':
          dim[d]['type'] = 'a'

    self.update()

  def update(self):
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
    self.radius = self.dimensions['r']['calcVal']

  def draw(self, surface: pg.Surface):
    if isinstance(self.background, pg.Surface):
      surface.blit(self.background, (self.x, self.y))
    elif isinstance(self.background, pg.Color):
      pg.draw.circle(surface, self.background, (self.x, self.y), self.radius)

  def __getRel(self, typ: str):
    if typ == 'x':
      return self.container.x
    if typ == 'y':
      return self.container.y
    if typ == 'w':
      return self.container.width
    if typ == 'h':
      return self.container.height

  def __getPadding(self, key: str):
    if key == 'x':
      return self.container.x
    if key == 'y':
      return self.container.y
    return 0

  def __validDims(self):
    dim = self.dimensions
    if (set(self.dimensions.keys()) == set(ALLOWED_DIMENSIONS_KEYVALS[1])):
      for d in dim:
        if ((set(dim[d].keys()) == set(ALLOWED_DIMENSIONS_KEYVALS[2])) and (dim[d]['type'][0] in ALLOWED_DIMENSIONS_KEYVALS[3])):
          if dim[d]['type'][0] == 'r':
            if (len(dim[d]['type']) == 2) and dim[d]['type'][1] in ALLOWED_DIMENSIONS_KEYVALS[0]:
              return True
            else: break
          return True
        else: break
    return False

  @staticmethod
  def createDimObject(arr: Iterable):
    return {
      'x': {'type': arr[0], 'value': arr[1]},
      'y': {'type': arr[2], 'value': arr[3]},
      'r': {'type': arr[4], 'value': arr[5]}
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

    self.update()

  def checkEvent(self, event: pg.event.Event) -> bool:
    if event.type == pg.MOUSEBUTTONDOWN and event.button == 1 and self.section.rect.collidepoint(event.pos):
      self.pressed = True
      self.section.background = self.pressedBackground

      if self.onClick:
        self.onClick()

      return True
    elif event.type == pg.MOUSEBUTTONUP and self.pressed:
      self.pressed = False
      self.section.background = self.defaultBackground

      return True
    return False

  def update(self):
    if not isinstance(self.section, pg.Rect):
      self.section.update()

    newX, newY = self.section.x - self.border, self.section.y - self.border
    newWidth, newHeight = self.section.width + (self.border * 2), self.section.height + (self.border * 2)

    self.borderRect.update(newX, newY, newWidth, newHeight)

    self.fontSize = max(10, int(self.section.height * .6))
    self.font = pg.font.SysFont(self.fontPath, self.fontSize)

    self.textSurface = self.font.render(self.text, True, self.textColor)
    self.textRect = self.textSurface.get_rect(center = self.section.rect.center)

  def draw(self, surface: pg.Surface):
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

  def checkEvent(self, event: pg.event.Event) -> bool:
    if event.type == pg.MOUSEBUTTONDOWN and event.button == 1 and self.section.rect.collidepoint(event.pos):
      self.toggled = not self.toggled

      if self.toggled:
        self.section.background = self.toggledBackground
      else:
        self.section.background = self.defaultBackground

      if self.onClick:
        self.onClick(self.toggled)

      return True
    return False

  def update(self):
    self.section.update()

    newX, newY = self.section.x - self.border, self.section.y - self.border
    newWidth, newHeight = self.section.width + (self.border * 2), self.section.height + (self.border * 2)

    self.borderRect.update(newX, newY, newWidth, newHeight)

  def draw(self, surface: pg.Surface):
    if self.border > 0:
      if self.toggled:
        pg.draw.rect(surface, self.borderColorToggled, self.borderRect)
      else:
        pg.draw.rect(surface, self.borderColor, self.borderRect)

    self.section.draw(surface)

class RangeSlider:
  def __init__(self, section: containerType, sliderRange: Iterable, emptySliderColor: pg.Color, fullSliderColor: pg.color, dragCircleRadius: numType, dragCircleColor: pg.color):
    self.section = section
    self.sliderRange = sliderRange
    self.sliderValue = 0
    self.rangeLength = abs(self.sliderRange[0] - self.sliderRange[1])
    self.fullLengthSliderColor = emptySliderColor
    self.filledSliderColor = fullSliderColor
    self.dragCircleRadius = dragCircleRadius
    self.dragCircleColor = dragCircleColor
    self.dragPosition = self.section.x
    self.pressed = False

    self.oldDim = {
      'x': 0,
      'y': 0,
      'w': 0,
      'h': 0
    }

    self.fullLengthSlider = Section(
      Section.createDimObject(('rx', 0, 'ry', 0, 'rw', 1, 'a', 8)),
      self.fullLengthSliderColor,
      self.section
    )

    self.filledSlider = pg.Rect(self.section.x, self.section.y,  self.dragPosition - self.section.x, 8)

    self.dragCircle = Circle(
      Circle.createDimObject(('rw', 1, 'rh', .5, 'a', self.dragCircleRadius)),
      self.dragCircleColor,
      self.filledSlider
    )

  def update(self):
    self.oldDim = {
      'x': self.section.x,
      'y': self.section.y,
      'w': self.section.width,
      'h': self.section.height
    }

    if not isinstance(self.section, pg.Rect):
      self.section.update()

    self.fullLengthSlider.update()

    self.dragPosition = mapRange(self.dragPosition, self.oldDim['x'], self.oldDim['x'] + self.oldDim['w'], self.section.x, self.section.x + self.section.width)

    self.filledSlider.update(self.section.x, self.section.y, self.dragPosition - self.section.x, 8)

    self.dragCircle.update()

    self.value = mapRange(self.dragPosition, self.section.x, self.section.x + self.section.width, self.sliderRange[0], self.sliderRange[1])

  def draw(self, surface: pg.Surface):
    self.section.draw(surface)
    self.fullLengthSlider.draw(surface)
    pg.draw.rect(surface, self.filledSliderColor, self.filledSlider)
    self.dragCircle.draw(surface)

  def checkEvent(self, event: pg.event.Event) -> bool:
    if event.type == pg.MOUSEBUTTONDOWN and event.button == 1 and self.fullLengthSlider.rect.collidepoint(event.pos):
      self.dragPosition = event.pos[0]
      self.pressed = True
      self.update()
      return True
    elif event.type == pg.MOUSEBUTTONUP:
      self.pressed = False
    return False

  def drag(self, mouseX: numType):
    if (self.pressed) and (mouseX >= self.section.x) and (mouseX <= (self.section.x + self.section.width)):
      self.dragPosition = mouseX
      self.update()

class System:
  def __init__(self, surface: pg.Surface):
    self.surface = surface
    self.elements: Dict[str, elementType] = {}
    self.sections: Dict[str, Section] = {}
    self.circles: Dict[str, Circle] = {}
    self.buttons: Dict[str, Button] = {}
    self.toggles: Dict[str, Toggle] = {}
    self.rangeSliders: Dict[str, RangeSlider] = {}

  def addElement(self, element: elementType, elementID: str) -> bool:
    if elementID in self.elements:
      print(f'An element with id: {elementID} already exists, please enter a unique id.')
      return False

    self.elements[elementID] = element

    if isinstance(element, Section):
      self.sections[id] = element
    elif isinstance(element, Circle):
      self.circles[id] = element
    elif isinstance(element, Button):
      self.buttons[id] = element
    elif isinstance(element, Toggle):
      self.toggles[id] = element
    elif isinstance(element, RangeSlider):
      self.rangeSliders[id] = element

    return True

  def __validateIDs(self, elementIDs: Optional[Iterable] = None) -> Union[Iterable, None, dict]:
    if elementIDs == None:
      return self.elements

    if not allIn(elementIDs, self.elements):
      print('The given iterable contains id(s) that do not exist in this system, please enter a valid iterable')
      return None

    return elementIDs

  def draw(self, elementIDs: Optional[Iterable] = None):
    idList = self.__validateIDs(elementIDs)

    if not idList == None:
      for elementID in idList:
        self.elements[elementID].draw(self.surface)

  def update(self, elementIDs: Optional[Iterable] = None):
    idList = self.__validateIDs(elementIDs)
    # print(idList)

    if not idList == None:
      for elementID in idList:
        self.elements[elementID].update()
        # print(elementID)

  def handleEvents(self, event: pg.event.Event, mouseX: numType):
    for buttonID in self.buttons:
      self.buttons[buttonID].checkEvent(event)

    for toggleID in self.toggles:
      self.toggles[toggleID].checkEvent(event)

    for rangeSliderID in self.rangeSliders:
      self.rangeSliders[rangeSliderID].checkEvent(event)
      self.rangeSliders[rangeSliderID].drag(mouseX)
