import json

def getJsonByOsu(url, dumpURL=None):
  map = open(url, "r")
  hitobject_data = ""
  hitobject_json = "{"
  flag = False

  for line in map:
    if flag:
      hitobject_data += line

    if line == "[HitObjects]\n":
      flag = True

  hitobject_line = ""
  hitobject_no = 0

  for i in range(len(hitobject_data)):

    if not hitobject_data[i] == "\n":
      hitobject_line += hitobject_data[i]
    else:
      hitobject_line += ","
      hitobject = "{"
      param_no = 0
      hitobject_param = ""
      new_combo = "0"

      for j in range(len(hitobject_line)):
        if not hitobject_line[j] == ",":
          hitobject_param += hitobject_line[j]
        else:
          param_no += 1
          param_name = ""

          if (param_no == 1):
            param_name = "x"
          elif (param_no == 2):
            param_name = "y"
          elif (param_no == 3):
            param_name = "time"
          elif (param_no == 4):
            param_name = "type"
            if (hitobject_param == "12"):
              hitobject_param = "3"
            elif (hitobject_param == "2" or hitobject_param == "4" or hitobject_param == "5" or hitobject_param == "6"):
              new_combo = "1"
          elif (param_no == 6 and (hitobject_param[0] == "B" or hitobject_param[0] == "C" or hitobject_param[0] == "L" or hitobject_param[0] == "P")):
            param_name = "objectParams"
          else:
            param_name = f"param{param_no}"

          hitobject += f"\"{param_name}\": \"{hitobject_param}\","
          hitobject_param = ""

      hitobject_line = ""
      hitobject = hitobject[0:len(hitobject)-1]
      hitobject += "}"
      hitobject_pyobj = json.loads(hitobject)

      if ("objectParams" in hitobject_pyobj):
        hitobject_pyobj["type"] = "1"
      elif (not hitobject_pyobj["type"] == "3"):
        hitobject_pyobj["type"] = "0"

      hitobject_pyobj["newCombo"] = new_combo

      hitobject = json.dumps(hitobject_pyobj)
      hitobject_json += f"\"{hitobject_no}\": {hitobject},"
      hitobject_no += 1

  hitobject_json = hitobject_json[0:len(hitobject_json)-1]
  hitobject_json += "}"

  if (dumpURL):
    dumpFile = open(dumpURL, "w")
    dumpFile.write(hitobject_json)
    dumpFile.close()

  return hitobject_json

newJSON = getJsonByOsu("map1.osu", "test1.json")
