from json import dumps
from modules.gameLists import MAP_FILE_SECTIONS
from typing import Union

MAP_RETURN_TYPES = ('pyObject', 'json')

def getMapSections(mapContent: str) -> dict:
  sectionsData = {}
  end = '\n\n'

  for i in range(MAP_FILE_SECTIONS['total']):
    section = MAP_FILE_SECTIONS['headers'][i]
    sectionStart = mapContent.find(section)

    if sectionStart == -1:
      break

    singleSectionData = mapContent[sectionStart + len(section) : mapContent[sectionStart:].find(end) + sectionStart]
    sectionsData[MAP_FILE_SECTIONS['names'][i]] = singleSectionData
    
  return sectionsData

def readMap(mapURL: str, returnType: str = 'pyObject', dumpJsonURL: str = None) -> Union[dict, str, None]:
  if returnType not in MAP_RETURN_TYPES:
    raise ValueError(f'Invalid return type: \'{returnType}\'. Allowed values are: {MAP_RETURN_TYPES}.')

  if not mapURL.endswith('.osu'):
    raise ValueError(f'Invalid url: expected a .osu file, received : {mapURL}')

  try:
    with open(mapURL, 'r', encoding = 'utf-8') as mapFile:
      mapContent = mapFile.read() + '\n'

      mapObject = {}
      mapObject['fileVer'] = int(mapContent.split('\n')[0][17:])

      sections = getMapSections(mapContent)

      ## FUNCTION IN PROGRESS ##

      if dumpJsonURL:
        try:
          with open(dumpJsonURL, 'w') as jsonFile:
            jsonFile.write(dumps(mapObject))
        except FileNotFoundError:
          print(f"The file at URL '{dumpJsonURL}' does not exist. Please provide a valid path.")
        except PermissionError:
          print(f"Access to the file '{dumpJsonURL}' is denied. Check file permissions.")

      if returnType == 'pyObject':
        return mapObject
      elif returnType == 'json':
        return dumps(mapObject)
  except FileNotFoundError:
    print(f"The file at URL '{mapURL}' does not exist. Please provide a valid path.")
    return None
  except PermissionError:
    print(f"Access to the file '{mapURL}' is denied. Check file permissions.")
    return None
