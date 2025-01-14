# a module that helps render stuff on screen with pygame
# reusing code is not something I know
from math import sqrt
import pygame as pg
from modules.misc.helpers import mapRange, allIn, squish, fit, fill
from typing import Union, Optional, Callable, Dict, Iterable, Any

numType = Union[int, float]
containerType = Union['Section', pg.Rect]
backgroundType = Union[pg.Color, pg.Surface]
elementType = Union['Section', 'Circle', 'Button', 'Toggle', 'RangeSliderHorizontal', 'RangeSliderVertical']

VALID_SIZE_TYPES = ('fit', 'fill', 'squish')
DIMENSION_REFERENCE_TYPES = ('number', 'percent', 'dictNum', 'classNum', 'dictPer', 'classPer', 'customCallable')

class DynamicValue:
  def __init__(self, referenceType: str, reference: Union[Callable, numType, Dict[str, numType], object], callableParameters: Optional[Any] = None, dictKey: Optional[str] = None, classAttr: Optional[str] = None, percent: Optional[numType] = None):
    self.referenceType = referenceType
    self.reference = reference
    self.callableParameters = callableParameters
    self.dictKey = dictKey
    self.classAttr = classAttr
    self.percent = percent
    self.value = None

    if not self.referenceType in DIMENSION_REFERENCE_TYPES:
      raise ValueError(f'Invalid dimType value received, value must be one of the following: {DIMENSION_REFERENCE_TYPES}')

    if (self.referenceType == 'customCallable') and not callable(self.reference):
      raise ValueError('If referenceType is custumCallable then reference must be callable')

    if (self.referenceType == 'dictNum' or self.referenceType == 'dictPer') and not (isinstance(self.reference, dict)):
      raise ValueError('If referenceType is dictNum or dictPer then given reference must be a dict object')

    if (self.referenceType == 'dictNum' or self.referenceType == 'dictPer') and (self.dictKey is None):
      raise ValueError('If referenceType is dictNum or dictPer then dictKey must be defined')

    if (self.referenceType == 'classNum' or self.referenceType == 'classPer') and not (isinstance(self.reference, object)):
      raise ValueError('If referenceType is classNum or classPer then given reference must be an object')

    if (self.referenceType == 'classNum' or self.referenceType == 'classPer') and (self.classAttr is None):
      raise ValueError('If referenceType is classNum or classPer then classAttr must be defined')

    if (self.referenceType == 'percent' or self.referenceType == 'dictPer' or self.referenceType == 'classPer') and (self.percent is None):
      raise ValueError('If referenceType is percent, dictPer or classPer percent must be defined')

    self.resolveValue()

  def resolveValue(self):
    if self.referenceType == 'number':
      self.value = self.reference
    elif self.referenceType == 'percent':
      self.value = self.reference * (self.percent / 100)
    elif self.referenceType == 'customCallable':
      if not self.callableParameters is None:
        self.value = self.reference(self.callableParameters)
      else:
        self.value = self.reference()
    elif self.referenceType == 'dictNum':
      self.value = self.reference[self.dictKey]
    elif self.referenceType == 'dictPer':
      self.value = self.reference[self.dictKey] * (self.percent / 100)
    elif self.referenceType == 'classNum':
      self.value = getattr(self.reference, self.classAttr, 0)
    elif self.referenceType == 'classPer':
      self.value = getattr(self.reference, self.classAttr, 0) * (self.percent / 100)

class Section:
  def __init__(self, dimensions: Dict['str', DynamicValue], background: backgroundType, borderRadius: Optional[numType] = 0, backgroundSizeType: Optional[str] = 'fit', backgroundSizePercent: Optional[int] = 100):
    self.dimensions = dimensions
    self.background = background
    self.drawImage = None
    self.rect = pg.Rect(0, 0, 0, 0)
    self.borderRadius = borderRadius
    self.backgroundSizeType = backgroundSizeType
    self.backgroundSizePercent = backgroundSizePercent
    self.active = True

    if len(self.dimensions) != 4:
      raise ValueError(f'dimensions must contain 4 Dimension objects, received: {len(self.dimensions)}')

    if not allIn(('x', 'y', 'width', 'height'), self.dimensions):
      raise ValueError('dimensions must contain all of the following keys: \'x\', \'y\', \'width\' \'height\'')

    if not self.backgroundSizeType in VALID_SIZE_TYPES:
      raise ValueError(f'Invalid \"backgroundSizeType\" value, must be one of the following values: {VALID_SIZE_TYPES}')

    self.x = self.dimensions['x'].value
    self.y = self.dimensions['y'].value
    self.width = self.dimensions['width'].value
    self.height = self.dimensions['height'].value

    self.update()

  def update(self):
    if not self.active:
      return None

    # This is really not ideal but I don't know what else I can do
    unstable = True
    totalIterations = 0
    maxIterations = len(self.dimensions)
    while unstable:
      if totalIterations > maxIterations:
        raise ValueError('Provided dimensions are referencing each other in a cyclic pattern, please provide valid dimenisons')

      for dim in self.dimensions:
        self.dimensions[dim].resolveValue()

      if (
        self.x == self.dimensions['x'].value and
        self.y == self.dimensions['y'].value and
        self.width == self.dimensions['width'].value and
        self.height == self.dimensions['height'].value
        ): unstable = False
      else:
        totalIterations += 1

      self.x = self.dimensions['x'].value
      self.y = self.dimensions['y'].value
      self.width = self.dimensions['width'].value
      self.height = self.dimensions['height'].value

    self.rect.update(self.x, self.y, self.width, self.height)

    if isinstance(self.background, pg.Surface):
      if self.backgroundSizeType == 'fit':
        self.drawImage = fit(self.background, (self.width, self.height), self.backgroundSizePercent)
      elif self.backgroundSizeType == 'fill':
        self.drawImage = fill(self.background, (self.width, self.height), self.backgroundSizePercent)
      else:
        self.drawImage = squish(self.background, (self.width, self.height), self.backgroundSizePercent)

      self.imageX = self.x + ((self.width - self.drawImage.get_width()) / 2)
      self.imageY = self.y + ((self.height - self.drawImage.get_height()) / 2)

  def draw(self, surface: pg.Surface):
    if not self.active:
      return None

    if isinstance(self.background, pg.Surface):
      surface.blit(self.drawImage, (self.imageX, self.imageY))
    elif isinstance(self.background, pg.Color):
      pg.draw.rect(surface, self.background, self.rect, border_radius = self.borderRadius)

class Circle:
  def __init__(self, dimensions: Dict[str, DynamicValue], background: backgroundType, backgroundSizeType: Optional[str] = 'fit'):
    self.dimensions = dimensions
    self.background = background
    self.drawImage = None
    self.backgroundSizeType = backgroundSizeType
    self.sqrt2 = sqrt(2)
    self.active = True

    if len(self.dimensions) != 3:
      raise ValueError(f'dimensions must contain 4 Dimension objects, received: {len(self.dimensions)}')

    if not allIn(('x', 'y', 'radius'), self.dimensions):
      raise ValueError('dimensions must contain all of the following keys: \'x\', \'y\', \'radius\'')

    if not self.backgroundSizeType in VALID_SIZE_TYPES:
      raise ValueError(f'Invalid \"backgroundSizeType\" value, must be one of the following values: {VALID_SIZE_TYPES}')

    self.x = self.dimensions['x'].value
    self.y = self.dimensions['y'].value
    self.radius = self.dimensions['radius'].value

    self.update()

  def update(self):
    if not self.active:
      return None
    
    # Same as before... not ideal but I don't know what else I can do
    unstable = True
    totalIterations = 0
    maxIterations = len(self.dimensions)
    while unstable:
      if totalIterations > maxIterations:
        raise ValueError('Provided dimensions are referencing each other in a cyclic pattern, please provide valid dimenisons')

      for dim in self.dimensions:
        self.dimensions[dim].resolveValue()

      if (
        self.x == self.dimensions['x'].value and
        self.y == self.dimensions['y'].value and
        self.radius == self.dimensions['radius'].value
        ): unstable = False
      else:
        totalIterations += 1

      self.x = self.dimensions['x'].value
      self.y = self.dimensions['y'].value
      self.radius = self.dimensions['radius'].value

    if isinstance(self.background, pg.Surface):
      if self.backgroundSizeType == 'fit':
        self.drawImage = fit(self.background, (self.radius * self.sqrt2, self.radius * self.sqrt2))
      elif self.backgroundSizeType == 'fill':
        self.drawImage = fill(self.background, (self.radius * 2, self.radius * 2))
      else:
        self.drawImage = squish(self.background, (self.radius * 2, self.radius * 2))

  def draw(self, surface: pg.Surface):
    if not self.active:
      return None

    if isinstance(self.background, pg.Surface):
      surface.blit(self.drawImage, (self.x - (self.drawImage.get_width() / 2), self.y - (self.drawImage.get_height() / 2)))
    elif isinstance(self.background, pg.Color):
      pg.draw.circle(surface, self.background, (self.x, self.y), self.radius)

class TextBox:
  def __init__(self, section: Section, text: str, fontPath: str, textColor: pg.Color, drawSectionDefault: Optional[bool] = False):
    self.section = section
    self.text = text
    self.fontPath = fontPath
    self.textColor = textColor
    self.drawSectionDefault = drawSectionDefault
    self.active = True

  def update(self):
    if not self.active:
      return None

    self.section.update()

    self.fontSize = max(10, int(self.section.height * .6))
    self.font = pg.font.SysFont(self.fontPath, self.fontSize)

    self.textSurface = self.font.render(self.text, True, self.textColor)
    self.textRect = self.textSurface.get_rect(center = self.section.rect.center)

  def draw(self, surface: pg.Surface, drawSection: Optional[bool] = None):
    if not self.active:
      return None

    if (drawSection is None and self.drawSectionDefault) or drawSection:
      self.section.draw(surface)

    surface.blit(self.textSurface, self.textRect)

class Button:
  def __init__(self, section: Section, pressedBackground: Optional[backgroundType] = None, borderColor: Optional[pg.Color] = None, borderColorPressed: Optional[pg.Color] = None, text: Optional[str] = None, fontPath: Optional[str] = None, textColor: Optional[pg.Color] = None, onClick: Optional[Callable] = None, onClickParams = None, border: Optional[int] = 0, onClickActuation: Optional[str] = 'buttonDown'):
    self.section = section
    self.onClick = onClick
    self.onClickParams = onClickParams
    self.onClickActuation = onClickActuation
    self.border = border
    self.pressed = False
    self.defaultBackground = section.background
    self.pressedBackground = pressedBackground
    self.borderColor = borderColor
    self.borderColorPressed = borderColorPressed
    self.active = True

    if self.border > 0:
      self.borderRect = pg.Rect(section.x - border, section.y - border, section.width + (border * 2), section.height + (border * 2))

    if text:
      self.textBox = TextBox(section, text, fontPath, textColor, False)
      self.hasText = True
    else:
      self.hasText = False

    if not onClickActuation in ('buttonDown', 'buttonUp'):
      raise ValueError('onClickActuation must be either \'buttonDown\' or \'buttonUp\'')

    self.update()

  def checkEvent(self, event: pg.event.Event) -> bool:
    if not self.active:
      return None

    if event.type == pg.MOUSEBUTTONDOWN and event.button == 1 and self.section.rect.collidepoint(event.pos):
      self.pressed = True

      if self.pressedBackground:
        self.section.background = self.pressedBackground
        self.section.update()

      if self.onClick and self.onClickActuation == 'buttonDown':
        self.onClick(self.onClickParams)

      return True
    elif event.type == pg.MOUSEBUTTONUP and self.pressed:
      self.pressed = False
      self.section.background = self.defaultBackground

      if self.onClick and self.onClickActuation == 'buttonUp':
        self.onClick(self.onClickParams)
      
      self.section.update()

      return True
    return False

  def update(self):
    if not self.active:
      return None

    if not isinstance(self.section, pg.Rect):
      if self.hasText:
        self.textBox.update()
      else:
        self.section.update()

    newX, newY = self.section.x - self.border, self.section.y - self.border
    newWidth, newHeight = self.section.width + (self.border * 2), self.section.height + (self.border * 2)

    if self.border > 0:
      self.borderRect.update(newX, newY, newWidth, newHeight)

  def draw(self, surface: pg.Surface):
    if not self.active:
      return None

    if self.border > 0:
      if self.pressed:
        pg.draw.rect(surface, self.borderColorPressed, self.borderRect, border_radius = self.section.borderRadius)
      else:
        pg.draw.rect(surface, self.borderColor, self.borderRect, border_radius = self.section.borderRadius)

    self.section.draw(surface)

    if self.hasText:
      self.textBox.draw(surface)

class Toggle:
  def __init__(self, section: Section, indicatorColor: pg.Color, borderColor: pg.Color, borderColorToggled: pg.Color, onClick: Optional[Callable] = None, onClickParams = None, sendStateInfoOnClick: Optional[bool] = False, border: int = 0):
    self.section = section
    self.onClick = onClick
    self.sendStateInfoOnClick = sendStateInfoOnClick
    self.onClickParams = onClickParams
    self.border = border
    self.toggled = False
    self.defaultBackground = section.background
    self.toggledBackground = indicatorColor
    self.borderColor = borderColor
    self.borderColorToggled = borderColorToggled
    self.innerBox = pg.Rect(self.section.x + 4, self.section.y + 4, (self.section.width / 2) - 4, self.section.height - 8)
    self.borderRect = pg.Rect(self.section.x - border, self.section.y - border, self.section.width + (border * 2), self.section.height + (border * 2))
    self.active = True

  def checkEvent(self, event: pg.event.Event) -> bool:
    if not self.active:
      return None

    if event.type == pg.MOUSEBUTTONDOWN and event.button == 1 and self.section.rect.collidepoint(event.pos):
      self.toggled = not self.toggled

      if self.toggled:
        self.section.background = self.toggledBackground
        self.innerBox.update(self.section.x + (self.section.width / 2), self.innerBox.y, self.innerBox.width, self.innerBox.height)
      else:
        self.section.background = self.defaultBackground
        self.innerBox.update(self.section.x + 4, self.section.y + 4, self.innerBox.width, self.innerBox.height)

      if self.onClick:
        if self.sendStateInfoOnClick:
          self.onClick(self.onClickParams, self.toggled)
        else:
          self.onClick(self.onClickParams)

      return True
    return False

  def update(self):
    if not self.active:
      return None

    self.section.update()

    newBorderX, newBorderY = self.section.x - self.border, self.section.y - self.border
    newBorderWidth, newBorderHeight = self.section.width + (self.border * 2), self.section.height + (self.border * 2)

    newInnerX, newInnerY = self.section.x + 4, self.section.y + 4
    if self.toggled:
      newInnerX = self.section.x + (self.section.width / 2)

    newInnerWidth, newInnerHeight = (self.section.width / 2) - 4, self.section.height - 8

    self.borderRect.update(newBorderX, newBorderY, newBorderWidth, newBorderHeight)
    self.innerBox.update(newInnerX, newInnerY, newInnerWidth, newInnerHeight)

  def draw(self, surface: pg.Surface):
    if not self.active:
      return None

    if self.border > 0:
      if self.toggled:
        pg.draw.rect(surface, self.borderColorToggled, self.borderRect, border_radius = self.section.borderRadius)
      else:
        pg.draw.rect(surface, self.borderColor, self.borderRect, border_radius = self.section.borderRadius)

    self.section.draw(surface)

    if self.toggled:
      pg.draw.rect(surface, self.defaultBackground, self.innerBox, border_radius = self.section.borderRadius)
    else:
      pg.draw.rect(surface, self.toggledBackground, self.innerBox, border_radius = self.section.borderRadius)

class RangeSliderHorizontal:
  def __init__(self, section: containerType, sliderRange: Iterable, emptySliderColor: pg.Color, fullSliderColor: pg.color, dragCircleRadius: numType, dragCircleColor: pg.color, onChange: Optional[Callable] = None, onChangeParams = None, sendValueInfoOnChange: Optional[bool] = False, hoverToScroll: Optional[bool] = True, scrollSpeed: Optional[int] = 1):
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
    self.onChange = onChange
    self.onChangeParams = onChangeParams
    self.sendValueInfoOnChange = sendValueInfoOnChange
    self.hoverToScroll = hoverToScroll
    self.scrollSpeed = scrollSpeed
    self.active = True

    self.oldDim = {
      'x': 0,
      'y': 0,
      'w': 0,
      'h': 0
    }

    self.fullLengthSlider = Section(
      {
        'x': DynamicValue('classNum', self.section, classAttr='x'),
        'y': DynamicValue('classNum', self.section, classAttr='y'),
        'width': DynamicValue('classNum', self.section, classAttr='width'),
        'height': DynamicValue('number', 8)
      },
      self.fullLengthSliderColor,
      self.section.borderRadius
    )

    self.filledSlider = pg.Rect(self.section.x, self.section.y,  self.dragPosition - self.section.x, 8)

    def getSliderY(filledSlider):
      return filledSlider.y + (filledSlider.height / 2)

    self.dragCircle = Circle(
      {
        'x': DynamicValue('classNum', self.filledSlider, classAttr='width'),
        'y': DynamicValue('customCallable', getSliderY, callableParameters=self.filledSlider),
        'radius': DynamicValue('number', self.dragCircleRadius)
      },
      self.dragCircleColor
    )

  def update(self):
    if not self.active:
      return None

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
    if not self.active:
      return None

    self.section.draw(surface)
    self.fullLengthSlider.draw(surface)
    pg.draw.rect(surface, self.filledSliderColor, self.filledSlider, border_radius = self.section.borderRadius)
    self.dragCircle.draw(surface)

  def checkEvent(self, event: pg.event.Event) -> bool:
    if not self.active:
      return None

    if event.type == pg.MOUSEBUTTONDOWN and event.button == 1 and self.fullLengthSlider.rect.collidepoint(event.pos):
      self.dragPosition = event.pos[0]
      self.pressed = True
      self.update()
      return True
    elif event.type == pg.MOUSEBUTTONUP:
      if self.pressed:
        if self.onChange:
          if self.sendValueInfoOnChange:
            self.onChange(self.onChangeParams, self.value)
          else:
            self.onChange(self.onChangeParams)
        self.pressed = False
    elif event.type == pg.MOUSEWHEEL:
      scroll = False
      scrollTo = 0
      mouseX, mouseY = pg.mouse.get_pos()

      if self.hoverToScroll:
        if self.fullLengthSlider.rect.collidepoint((mouseX, mouseY)):
          scroll = True
      else:
        scroll = True

      if scroll:
        if event.x != 0:
          scrollTo = self.dragPosition + event.x * self.scrollSpeed
        elif event.y != 0:
          scrollTo = self.dragPosition + event.y * self.scrollSpeed

        if (scrollTo < self.section.x):
          scrollTo = self.section.x
        elif (scrollTo > (self.section.x + self.section.width)):
          scrollTo = (self.section.x + self.section.width)

        if self.dragPosition != scrollTo:
          self.dragPosition = scrollTo
          self.update()

          if self.onChange:
            if self.sendValueInfoOnChange:
              self.onChange(self.onChangeParams, self.value)
            else:
              self.onChange(self.onChangeParams)

          return True
    return False

  def drag(self):
    if not self.active:
      return None

    mouseX = pg.mouse.get_pos()[0]
    if (self.pressed) and (mouseX >= self.section.x) and (mouseX <= (self.section.x + self.section.width)):
      self.dragPosition = mouseX
      self.update()

class RangeSliderVertical:
  def __init__(self, section: containerType, sliderRange: Iterable, emptySliderColor: pg.Color, fullSliderColor: pg.color, dragCircleRadius: numType, dragCircleColor: pg.color, onChange: Optional[Callable] = None, onChangeParams = None, sendValueInfoOnChange: Optional[bool] = False, hoverToScroll: Optional[bool] = True, scrollSpeed: Optional[int] = 1):
    self.section = section
    self.sliderRange = sliderRange
    self.sliderValue = 0
    self.rangeLength = abs(self.sliderRange[0] - self.sliderRange[1])
    self.fullLengthSliderColor = emptySliderColor
    self.filledSliderColor = fullSliderColor
    self.dragCircleRadius = dragCircleRadius
    self.dragCircleColor = dragCircleColor
    self.dragPosition = self.section.y
    self.pressed = False
    self.onChange = onChange
    self.onChangeParams = onChangeParams
    self.sendValueInfoOnChange = sendValueInfoOnChange
    self.hoverToScroll = hoverToScroll
    self.scrollSpeed = scrollSpeed
    self.active = True

    self.oldDim = {
      'x': 0,
      'y': 0,
      'w': 0,
      'h': 0
    }

    self.fullLengthSlider = Section(
      {
        'x': DynamicValue('classNum', self.section, classAttr='x'),
        'y': DynamicValue('classNum', self.section, classAttr='y'),
        'width': DynamicValue('number', 8),
        'height': DynamicValue('classNum', self.section, classAttr='height')
      },
      self.fullLengthSliderColor,
      self.section.borderRadius
    )

    self.filledSlider = pg.Rect(self.section.x, self.section.y, 8, self.dragPosition - self.section.y)

    def getSliderX(filledSlider):
      return filledSlider.x + (filledSlider.width / 2)

    self.dragCircle = Circle(
      {
        'x': DynamicValue('customCallable', getSliderX, callableParameters=self.filledSlider),
        'y': DynamicValue('classNum', self.filledSlider, classAttr='height'),
        'radius': DynamicValue('number', self.dragCircleRadius)
      },
      self.dragCircleColor
    )

  def update(self):
    if not self.active:
      return None

    self.oldDim = {
      'x': self.section.x,
      'y': self.section.y,
      'w': self.section.width,
      'h': self.section.height
    }

    if not isinstance(self.section, pg.Rect):
      self.section.update()

    self.fullLengthSlider.update()

    self.dragPosition = mapRange(self.dragPosition, self.oldDim['y'], self.oldDim['y'] + self.oldDim['h'], self.section.y, self.section.y + self.section.height)

    self.filledSlider.update(self.section.x, self.section.y, 8, self.dragPosition - self.section.y)

    self.dragCircle.update()

    self.value = mapRange(self.dragPosition, self.section.y, self.section.y + self.section.height, self.sliderRange[0], self.sliderRange[1])

  def draw(self, surface: pg.Surface):
    if not self.active:
      return None

    self.section.draw(surface)
    self.fullLengthSlider.draw(surface)
    pg.draw.rect(surface, self.filledSliderColor, self.filledSlider, border_radius = self.section.borderRadius)
    self.dragCircle.draw(surface)

  def checkEvent(self, event: pg.event.Event) -> bool:
    if not self.active:
      return None

    if event.type == pg.MOUSEBUTTONDOWN and event.button == 1 and self.fullLengthSlider.rect.collidepoint(event.pos):
      self.dragPosition = event.pos[0]
      self.pressed = True
      self.update()
      return True
    elif event.type == pg.MOUSEBUTTONUP:
      if self.pressed:
        if self.onChange:
          if self.sendValueInfoOnChange:
            self.onChange(self.onChangeParams, self.value)
          else:
            self.onChange(self.onChangeParams)
        self.pressed = False
    elif event.type == pg.MOUSEWHEEL:
      scroll = False
      scrollTo = 0
      mouseX, mouseY = pg.mouse.get_pos()

      if self.hoverToScroll:
        if self.fullLengthSlider.rect.collidepoint((mouseX, mouseY)):
          scroll = True
      else:
        scroll = True

      if scroll:
        if event.y != 0:
          scrollTo = self.dragPosition + (event.y * self.scrollSpeed)
        elif event.x != 0:
          scrollTo = self.dragPosition + (event.x * self.scrollSpeed)

        if (scrollTo < self.section.y):
          scrollTo = self.section.y
        elif (scrollTo > (self.section.y + self.section.height)):
          scrollTo = (self.section.y + self.section.height)

        if self.dragPosition != scrollTo:
          self.dragPosition = scrollTo
          self.update()

          if self.onChange:
            if self.sendValueInfoOnChange:
              self.onChange(self.onChangeParams, self.value)
            else:
              self.onChange(self.onChangeParams)

          return True
    return False

  def drag(self):
    if not self.active:
      return None

    mouseY = pg.mouse.get_pos()[1]
    if (self.pressed) and (mouseY >= self.section.y) and (mouseY <= (self.section.y + self.section.height)):
      self.dragPosition = mouseY
      self.update()

class System:
  def __init__(self, surface: Optional[pg.Surface] = None, preLoadState: Optional[bool] = False):
    self.locked = preLoadState

    if not self.locked:
      if not surface:
        self.locked = True
        print('No surface provided, the system is locked by default.\nIt can be initiated manually by providing a surface')
      else:
        self.surface = surface

    self.elements: Dict[str, elementType] = {}
    self.sections: Dict[str, Section] = {}
    self.circles: Dict[str, Circle] = {}
    self.textBoxes: Dict[str, TextBox] = {}
    self.buttons: Dict[str, Button] = {}
    self.toggles: Dict[str, Toggle] = {}
    self.rangeSliders: Dict[str, Union[RangeSliderHorizontal, RangeSliderVertical]] = {}

  def addElement(self, element: elementType, elementID: str) -> bool:
    if elementID in self.elements:
      raise ValueError(f'An element with id: {elementID} already exists, please enter a unique id.')

    self.elements[elementID] = element

    if isinstance(element, Section):
      self.sections[elementID] = element
    elif isinstance(element, Circle):
      self.circles[elementID] = element
    elif isinstance(element, TextBox):
      self.textBoxes[elementID] = element
    elif isinstance(element, Button):
      self.buttons[elementID] = element
    elif isinstance(element, Toggle):
      self.toggles[elementID] = element
    elif isinstance(element, RangeSliderHorizontal) or isinstance(element, RangeSliderVertical):
      self.rangeSliders[elementID] = element

    return True

  def __validateIDs(self, elementIDs: Optional[Iterable] = None) -> Union[Iterable, None, dict]:
    if elementIDs == None:
      return self.elements

    if not allIn(elementIDs, self.elements):
      print('The given iterable contains id(s) that do not exist in this system, please enter a valid iterable')
      return None

    return elementIDs

  def draw(self, elementIDs: Optional[Iterable] = None):
    if self.locked:
      print('System is currently locked')
      return None
    
    idList = self.__validateIDs(elementIDs)

    if not idList == None:
      for elementID in idList:
        if self.elements[elementID].active:
          self.elements[elementID].draw(self.surface)

  def update(self, elementIDs: Optional[Iterable] = None):
    if self.locked:
      print('System is currently locked')
      return None

    idList = self.__validateIDs(elementIDs)

    if not idList == None:
      for elementID in idList:
        if self.elements[elementID].active:
          self.elements[elementID].update()

  def handleEvents(self, event: pg.event.Event):
    if self.locked:
      print('System is currently locked')
      return None

    changeCursor = False
    for buttonID in self.buttons:
      if self.buttons[buttonID].active:
        if self.buttons[buttonID].section.rect.collidepoint(pg.mouse.get_pos()):
          changeCursor = 'hand'

      self.buttons[buttonID].checkEvent(event)

    for toggleID in self.toggles:
      if self.toggles[toggleID].active:
        if self.toggles[toggleID].section.rect.collidepoint(pg.mouse.get_pos()):
          changeCursor = 'hand'

      self.toggles[toggleID].checkEvent(event)

    for rangeSliderID in self.rangeSliders:
      if self.rangeSliders[rangeSliderID].active:
        if self.rangeSliders[rangeSliderID].section.rect.collidepoint(pg.mouse.get_pos()):
          changeCursor = 'hand'

        self.rangeSliders[rangeSliderID].checkEvent(event)
        self.rangeSliders[rangeSliderID].drag()

    if changeCursor == 'hand':
      pg.mouse.set_cursor(pg.SYSTEM_CURSOR_HAND)
    else:
      pg.mouse.set_cursor(pg.SYSTEM_CURSOR_ARROW)

  def initiate(self, surface: pg.Surface):
    self.surface = surface

    self.locked = False
