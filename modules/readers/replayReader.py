from modules.readers.osuDataTypes import *
from json import dumps
from lzma import decompress
from modules.misc.gameLists import MODS_ABRV, KEYS
from modules.readers.parsingHelpers import separateByComma

def replayArray(file):
  # read the compressed LZMA byte array containing the replay data from a ".osr" file
  replayByteArrayLength = integer(file)
  LZMAbyteArray = file.read(replayByteArrayLength)

  # decompress and decodes the data in utf-8
  decodedReplayString = decompress(LZMAbyteArray).decode('utf-8')

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
        replayArray.append({
          'interval' : int(actions[0]),
          'x' : float(actions[1]),
          'y' : float(actions[2]),
          'keys' : decodeBinValue(int(action), KEYS)
        })

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
      'mods' : decodeBinValue(integer(file), MODS_ABRV),
      'lifeBar' : separateByComma(string(file)),
      'timeStamp' : dateTime(file),
      'replayArray' : replayArray(file),
      'onlineScoreID' : long(file)
    }

    # convert the data in json format and bump it in a file if a URL to the file is given
    if dumpJsonURL:
      with open(dumpJsonURL, 'w') as dumpFile:
        dumpFile.write(dumps(replayData, indent=2))

    return replayData
