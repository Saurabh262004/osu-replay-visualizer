from typing import Optional, Union, List
from modules.misc.helpers import tryToNum

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

def getFileSections(fileContent: str, sectionData: dict) -> dict:
  sectionsData = {}

  for i in range(sectionData['total']):
    section = sectionData['headers'][i]
    sectionStart = fileContent.find(section)

    if sectionStart == -1:
      continue

    singleSectionData = fileContent[sectionStart + len(section) : fileContent[sectionStart:].find(sectionData['sectionEnd']) + sectionStart]
    sectionsData[sectionData['names'][i]] = singleSectionData

  return sectionsData
