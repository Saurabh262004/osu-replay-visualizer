# maps a number from one range to another
def mapRange(x, a, b, c, d):
  return c + (x - a) * (d - c) / (b - a)

# finds a value in array and return the index of the found value else returns `False`
def find(value, arr):
  index = 0

  for item in arr:
    if item == value:
      return index
    index += 1

  return -1

