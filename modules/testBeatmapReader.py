from json import dumps
from typing import Union, Optional
from modules.helpers import tryToNum
from modules.gameLists import MAP_FILE_SECTIONS

ALLOWED_RETURN_TYPES = ('pyObject', 'json')

def separateByComma(sectionSTR: str, convertValuesToNum: Optional[bool] = False) -> list:
  lines = sectionSTR.splitlines()
  data = []

  if len(lines) > 1:
    for line in lines:
      if convertValuesToNum:
        data.append([tryToNum(value.strip()) for value in line.split(',')])
      else:
        data.append([value.strip() for value in line.split(',')])
  else:
    data = [tryToNum(value.strip()) for value in lines[0].split(',')]

  return data

def keyValuePairs(sectionSTR: str, convertValuesToNum: Optional[bool] = False) -> dict:
  lines = sectionSTR.splitlines()
  pairs = {}

  for line in lines:
    containsMultipleValues = False
    pair = line.split(':')

    value = pair[1].strip()

    if value.find(',') > -1:
      containsMultipleValues = True

    if not containsMultipleValues and convertValuesToNum:
        value = tryToNum(value)
    else:
      value = separateByComma(value, convertValuesToNum)

    pairs[pair[0].strip()] = value

  return pairs

def getMapSections(mapContent: str) -> dict:
  sectionsData = {}

  for i in range(MAP_FILE_SECTIONS['total']):
    section = MAP_FILE_SECTIONS['headers'][i]
    sectionStart = mapContent.find(section)

    if sectionStart == -1:
      continue

    singleSectionData = mapContent[sectionStart + len(section) : mapContent[sectionStart:].find(MAP_FILE_SECTIONS['sectionEnd']) + sectionStart]
    sectionsData[MAP_FILE_SECTIONS['names'][i]] = singleSectionData

  return sectionsData

## !!!FUNCTION IN PROGRESS!!! ##
def readMap(mapURL: str, returnType: Optional[str] = 'pyObject', dumpJsonURL: Optional[str] = None) -> Union[dict, str, None]:
  if returnType not in ALLOWED_RETURN_TYPES:
    raise ValueError(f'Invalid return type: \'{returnType}\'. Allowed values are: {ALLOWED_RETURN_TYPES}.')

  if not mapURL.endswith('.osu'):
    raise ValueError(f'Invalid url: expected a .osu file, received : {mapURL}')

  try:
    with open(mapURL, 'r', encoding = 'utf-8') as mapFile:
      mapContent = mapFile.read() + '\n'

      mapObject = {}
      mapObject['fileVer'] = int(mapContent.split('\n')[0][17:])

      sections = getMapSections(mapContent)

      for i in range(MAP_FILE_SECTIONS['total']):
        sectionName = MAP_FILE_SECTIONS['names'][i]

        if not sectionName in sections:
          continue

        if MAP_FILE_SECTIONS['types'][i] == 'kvp':
          mapObject[sectionName] = keyValuePairs(sections[sectionName], True)
        elif MAP_FILE_SECTIONS['types'][i] == 'csl':
          mapObject[sectionName] = separateByComma(sections[sectionName], True)

      if dumpJsonURL:
        try:
          with open(dumpJsonURL, 'w') as jsonFile:
            jsonFile.write(dumps(mapObject, indent = 2))
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
