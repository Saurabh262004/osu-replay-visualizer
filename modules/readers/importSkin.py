import os
from pygame import image
from modules.misc.gameLists import SKIN_ELEMENTS, FONT_ELEMENTS
from modules.readers.parsingHelpers import keyValuePairs

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

  # parse the skin.ini config file
  try:
    with open(skin['configURL'], 'r') as config:
      configLines = config.readlines()
      processedLines = ''

      for line in configLines:
        stripChars = [' ', '\t']
        for _ in range(len(stripChars)):
          for c in stripChars:
            line = line.strip(c)
        if len(line) > 0 and line[0].isalpha():
          processedLines += line

      skin['config'] = keyValuePairs(processedLines, True)

  except FileNotFoundError:
    raise FileNotFoundError(f"The file at URL '{skin['configURL']}' does not exist. Please provide a valid path.")
  except PermissionError:
    raise PermissionError(f"Access to the file '{skin['configURL']}' is denied. Please check file permissions.")
  except Exception as e:
    raise e

  # load the skin elements
  for element in SKIN_ELEMENTS:
    imageURL = f"{skin['url']}/{element}.png"
    requiredElementNotFound = False

    if os.path.isfile(imageURL):
      skin['elements'][element] = image.load(imageURL)
    elif (SKIN_ELEMENTS[element]['animetable']):
      skin['elements'][element] = []
      i = 0
      imageURL = f"{skin['url']}/{SKIN_ELEMENTS[element]['animationName'].replace('*', str(i))}.png"

      while os.path.isfile(imageURL):
        skin['elements'][element].append(image.load(imageURL))
        i += 1
        imageURL = f"{skin['url']}/{SKIN_ELEMENTS[element]['animationName'].replace('*', str(i))}.png"

      if len(skin['elements'][element]) == 0 and SKIN_ELEMENTS[element]['required']:
        skin['elements'].pop(element)
        requiredElementNotFound = True
    elif SKIN_ELEMENTS[element]['required']:
      requiredElementNotFound = True

    if requiredElementNotFound:
      raise FileNotFoundError(f"One of the necessary skin elements, '{element}', is missing from the skin '{skinName}'. Please provide a valid skin")

  # load the font elements
  for element in FONT_ELEMENTS:
    if not FONT_ELEMENTS[element]['prefixIdentifier'] in skin['config']:
      skin['config'][FONT_ELEMENTS[element]['prefixIdentifier']] = element

    for fontURLPostfix in FONT_ELEMENTS[element]['urls']:
      fontURL = f"{skin['url']}/{skin['config'][FONT_ELEMENTS[element]['prefixIdentifier']]}{fontURLPostfix}.png"

      if os.path.isfile(fontURL):
        skin['elements'][f'{element}{fontURLPostfix}'] = image.load(fontURL)

  return skin
