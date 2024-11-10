from osuDataTypes import *
import json

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
      'replyArray' : replayArray(file),
      'onlineScoreID' : long(file)
    }

    if (dumpJsonURL):
      with open(dumpJsonURL, 'w') as dumpFile:
        dumpFile.write(json.dumps(replayData))

    return replayData

getReplayData('Ultraviolet_2643867_4702446541.osr', 'replayData.json')