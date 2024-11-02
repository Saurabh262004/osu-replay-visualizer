from os import walk

def updateSongsList(osuDir):
  d = []
  string = ''

  for (dirpath, dirnames, filenames) in walk(osuDir + '/Songs'):
    d.extend(dirnames)
    break

  for i in d:
    string += f'{i}\n'

  with open('././data/songsList.dat', 'w') as dumpFile:
    dumpFile.write(string)
