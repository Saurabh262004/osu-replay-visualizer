from json import dumps
from typing import Union, Optional, List, Dict
from modules.helpers import tryToNum
from modules.gameLists import MAP_FILE_SECTIONS

ALLOWED_RETURN_TYPES = ('pyObject', 'json')

def hitSample(s: str) -> dict:
  separateS = s.split(':')

  return {
    'normal': int(separateS[0]),
    'addition': int(separateS[1]),
    'index': int(separateS[2]),
    'volume': int(separateS[3]),
    'filename': separateS[4]
  }

def processSliderParams(rawValues: list) -> dict:
  slider = {}
  rawValuesLen = len(rawValues)

  cTypeAndcPoints = rawValues[5].split('|')
  slider['curveType'] = cTypeAndcPoints[0]
  cPointsRaw = cTypeAndcPoints[1:]
  slider['curvePoints'] = []

  for point in cPointsRaw:
    separateXY = point.split(':')
    slider['curvePoints'].append({
      'x': int(separateXY[0]),
      'y': int(separateXY[1])
    })
  
  slider['slides'] = rawValues[6]
  slider['length'] = rawValues[7]

  if rawValuesLen > 9:
    edgeSoundsRaw = rawValues[8].split('|')
    slider['edgeSounds'] = [int(v) for v in edgeSoundsRaw]

    edgeSetsRaw = rawValues[9].split('|')
    edgeSetsSeparate = [[int(v1) for v1 in v.split(':')] for v in edgeSetsRaw]
    slider['edgeSets'] = [{'normal': v[0], 'addition': v[1]} for v in edgeSetsSeparate]

    if rawValuesLen > 10:
      slider['hitSample'] = hitSample(rawValues[10])

  return slider

def processSpinnerParams(rawValues: list) -> dict:
  spinner = {
    'endTime': int(rawValues[5]),
    'hitSample': hitSample(rawValues[6]) if len(rawValues) > 6 else None
  }
  return spinner

def processHitobjectParams(rawValues: list) -> dict:
  hitobject = {}

  hitobject['x'] = rawValues[0]
  hitobject['y'] = rawValues[1]
  hitobject['time'] = rawValues[2]

  objectType = bin(rawValues[3])[2:].zfill(8)

  hitobject['type'] = (
    'hitcircle' if objectType[7] == '1'
    else 'slider' if objectType[6] == '1'
    else 'spinner' if objectType[4] == '1'
    else 'uncategorized'
  )

  hitobject['newCombo'] = (objectType[5] == '1')

  hitobject['comboColorsSkip'] = int(objectType[1:4], 2)

  if objectType[0] == '1':
    hitobject['maniaHoldNote'] = True
  else:
    hitobject['maniaHoldNote'] = False

  hitobject['hitSound'] = rawValues[4]

  updateObject = (
    {'hitSample': hitSample(rawValues[5])} if hitobject['type'] == 'hitcircle'
    else processSliderParams(rawValues) if hitobject['type'] == 'slider'
    else processSpinnerParams(rawValues) if hitobject['type'] == 'spinner'
    else {}
  )

  hitobject.update(updateObject)

  return hitobject

def processTimingPoints(timingPoints: List[List[Union[int, float]]]) -> List[Dict[str, Union[int, float]]]:
  processedTimingPoints = []

  for point in timingPoints:
    newPoint = {
      'time': point[0],
      'beatLength': point[1],
      'meter': point[2],
      'sampleSet': point[3],
      'sampleIndex': point[4],
      'volume': point[5],
      'uninherited': point[6],
      'effects': point[7]
    }

    if newPoint['uninherited'] == 0:
      newPoint['inverseSliderVelocityMultiplier'] = newPoint.pop('beatLength')

    processedTimingPoints.append(newPoint)

  return processedTimingPoints

def separateByComma(sectionSTR: str, convertValuesToNum: Optional[bool] = False) -> Union[List[Union[int, float, str]], List[List[Union[int, float, str]]]]:
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

    if not containsMultipleValues:
      if convertValuesToNum:
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

      mapObject['timingPoints'] = processTimingPoints(mapObject['timingPoints'])
      mapObject['hitobjects'] = [processHitobjectParams(raw) for raw in mapObject['hitobjects']]

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
