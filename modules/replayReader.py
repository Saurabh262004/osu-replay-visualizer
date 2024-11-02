from lzma import decompress as dcmp
from struct import unpack as up
import json

def byte(file):
  return up('B', file.read(1))[0]

def short(file):
  return up('h', file.read(2))[0]

def integer(file):
  return up('i', file.read(4))[0]

def long(file):
  return up('q', file.read(8))[0]

def ULEB128(file):
  result = 0
  shift = 0

  while True:
    byte = file.read(1)
    byte_value = ord(byte)
    result |= (byte_value & 0x7F) << shift

    if (byte_value & 0x80) == 0:
      break

    shift += 7

  return result

def string(file):
  extractedSTR = ''
  if file.read(1) == b'\x0b':
    stringLength = ULEB128(file)

    extractedSTR += file.read(stringLength).decode('utf-8')

  return extractedSTR

def getReplayArray(string):
  array = []
  actions = []
  action = ''

  for char in string:
    if char == '|':
      actions.append(action)
      action = ''
    elif char == ',':
      array.append({'w' : int(actions[0]), 'x' : float(actions[1]), 'y' : float(actions[2]), 'z' : int(action)})
      action = ''
      actions = []
    else:
      action += char

  return array

def getReplayData(replayURL, dumpJsonURL=None):
  with open(replayURL, 'rb') as file:
    replayData = {
      'type' : byte(file),
      'clientVer' : integer(file),
      'beatmapMD5Hash' : string(file),
      'playerName' : string(file),
      'replayMD5Hash' : string(file),
      '300' : short(file),
      '100' : short(file),
      '50' : short(file),
      'geki' : short(file),
      'katu' : short(file),
      'miss' : short(file),
      'score' : integer(file),
      'combo' : short(file),
      'pfc' : byte(file),
      'mods' : integer(file),
      'lifeBar' : string(file),
      'timeStamp' : long(file),
      'replayDataByteArrayLength' : integer(file)
    }

    LZMAbyteArray = file.read(replayData['replayDataByteArrayLength'])
    decodedReplayString = dcmp(LZMAbyteArray).decode('ascii')
    # replayData['replayArray'] = decodedReplayString
    replayData['replayArray'] = getReplayArray(decodedReplayString)
    replayData['onlineScoreID'] = long(file)
  
    if (dumpJsonURL):
      with open(dumpJsonURL, 'w') as dumpFile:
        dumpFile.write(json.dumps(replayData))

    return replayData

getReplayData('Ultraviolet_2643867_4702446541.osr', 'replayData.json')