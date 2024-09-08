import json

def getJsonByOsu(osuURL, dumpJsonURL=None):
  map = open(osuURL, 'r')
  newJson = '{'
  hitobjectDataRaw = ''
  hitobjectJson = '\"hitobjects\": ['
  hitobjectsMark = False

  for line in map:
    if hitobjectsMark:
      hitobjectDataRaw += line

    if line == '[HitObjects]\n':
      hitobjectsMark = True

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

          if paramNum == 5:
            hitobjectParam = ''
            continue

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
            hitobjectParam = f'\"{hitobjectParam}\"' # temporary
            # edit objectParams value as needed here
          else:
            paramName = f'param{paramNum}'
            hitobjectParam = f'\"{hitobjectParam}\"' # also temporary
            
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
      hitobjectJson += f'{hitobject},'
      hitobjectNum += 1

  hitobjectJson = hitobjectJson[0:len(hitobjectJson)-1]
  hitobjectJson += ']'

  newJson += hitobjectJson
  newJson += '}'

  if (dumpJsonURL):
    dumpFile = open(dumpJsonURL, 'w')
    dumpFile.write(newJson)
    dumpFile.close()

  return newJson
