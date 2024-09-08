import json

def getJsonByOsu(url, dumpURL=None):
  map = open(url, 'r')
  newJson = '{'
  hitobjectDataRaw = ''
  hitobjectJson = '\"hitobjects\": ['
  flag = False

  for line in map:
    if flag:
      hitobjectDataRaw += line

    if line == '[HitObjects]\n':
      flag = True

  hitobjectLine = ''
  hitobject_no = 0

  for i in range(len(hitobjectDataRaw)):

    if not hitobjectDataRaw[i] == '\n':
      hitobjectLine += hitobjectDataRaw[i]
    else:
      hitobjectLine += ','
      hitobject = '{'
      paramNum = 0
      hitobject_param = ''

      for j in range(len(hitobjectLine)):
        if not hitobjectLine[j] == ',':
          hitobject_param += hitobjectLine[j]
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
            if (hitobject_param == '12'):
              hitobject_param = '3'
          elif (paramNum == 6 and (hitobject_param[0] == 'B' or hitobject_param[0] == 'C' or hitobject_param[0] == 'L' or hitobject_param[0] == 'P')):
            paramName = 'objectParams'
          else:
            paramName = f'param{paramNum}'

          hitobject += f'\"{paramName}\": \"{hitobject_param}\",'
          hitobject_param = ''

      hitobjectLine = ''
      hitobject = hitobject[0:len(hitobject)-1]
      hitobject += '}'
      hitobject_pyobj = json.loads(hitobject)

      if ('objectParams' in hitobject_pyobj):
        hitobject_pyobj['type'] = '1'
      elif (not hitobject_pyobj['type'] == '3'):
        hitobject_pyobj['type'] = '0'
        
      

      hitobject = json.dumps(hitobject_pyobj)
      hitobjectJson += f'{hitobject},'
      hitobject_no += 1

  hitobjectJson = hitobjectJson[0:len(hitobjectJson)-1]
  hitobjectJson += ']'

  newJson += hitobjectJson
  newJson += '}'

  if (dumpURL):
    dumpFile = open(dumpURL, 'w')
    dumpFile.write(newJson)
    dumpFile.close()    

  return newJson

test1 = getJsonByOsu('map2.osu', 'test2.json')
