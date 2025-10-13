import os
import pygame as pg
from modules.misc.helpers import customStrip
from modules.misc.gameLists import SKIN_ELEMENTS, FONT_ELEMENTS, HITSOUNDS
from modules.readers.parsingHelpers import keyValuePairs

def importSkin(skinName: str, defaultSkinURL: str, osuURL: str, directSkinURL: bool = None) -> dict:
  if not os.path.isdir(osuURL):
    raise FileNotFoundError(f"The directory '{osuURL}' does not exist. Please provide a valid path to the osu! folder.")

  if not directSkinURL:
    skinURL = osuURL + '/Skins/' + skinName
  else:
    skinURL = skinName

  if not os.path.isdir(skinURL):
    raise FileNotFoundError(f"The skin '{skinName}' does not exist. Please provide a valid skin.")

  skin = {
    'url': skinURL,
    'configURL': skinURL + '/skin.ini',
    'folderName': skinName,
    'elements': {},
    'config': {},
    'hitsounds': {}
  }

  # parse the skin.ini config file
  try:
    with open(skin['configURL'], 'r', encoding='utf-8') as config:
      configLines = config.readlines()
      processedLines = ''

      for line in configLines:
        line = customStrip(line, ['\t', ' '])

        if len(line) > 0 and line[0].isalpha():
          commentIndex = line.find('//')
          if commentIndex != -1:
            line = line[:commentIndex] + '\n'
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
    stillImageURL = f"{skin['url']}/{element}.png"
    requiredElementNotFound = False

    if (SKIN_ELEMENTS[element]['animetable']):
      skin['elements'][element] = []
      i = 0
      imageURL = f"{skin['url']}/{SKIN_ELEMENTS[element]['animationName'].replace('*', str(i))}.png"

      while os.path.isfile(imageURL):
        skin['elements'][element].append(pg.image.load(imageURL).convert_alpha())
        i += 1
        imageURL = f"{skin['url']}/{SKIN_ELEMENTS[element]['animationName'].replace('*', str(i))}.png"

      if len(skin['elements'][element]) == 0:
        if os.path.isfile(stillImageURL):
          skin['elements'][element] = pg.image.load(stillImageURL).convert_alpha()
        elif SKIN_ELEMENTS[element]['required']:
          skin['elements'].pop(element)
          stillImageURL = f"{defaultSkinURL}/{element}.png"
          skin['elements'][element] = pg.image.load(stillImageURL).convert_alpha()
          requiredElementNotFound = True

    elif os.path.isfile(stillImageURL):
      skin['elements'][element] = pg.image.load(stillImageURL).convert_alpha()
    elif SKIN_ELEMENTS[element]['required']:
      stillImageURL = f"{defaultSkinURL}/{element}.png"
      skin['elements'][element] = pg.image.load(stillImageURL).convert_alpha()
      requiredElementNotFound = True

    if requiredElementNotFound:
      print(f"One of the necessary skin elements, '{element}', is missing from the skin '{skinName}'. Imported element from default skin")

  # load the font elements
  for element in FONT_ELEMENTS:
    if not FONT_ELEMENTS[element]['prefixIdentifier'] in skin['config']:
      skin['config'][FONT_ELEMENTS[element]['prefixIdentifier']] = element

    for fontURLPostfix in FONT_ELEMENTS[element]['urls']:
      fontURL = f"{skin['url']}/{skin['config'][FONT_ELEMENTS[element]['prefixIdentifier']]}{fontURLPostfix}.png"

      if os.path.isfile(fontURL):
        skin['elements'][f'{element}{fontURLPostfix}'] = pg.image.load(fontURL).convert_alpha()

  # load hitsounds
  for sampleSet in HITSOUNDS['sampleSets']:
    for hitSound in HITSOUNDS['hitSounds']:
      for fileType in HITSOUNDS['fileTypes']:
        fileName = f'{sampleSet}-hit{hitSound}'
        fileURL = f'{skin['url']}/{fileName}.{fileType}'

        if os.path.isfile(fileURL):
          skin['hitsounds'][fileName] = pg.mixer.Sound(fileURL)
          break

  return skin
