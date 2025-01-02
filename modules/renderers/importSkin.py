import os
from pygame import image
from modules.misc.gameLists import NECESSARY_SKIN_ELEMENT_NAMES, SKIN_CONFIG_SECTIONS
from modules.readers.parsingHelpers import keyValuePairs, getFileSections

def importSkin(skinName: str, osuURL: str) -> dict:
  if not os.path.isdir(osuURL):
    raise FileNotFoundError(f"The directory '{osuURL}' does not exist. Please provide a valid path to the osu! folder.")

  skinURL = osuURL + '/Skins/' + skinName

  if not os.path.isdir(skinURL):
    raise FileNotFoundError(f"The skin '{skinName}' does not exist. Please provide a valid skin.")

  skin = {
    'url': skinURL,
    'configURL': skinURL + '/skin.ini',
    'folderName': skinName,
    'elements': {},
    'config': {}
  }

  for element in NECESSARY_SKIN_ELEMENT_NAMES:
    imageURL = skin['url'] + '/' + element + '.png'

    if not os.path.isfile(imageURL):
      raise FileNotFoundError(f"One of the necessary skin elements, '{element}', is missing from the skin '{skinName}'. Please provide a valid skin.")

    skin['elements'][element] = image.load(imageURL)

  try:
    with open(skin['configURL'], 'r') as config:
      configLines = config.readlines()
      processedLines = ''

      for line in configLines:
        line = line.strip(' ')
        if line[0].isalpha() or line[0] == '[' or line[0] == '\n':
          processedLines += line

      processedLines += '\n\n'

      skinSections = getFileSections(processedLines, SKIN_CONFIG_SECTIONS)

      for section in skinSections:
        skin['config'][section] = keyValuePairs(skinSections[section], True)

  except FileNotFoundError:
    raise FileNotFoundError(f"The file at URL '{skin['configURL']}' does not exist. Please provide a valid path.")
  except PermissionError:
    raise PermissionError(f"Access to the file '{skin['configURL']}' is denied. Please check file permissions.")
  except Exception as e:
    raise e

  return skin
