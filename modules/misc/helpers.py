from typing import Union

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

# finds a value in array and return the index of the found value else returns `False`
def find(value, arr: Union[list, tuple]) -> int:
  index = 0

  for item in arr:
    if item == value:
      return index
    index += 1

  return -1
