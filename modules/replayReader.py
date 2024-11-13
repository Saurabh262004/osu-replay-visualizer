from modules.osuDataTypes import *
import json

def replayArray(file):
  replayByteArrayLength = integer(file)
  LZMAbyteArray = file.read(replayByteArrayLength)
  decodedReplayString = dcmp(LZMAbyteArray).decode('ascii')

  replayArray = []
  actions = []
  action = ''

  for char in decodedReplayString:
    if char == '|':
      actions.append(action)
      action = ''
    elif char == ',':
      replayArray.append({'w' : int(actions[0]), 'x' : float(actions[1]), 'y' : float(actions[2]), 'z' : int(action)})
      action = ''
      actions = []
    else:
      action += char

  return replayArray

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
      'timeStamp' : windowsDateTime(file),
      'replyArray' : replayArray(file),
      'onlineScoreID' : long(file)
    }

    if (dumpJsonURL):
      with open(dumpJsonURL, 'w') as dumpFile:
        dumpFile.write(json.dumps(replayData))

    return replayData
