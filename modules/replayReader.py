from modules.osuDataTypes import *
import json
from lzma import decompress as dcmp

def replayArray(file):
  # read the compressed LZMA byte array containing the replay data from a ".osr" file
  replayByteArrayLength = integer(file)
  LZMAbyteArray = file.read(replayByteArrayLength)

  # decompress and decodes the data in utf-8
  decodedReplayString = dcmp(LZMAbyteArray).decode('utf-8')

  replayArray = []
  actions = []
  action = ''

  # process the data and returns a python `list` object containing the replay actions
  for char in decodedReplayString:
    if char == '|':
      actions.append(action)
      action = ''
    elif char == ',':
      if (actions[0] == '-12345'):
        replayArray.append({'seed' : int(action)})
      else:
        replayArray.append({'interval' : int(actions[0]), 'x' : float(actions[1]), 'y' : float(actions[2]), 'keys' : decodeBinValue('keys', int(action))})

      action = ''
      actions = []
    else:
      action += char

  return replayArray

def getReplayData(replayURL, dumpJsonURL=None):
  # read the data from a ".osr" file and store it in a python `dict` object
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
      'mods' : decodeBinValue('mods', integer(file)),
      'lifeBar' : string(file),
      'timeStamp' : dateTime(file, 'Asia/Calcutta'),
      'replyArray' : replayArray(file),
      'onlineScoreID' : long(file)
    }

    # convert the data in json format and bump it in a file if a URL to the file is given
    if (dumpJsonURL):
      with open(dumpJsonURL, 'w') as dumpFile:
        dumpFile.write(json.dumps(replayData, indent=2))

    return replayData
