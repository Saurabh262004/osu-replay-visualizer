from modules.readers.osuDataTypes import *
from json import dumps

def beatmap(file, clientVer):
  bm = {
    'entrySize': integer(file) if clientVer < 20191106 else None,
    'artistName' : string(file),
    'artistNameUnicode' : string(file),
    'songTitle' : string(file),
    'songTitleUnicode' : string(file),
    'creatorName' : string(file),
    'difficultyName' : string(file),
    'audioFileName' : string(file),
    'MD5Hash' : string(file),
    'osuFileName' : string(file),
    'rankedStatus' : getRankedStatus(file),
    'totalHitcircles' : short(file),
    'totalSliders' : short(file),
    'totalSpinners' : short(file),
    'lastModificationTime' : dateTime(file),
    'approachRate' : byte(file) if clientVer < 20140609 else single(file),
    'circleSize' : byte(file) if clientVer < 20140609 else single(file),
    'hpDrain' : byte(file) if clientVer < 20140609 else single(file),
    'overallDifficulty' : byte(file) if clientVer < 20140609 else single(file),
    'sliderVelocity' : double(file),
    'standartStarRatings' : getStarRatings(file, clientVer) if clientVer >= 20140609 else None,
    'taikoStarRatings' : getStarRatings(file, clientVer) if clientVer >= 20140609 else None,
    'CTBStarRatings' : getStarRatings(file, clientVer) if clientVer >= 20140609 else None,
    'maniaStarRatings' : getStarRatings(file, clientVer) if clientVer >= 20140609 else None,
    'drainTime' : integer(file) * 1000, # convert to milliseconds
    'totalTime' : integer(file),
    'previewPoint' : integer(file),
    'timingPoints' : timingPoints(file),
    'difficultyID' : integer(file),
    'beatmapID' : integer(file),
    'threadID' : integer(file),
    'standardGrade' : byte(file),
    'taikoGrade' : byte(file),
    'CTBGrade' : byte(file),
    'mainaGrade' : byte(file),
    'localOffset' : short(file),
    'stackLeniency' : single(file),
    'gameplayMode' : byte(file),
    'songSource' : string(file),
    'songTags' : string(file),
    'onlineOffset' : short(file),
    'titleFont' : string(file),
    'isUnplayed' : boolean(file),
    'lastPlayed' : long(file),
    'isosz2' : boolean(file),
    'folderName' : string(file),
    'lastCheckedAgainstOsuRepository' : long(file),
    'ignoreBeatmapSounds' : boolean(file),
    'ignoreBeatmapSkin' : boolean(file),
    'disableStoryboard' : boolean(file),
    'disableVideo' : boolean(file),
    'visualOverride' : boolean(file),
    'aShortThatWasHereBeforeVer20140609ForSomeReason' : short(file) if clientVer < 20140609 else None,
    'lastModificationTimeInt' : integer(file),
    'maniaScrollSpeed' : byte(file)
  }

  return bm

def getDataBase(dbURL, dumpJsonURL=None):
  with open(dbURL, 'rb') as dbFile:
    DB = {
      'clientVersion' : integer(dbFile),
      'SongsFolderCount' : integer(dbFile),
      'accountUnlocked' : boolean(dbFile),
      'accountUnlockDate' : dateTime(dbFile),
      'playerName' : string(dbFile),
      'totalBeatmaps' : integer(dbFile),
      'beatmaps' : []
    }

    # print('got here')

    DB['beatmaps'].extend([beatmap(dbFile, DB['clientVersion']) for _ in range(DB['totalBeatmaps'])])
    DB['userPermission'] = integer(dbFile)

    # print('probably did not get here')

    if (dumpJsonURL):
      with open(dumpJsonURL, 'w') as dumpFile:
        dumpFile.write(dumps(DB, indent=2))

    return DB

def beatmapMD5(file, clientVer):
  backtrackLen = 0

  if clientVer < 20191106:
    backtrackLen += 4
    # skip to strings
    file.seek(4, 1)

  # skip all 7 strings and add their lenghts to total backtrack length
  for _ in range(7):
    strTmp, strLen = string(file, True, True)
    backtrackLen += strLen

  MD5Hash, hashLength = string(file, True, True)

  backtrackLen += hashLength

  return MD5Hash, backtrackLen

def skipAfterMD5(file, clientVer):
  string(file)

  # figure out difficulty section length and skip accordingly
  if clientVer < 20140609:
    file.seek(27, 1)
  else:
    file.seek(39, 1)

  # skip star ratings
  if clientVer >= 20140609:
    if clientVer > 20250107:
      for _ in range(4):
        totalPairsLength = integer(file) * 10
        file.seek(totalPairsLength, 1)
    else:
      for _ in range(4):
        totalPairsLength = integer(file) * 14
        file.seek(totalPairsLength, 1)

  # skip to timing points
  file.seek(12, 1)

  # get timing points length
  totalTimingPoints = integer(file)
  # print(f'timingPoints size: {totalTimingPoints}')
  timingPointsLength = totalTimingPoints * 17

  # skip more to get to strings
  file.seek(timingPointsLength + 23, 1)

  string(file)
  string(file)

  # skip a short to get to another string
  file.seek(2, 1)

  string(file)
  
  # skip to get to another string
  file.seek(10, 1)

  string(file)

  # skip more
  file.seek(13, 1)

  # skip extra two bytes because there was a short here before ver. 20140609 for some reason
  if clientVer < 20140609:
    file.seek(7, 1)
  else:
    file.seek(5, 1)

def getMapByMD5(dbURL, MD5):
  with open(dbURL, 'rb') as dbFile:
    clientVer = integer(dbFile)

    # skip to player name
    dbFile.seek(17, 0)

    # read player name to skip further
    string(dbFile)

    totalBeatmaps = integer(dbFile)

    for i in range(totalBeatmaps):
      currentBeatmapMD5, backtrack = beatmapMD5(dbFile, clientVer)

      if currentBeatmapMD5 == MD5:
        # print('going back')
        dbFile.seek(-backtrack, 1)
        return beatmap(dbFile, clientVer)

      # print(f'skipping beatmap no. {i+1}')
      skipAfterMD5(dbFile, clientVer)

    return None
