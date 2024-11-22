from struct import unpack as up
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo
from modules.helpers import find
from modules.typePairsTable import RANKED_STATUS, MODS_ABRV

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

def getStarRatings(file):
  pairs = IntDoublePairs(file)

  for pair in pairs:
    pair[0] = decodeBinValue(pair[0], MODS_ABRV)

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

def dateTime(file, timezone="UTC"):
  ticks = long(file)

  dateTime = TICKS_EPOCH_START + timedelta(seconds=(ticks//TICKS_PER_SECOND))

  localizedTime = dateTime.replace(tzinfo=ZoneInfo("UTC")).astimezone(ZoneInfo(timezone))

  return localizedTime.strftime("%m/%d/%Y %I:%M:%S %p")

def windowsDateTime(file, timezone="UTC"):
  ticks = long(file)

  dateTime = WINDOWS_EPOCH_START + timedelta(seconds=(ticks//TICKS_PER_SECOND))

  localizedTime = dateTime.replace(tzinfo=ZoneInfo("UTC")).astimezone(ZoneInfo(timezone))

  return localizedTime.strftime("%m/%d/%Y %I:%M:%S %p")

def getRankedStatus(file):
  return RANKED_STATUS[byte(file)]

def decodeBinValue(value, table):
  valueBin = bin(value)[2:]
  decoded = []
  lenValueBin = len(valueBin)

  if not (('arr' in table) and ('pairs' in table) and ('pairNames' in table)):
    return None

  if not ((type(table['arr']) is list) and (type(table['pairs']) is list) and (type(table['pairNames']) is list)):
    return None

  if len(table['pairs']) != len(table['pairNames']):
    return None

  for i in range(lenValueBin):
    if (valueBin[(lenValueBin - i) - 1] == '1'):
      decoded.append(table['arr'][i])

  pairIndex = -1
  foundPairIndexes = []
  for pair in table['pairs']:
    pairIndex += 1
    foundPair = -1

    for value in pair:
      foundPair = find(value, decoded)
      if foundPair == -1:
        break

    if not foundPair == -1:
      foundPairIndexes.append(pairIndex)

  for index in foundPairIndexes:
    for value in table['pairs'][index]:
      if value in decoded:
        decoded.remove(value)
    decoded.append(table['pairNames'][index])

  return decoded
