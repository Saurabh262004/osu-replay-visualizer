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
  def __init__(self, objectDict: dict, beatmap):
    self.rawDict = objectDict
    self.beatmap = beatmap
    self.x = self.rawDict['x']
    self.y = self.rawDict['y']
    self.time = self.rawDict['time']
    self.curveType = self.rawDict['curveType']
    self.length = self.rawDict['length']
    self.slides = self.rawDict['slides']
    self.comboIndex = 0
    self.comboColorIndex = 0
    self.hit = self.time
    self.head = Hitcircle(self.rawDict, self.beatmap)
    self.precomputedBezier = []
    self.slideTime = 0

    self.anchors = [
      {
        'x': self.x,
        'y': self.y,
        'red': False
      }
    ]

    self.anchors.extend([anchor for anchor in self.rawDict['curvePoints']])

    self.totalAnchors = len(self.anchors)

    self.curves = []

    tmpCurve = []
    for i in range(self.totalAnchors):
      if self.anchors[i]['red'] or i == (self.totalAnchors - 1):
        tmpCurve.append(self.anchors[i])
        self.curves.append(tmpCurve)
        tmpCurve = [self.anchors[i]]
      else:
        tmpCurve.append(self.anchors[i])

    # print(self.curves)

  # def renderCurves(self):
  #   if self.curveType == 'L':
  #     for curve in self.curves:
  #       tmpCurveSurface = pgSurface()

  def getRenderable(self) -> pgSurface:
    pass

class Spinner:
  def __init__(self, objectDict: dict, map):
    self.rawDict = objectDict
    self.map = map
    self.time = self.rawDict['time']
    self.endTime = self.rawDict['endTime']
    self.comboIndex = 0
    self.comboColorIndex = 0

  def getRenderable(self) -> pgSurface:
    pass
