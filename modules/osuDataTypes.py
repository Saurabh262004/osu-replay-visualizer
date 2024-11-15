from struct import unpack as up
from datetime import datetime, timedelta
from lzma import decompress as dcmp

TICKS_PER_SECOND = 10**7
TICKS_EPOCH_START = datetime(1, 1, 1)
WINDOWS_EPOCH_START = datetime(1601, 1, 1)

def byte(file):
  return up('<B', file.read(1))[0]

def short(file):
  return up('<h', file.read(2))[0]

def integer(file):
  return up('<i', file.read(4))[0]

def long(file):
  return up('<q', file.read(8))[0]

def ULEB128(file):
  result = 0
  shift = 0

  while True:
    byte_value = file.read(1)[0]
    result |= (byte_value & 0x7F) << shift

    if (byte_value & 0x80) == 0:
      break

    shift += 7

  return result

def single(file):
  return up('<f', file.read(4))[0]

def double(file):
  return up('<d', file.read(8))[0]

def boolean(file):
  if (file.read(1) == b'\x00'):
    return False
  return True

def string(file):
  extractedSTR = ''
  if file.read(1) == b'\x0b':
    stringLength = ULEB128(file)

    extractedSTR += file.read(stringLength).decode('utf-8')

  return extractedSTR

def singleIntDoublePair(file):
  pair = []

  # intFlag
  byte(file)
  pair.append(integer(file))

  # doubleFlag
  byte(file)
  pair.append(double(file))

  return pair

def IntDoublePairs(file):
  totalPairs = integer(file)
  pairs = []

  pairs.extend([singleIntDoublePair(file) for _ in range(totalPairs)])

  return pairs

def singleTimingPoint(file):
  point = {
    'bpm' : double(file),
    'offset' : double(file),
    'inherited' : not boolean(file)
  }
  
  if point['inherited']:
    point['inverseSliderVelocityMultiplier'] = point.pop('bpm')

  return point

def timingPoints(file):
  totalTimingPoints = integer(file)
  points = []

  points.extend([singleTimingPoint(file) for _ in range(totalTimingPoints)])

  return points

def dateTime(file):
  ticks = long(file)

  date_time = TICKS_EPOCH_START + timedelta(seconds=(ticks/TICKS_PER_SECOND))

  return date_time.strftime("%Y-%m-%d %H:%M:%S.%f") # this might change to the similar format of windowsDateTime

# !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!! NOT WORKING CORRECTLY !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!! #
def windowsDateTime(file):
  ticks = long(file)

  date_time = WINDOWS_EPOCH_START + timedelta(seconds=(ticks/TICKS_PER_SECOND))

  return date_time.strftime("%m-%d-%y %H:%M:%S")
