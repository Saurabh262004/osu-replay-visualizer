from typing import Union, Iterable, Optional
from pygame import Surface, transform, Color

numType = Union[int, float]

# checks if a given string can be converted to a valid floating point value
def isFloat(s: str) -> bool:
  try:
    float(s)
    return True
  except ValueError:
    return False

# try to convert a given string to a number if can't then return the same string
def tryToNum(s: str) -> Union[int, float, str]:
  if s.isdecimal():
    return int(s)

  if isFloat(s):
    return float(s)

  return s

# maps a number from one range to another
def mapRange(num: numType, start1: numType, start2: numType, end1: numType, end2: numType) -> numType:
  # return the mid-point of the end range if the start1 and start2 are the same
  if start1 == start2:
    return (end1 + end2) / 2

  return end1 + (num - start1) * (end2 - end1) / (start2 - start1)

# check if all the values are in an iterable if yes return True else return False
def allIn(values: Iterable, itr: Iterable) -> bool:
  for v in values:
    if not v in itr:
      return False
  return True

# finds a value in array and return the index of the found value else returns -1
def find(value, arr: Union[list, tuple]) -> int:
  index = 0

  for item in arr:
    if item == value:
      return index
    index += 1

  return -1

# returns a string with the leading and trailing characters removed
def customStrip(string: str, chars: Iterable):
  start = 0
  end = -1

  for i in range(len(string)):
    if not string[i] in chars:
      start = i
      break

  for i in range(len(string) - 1, start, -1):
    if not string[i] in chars:
      end = i
      break
  
  return string[start:end + 1]

# deforms the image to fit in the container
def squish(image: Surface, containerSize: Iterable, scalePercent: Optional[int] = 100) -> Surface:
  return transform.smoothscale(image, (containerSize[0] * (scalePercent / 100), containerSize[1] * (scalePercent / 100)))

# resizes the image to the smallest possible fit while preserving the original aspect ratio
def fit(image: Surface, containerSize: Iterable, scalePercent: Optional[int] = 100) -> Surface:
  containerWidth, containerHeight = containerSize
  containerWidth *= (scalePercent / 100)
  containerHeight *= (scalePercent / 100)

  imageWidth, imageHeight = image.get_width(), image.get_height()

  imageResRatio = imageWidth / imageHeight

  if containerWidth < containerHeight:
    newWidth = containerWidth
    newHeight = imageResRatio * newWidth
    return transform.smoothscale(image, (newWidth, newHeight))

  newHeight = containerHeight
  newWidth = imageResRatio * newHeight
  return transform.smoothscale(image, (newWidth, newHeight))

# resizes the image to the largest possible fit while preserving the original aspect ratio
def fill(image: Surface, containerSize: Iterable, scalePercent: Optional[int] = 100) -> Surface:
  containerWidth, containerHeight = containerSize
  containerWidth *= (scalePercent / 100)
  containerHeight *= (scalePercent / 100)
  imageWidth, imageHeight = image.get_width(), image.get_height()

  imageResRatio = imageWidth / imageHeight

  if containerWidth > containerHeight:
    newWidth = containerWidth
    newHeight = imageResRatio * newWidth
    return transform.smoothscale(image, (newWidth, newHeight))

  newHeight = containerHeight
  newWidth = imageResRatio * newHeight
  return transform.smoothscale(image, (newWidth, newHeight))

TINT_CONDITIONS = ('all', 'specific')
# changes an images rgb value based on conditions
def tintImage(image: Surface, tintColor: Color, condition: Optional[str] = 'all', conditionColor: Optional[Iterable[Color]] = None):
  image.lock()
  width, height = image.get_size()

  if not condition in TINT_CONDITIONS:
    raise ValueError(f'Tint condition must be one of the following: {TINT_CONDITIONS}')

  if condition == 'specific' and conditionColor is None:
    raise ValueError('If condition is set to specific the condition colors must be provided')

  if condition == 'all':
    for x in range(width):
      for y in range(height):
        _, _, _, a = image.get_at((x, y))
        if a > 0:
          image.set_at((x, y), (tintColor.r, tintColor.g, tintColor.b, a))
  else:
    for x in range(width):
      for y in range(height):
        r, g, b, a = image.get_at((x, y))

        if a > 0:
          for color in conditionColor:
            if color.r == r and color.g == g and color.b == b:
              image.set_at((x, y), (tintColor.r, tintColor.g, tintColor.b, a))
              break

  image.unlock()
