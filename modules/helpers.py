def mapRange(x, a, b, c, d):
  return c + (x - a) * (d - c) / (b - a)

def find(value, arr):
  index = 0

  for item in arr:
    if item == value:
      return index
    index += 1

  return False
