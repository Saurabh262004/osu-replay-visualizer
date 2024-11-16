from struct import unpack as up
from datetime import datetime, timedelta
from modules.helpers import find

TICKS_PER_SECOND = 10**7
TICKS_EPOCH_START = datetime(1, 1, 1)
WINDOWS_EPOCH_START = datetime(1601, 1, 1)
MODS = [
  'noFail',
  'easy',
  'touchDevice',
  'hidden',
  'hardRock',
  'suddenDeath',
  'doubleTime',
  'relax',
  'halfTime',
  'nightcore',
  'flashlight',
  'autoplay',
  'spunOut',
  'autopilot',
  'perfect',
  'key4',
  'key5',
  'key6',
  'key7',
  'key8',
  'fadeIn',
  'random',
  'cinema',
  'targetPractice',
  'key9',
  'coop',
  'key1',
  'key3',
  'key2',
  'scoreV2',
  'mirror'
]
MOD_PAIRS = {
  'pairs': [['doubleTime', 'nightCore'], ['key4', 'key5', 'key6', 'key7', 'key8']],
  'pairNames' : ['nightCore', 'keyMod']
}
KEYS = [
  'm1',
  'm2',
  'k1',
  'k2'
]
KEY_PAIRS = {
  'pairs': [['k1', 'm1'], ['k2', 'm2']],
  'pairNames' : ['k1', 'k2']
}

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

def decodeBinValue(type, value):
  valueBin = bin(value)[2:]
  decoded = []
  lenValueBin = len(valueBin)
  
  if (type == 'mods'):
    tabel = MODS
    pairsTabel = MOD_PAIRS
  elif (type == 'keys'):
    tabel = KEYS
    pairsTabel = KEY_PAIRS

  for i in range(lenValueBin):
    if (valueBin[(lenValueBin - i) - 1] == '1'):
      decoded.append(tabel[i])

  pairIndex = -1
  foundPairIndexes = []
  for pair in pairsTabel['pairs']:
    pairIndex += 1
    foundPair = -1

    for value in pair:
      foundPair = find(value, decoded)
      if foundPair == -1:
        break

    if not foundPair == -1:
      foundPairIndexes.append(pairIndex)

  for index in foundPairIndexes:
    for value in pairsTabel['pairs'][index]:
      if value in decoded:
        decoded.remove(value)
    decoded.append(pairsTabel['pairNames'][index])

  return decoded
