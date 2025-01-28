from pygame import Surface as pgSurface

class Hitcircle:
  def __init__(self, objectDict: dict, beatmap):
    self.rawDict = objectDict
    self.beatmap = beatmap
    self.x = self.rawDict['x']
    self.y = self.rawDict['y']
    self.time = self.rawDict['time']
    self.comboIndex = 0
    self.comboColorIndex = 0
    self.hit = self.time

  def getRenderable(self) -> pgSurface:
    pass

class Slider:
  def __init__(self, objectDict: dict, map):
    self.rawDict = objectDict
    self.map = map
    self.x = self.rawDict['x']
    self.y = self.rawDict['y']
    self.time = self.rawDict['time']
    self.curveType = self.rawDict['curveType']
    self.comboIndex = 0
    self.comboColorIndex = 0
    self.hit = self.time

    self.anchors = [
      {
        'x': self.x,
        'y': self.y,
        'red': False
      }
    ]

    self.anchors.extend([anchor for anchor in self.rawDict['curvePoints']])

  def getRenderable(self) -> pgSurface:
    pass

class Spinner:
  def __init__(self, objectDict: dict, map):
    self.rawDict = objectDict
    self.map = map
    self.time = self.rawDict['time']
    self.comboIndex = 0
    self.comboColorIndex = 0

  def getRenderable(self) -> pgSurface:
    pass
