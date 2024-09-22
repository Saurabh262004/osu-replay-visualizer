from os import walk

def updateSongsList(osuDir):
  d = []
  string = ''

  for (dirpath, dirnames, filenames) in walk(osuDir + '/Songs'):
    d.extend(dirnames)
    break

  for i in d:
    string += f'{i}\n'

  dumpFile = open('././data/songsList.txt', 'w')

  dumpFile.write(string)