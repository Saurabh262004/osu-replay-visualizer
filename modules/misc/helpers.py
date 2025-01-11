from typing import Union, Iterable
from pygame import Surface, transform

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
  return end1 + (num - start1) * (end2 - end1) / (start2 - start1)

# check if all the values are in an iterable if yes return True else return False
def allIn(values: Iterable, itr: Iterable) -> bool:
  for v in values:
    if not v in itr:
      return False
  return True

# finds a value in array and return the index of the found value else returns `False`
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
def squish(image: Surface, containerSize: Iterable) -> Surface:
  return transform.scale(image, containerSize)

# resizes the image to the smallest possible fit while preserving the original aspect ratio
def fit(image: Surface, containerSize: Iterable) -> Surface:
  containerWidth, containerHeight = containerSize
  imageWidth, imageHeight = image.get_width(), image.get_height()

  imageResRatio = imageWidth / imageHeight

  if containerWidth < containerHeight:
    newWidth = containerWidth
    newHeight = imageResRatio * newWidth
    return transform.scale(image, (newWidth, newHeight))

  newHeight = containerHeight
  newWidth = imageResRatio * newHeight
  return transform.scale(image, (newWidth, newHeight))

# resizes the image to the largest possible fit while preserving the original aspect ratio
def fit(image: Surface, containerSize: Iterable) -> Surface:
  containerWidth, containerHeight = containerSize
  imageWidth, imageHeight = image.get_width(), image.get_height()

  imageResRatio = imageWidth / imageHeight

  if containerWidth > containerHeight:
    newWidth = containerWidth
    newHeight = imageResRatio * newWidth
    return transform.scale(image, (newWidth, newHeight))

  newHeight = containerHeight
  newWidth = imageResRatio * newHeight
  return transform.scale(image, (newWidth, newHeight))
