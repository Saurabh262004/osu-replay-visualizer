from osuDataTypes import *

def getDataBase(dbURL):
  with open(dbURL, 'rb') as dbFile:
    DB = {
      'clientVersion' : integer(dbFile),
      'SongsFolderCount' : integer(dbFile),
      'accountUnlocked' : boolean(dbFile),
      'accountUnlockDate' : dateTime(dbFile),
      'playerName' : string(dbFile),
      'totalBeatmaps' : integer(dbFile)
    }

    return DB

print(getDataBase('./testFiles/osu!.db'))