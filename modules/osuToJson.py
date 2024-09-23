import json

def separateByColon(string, intValue=False):
  stringJson = '{'

  stringElement = ''
  for i in range(len(string)):
    if string[i] == ':':
      stringJson += f'\"{stringElement}\": '
      stringElement = ''
    elif string[i] == '\n':
      if intValue and len(stringElement) > 0:
        stringJson += f'{stringElement}, '
      else:
        stringJson += f'\"{stringElement}\", '
      stringElement = ''
    else:
      stringElement += string[i]

  stringJson = stringJson[0:len(stringJson)-6]
  stringJson += '}'

  return stringJson

def getJsonByOsu(osuURL, dumpJsonURL=None):
  map = open(osuURL, 'r', encoding='utf-8')
  newJson = '{'
  audioFileNameRaw = ''
  audioFileName = ''
  metadataRaw = ''
  diffRaw = ''
  hitobjectDataRaw = ''
  hitobjectJson = '\"hitobjects\": ['
  generalMark = False
  metadataMark = False
  diffMark = False
  hitobjectsMark = False
  fileVerMark = True
  fileVer = -1

  for line in map:
    if fileVerMark:
      fileVer = int(line[17:-1])
      fileVerMark = False

    if generalMark:
      audioFileNameRaw = line
      generalMark = False
    elif metadataMark:
      metadataRaw += line
    elif diffMark:
      diffRaw += line
    elif hitobjectsMark:
      hitobjectDataRaw += line

    if line == '[General]\n':
      generalMark = True
    elif line == '[Metadata]\n':
      metadataMark = True
    elif line == '[Difficulty]\n':
      diffMark = True
    elif line == '[HitObjects]\n':
      hitobjectsMark = True
    elif line == '\n':
      generalMark = False
      metadataMark = False
      diffMark = False
      hitobjectsMark = False

  map.close()

  newJson += f'\"ver\": {fileVer}, '

  newJson += f'\"audioFileName\": \"{audioFileNameRaw[15:len(audioFileNameRaw)-1]}\", '

  newJson += '\"metadata\": ' + separateByColon(metadataRaw) + ', '

  newJson += '\"difficulty\": ' + separateByColon(diffRaw, True) + ', '

  hitobjectLine = ''
  hitobjectNum = 0

  for i in range(len(hitobjectDataRaw)):
    if not hitobjectDataRaw[i] == '\n':
      hitobjectLine += hitobjectDataRaw[i]
    else:
      hitobjectLine += ','
      hitobject = '{'
      paramNum = 0
      hitobjectParam = ''

      for j in range(len(hitobjectLine)):
        if not hitobjectLine[j] == ',':
          hitobjectParam += hitobjectLine[j]
        else:
          paramNum += 1
          paramName = ''

          if (paramNum == 1):
            paramName = 'x'
          elif (paramNum == 2):
            paramName = 'y'
          elif (paramNum == 3):
            paramName = 'time'
          elif (paramNum == 4):
            paramName = 'type'
            if (hitobjectParam == '12'):
              hitobjectParam = 2
          elif (paramNum == 6 and (hitobjectParam[0] == 'B' or hitobjectParam[0] == 'C' or hitobjectParam[0] == 'L' or hitobjectParam[0] == 'P')):
            paramName = 'objectParams'
            hitobjectParam += '|'
            newObjectParams = '{\"curveType\": \"' + hitobjectParam[0] + '\", \"anchors\": ['
            anchorCoordinate = ''
            anchorsCoordinateList = []

            for k in range(2, len(hitobjectParam)):
              currentChar = hitobjectParam[k]
              if currentChar == ':' or currentChar == '|':
                anchorsCoordinateList.append(anchorCoordinate)
                anchorCoordinate = ''
              else:
                anchorCoordinate += currentChar

            skipAnchorIndex = -1
            for k in range(0, len(anchorsCoordinateList), 2):
              anchorType = '0'

              if len(anchorsCoordinateList) > 2 and k < len(anchorsCoordinateList)-3:
                if anchorsCoordinateList[k] == anchorsCoordinateList[k+2] and anchorsCoordinateList[k+1] == anchorsCoordinateList[k+3]:
                  skipAnchorIndex = k+2
                  anchorType = '1'

              if not (k == skipAnchorIndex):
                newObjectParams += '{\"anchorType\": ' + anchorType + f', \"x\": {anchorsCoordinateList[k]}, \"y\": {anchorsCoordinateList[k+1]}' + '}, '

            newObjectParams = newObjectParams[0:len(newObjectParams)-2] + ']}'
            hitobjectParam = newObjectParams
          else:
            paramName = f'param{paramNum}'
            hitobjectParam = f'\"{hitobjectParam}\"' # temporary

          hitobject += f'\"{paramName}\": {hitobjectParam},'
          hitobjectParam = ''

      hitobjectLine = ''
      hitobject = hitobject[0:len(hitobject)-1]
      hitobject += '}'
      hitobjectPyobj = json.loads(hitobject)

      if ('objectParams' in hitobjectPyobj):
        hitobjectPyobj['type'] = 1
      elif (not hitobjectPyobj['type'] == 2):
        hitobjectPyobj['type'] = 0
      else:
        hitobjectPyobj['endTime'] = int(hitobjectPyobj.pop('param6'))

      hitobject = json.dumps(hitobjectPyobj)
      hitobjectJson += f'{hitobject}, '
      hitobjectNum += 1

  hitobjectJson = hitobjectJson[0:len(hitobjectJson)-2]
  hitobjectJson += ']'

  newJson += hitobjectJson
  newJson += '}'

  if (dumpJsonURL):
    dumpFile = open(dumpJsonURL, 'w')
    dumpFile.write(newJson)
    dumpFile.close()

  return newJson
