from modules.osuDataTypes import *
from json import dumps

def beatmap(file, clientVer):
  bm = {
    'entrySize': (lambda: integer(file) if clientVer < 20191106 else None)(),
    'artistName' : string(file),
    'artistNameUnicode' : string(file),
    'songTitle' : string(file),
    'songTitleUnicode' : string(file),
    'creatorName' : string(file),
    'difficultyName' : string(file),
    'audioFileName' : string(file),
    'MD5Hash' : string(file),
    '.osuFileName' : string(file),
    'rankedStatus' : getRankedStatus(file),
    'totalHitcircles' : short(file),
    'totalSliders' : short(file),
    'totalSpinners' : short(file),
    'lastModificationTime' : dateTime(file, 'Asia/Calcutta'),
    'approachRate' : (lambda: byte(file) if clientVer < 20140609 else single(file))(),
    'circleSize' : (lambda: byte(file) if clientVer < 20140609 else single(file))(),
    'hpDrain' : (lambda: byte(file) if clientVer < 20140609 else single(file))(),
    'overallDifficulty' : (lambda: byte(file) if clientVer < 20140609 else single(file))(),
    'sliderVelocity' : double(file),
    'standartStarRatings' : (lambda: getStarRatings(file) if clientVer >= 20140609 else None)(),
    'taikoStarRatings' : (lambda: getStarRatings(file) if clientVer >= 20140609 else None)(),
    'CTBStarRatings' : (lambda: getStarRatings(file) if clientVer >= 20140609 else None)(),
    'maniaStarRatings' : (lambda: getStarRatings(file) if clientVer >= 20140609 else None)(),
    'drainTime(s)' : integer(file),
    'totalTime(ms)' : integer(file),
    'previewPoint(ms)' : integer(file),
    'timingPoints' : timingPoints(file),
    'difficultyID' : integer(file),
    'beatmapID' : integer(file),
    'threadID' : integer(file),
    'standardGrade' : byte(file),
    'taikoGrade' : byte(file),
    'CTBGrade' : byte(file),
    'mainaGrade' : byte(file),
    'localOffset(ms)' : short(file),
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
    'aShortThatWasHereBeforeVer20140609ForSomeReason' : (lambda: short(file) if clientVer < 20140609 else None)(),
    'lastModificationTime?' : integer(file),
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

    DB['beatmaps'].extend([beatmap(dbFile, DB['clientVersion']) for _ in range(DB['totalBeatmaps'])])
    DB['userPermission'] = integer(dbFile)

    if (dumpJsonURL):
      with open(dumpJsonURL, 'w') as dumpFile:
        dumpFile.write(dumps(DB, indent=2))

    return DB

def getMapByMD5(dbURL, MD5):
  with open(dbURL, 'rb') as dbFile:
    clientVer = integer(dbFile)

    #skip to player name
    dbFile.seek(13, 1)

    #read player name to skip further
    string(dbFile)

    totalBeatmaps = integer(dbFile)
    
    for _ in range(totalBeatmaps):
      currentBeatmap = beatmap(dbFile, clientVer)
      
      if currentBeatmap['MD5Hash'] == MD5:
        return currentBeatmap

    return None
