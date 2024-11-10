from struct import unpack as up
from lzma import decompress as dcmp

def byte(file):
  return up('B', file.read(1))[0]

def boolean(file):
  if (up('B', file.read(1)) == b'\x00'):
    return False
  return True

def short(file):
  return up('h', file.read(2))[0]

def integer(file):
  return up('i', file.read(4))[0]

def long(file):
  return up('q', file.read(8))[0]

def ULEB128(file):
  result = 0
  shift = 0

  while True:
    byte = file.read(1)
    byte_value = ord(byte)
    result |= (byte_value & 0x7F) << shift

    if (byte_value & 0x80) == 0:
      break

    shift += 7

  return result

def string(file):
  extractedSTR = ''
  if file.read(1) == b'\x0b':
    stringLength = ULEB128(file)

    extractedSTR += file.read(stringLength).decode('utf-8')

  return extractedSTR

def replayArray(file):
  replayByteArrayLength = integer(file)
  LZMAbyteArray = file.read(replayByteArrayLength)
  decodedReplayString = dcmp(LZMAbyteArray).decode('ascii')

  replayArray = []
  actions = []
  action = ''

  for char in decodedReplayString:
    if char == '|':
      actions.append(action)
      action = ''
    elif char == ',':
      replayArray.append({'w' : int(actions[0]), 'x' : float(actions[1]), 'y' : float(actions[2]), 'z' : int(action)})
      action = ''
      actions = []
    else:
      action += char

  return replayArray
