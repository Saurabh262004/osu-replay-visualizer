from typing import Union, List, Dict
from copy import deepcopy
from modules.misc.helpers import dist
import pygame as pg

numType = Union[int, float]

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
    self.slideTime = 0
    self.bodySurface = None
    self.bodySurfacePos = (0, 0)
    self.bodyPath = []

    if self.curveType == 'B':
      self.baseBezier = []
      self.transformedBezier = []
    elif self.curveType == 'L':
      self.baseLinear = []
      self.transformedLinear = []

    self.anchors = [
      {
        'x': self.x,
        'y': self.y,
        'red': False
      }
    ]

    self.anchors.extend([anchor for anchor in self.rawDict['curvePoints']])

    self.anchorLength = 0

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

    self.computeBaseBodyPath()

  def computeBaseBodyPath(self):
    if self.curveType == 'B':
      for curve in self.curves:
        self.baseBezier.append(self.computeBezier(curve, 0.005))
    elif self.curveType == 'L':
      self.baseLinear = self.computeLinearBody(self.anchors, 0.005)
    elif self.curveType == 'P':
      pass

  @staticmethod
  def lerpAnchors(anchor1: Dict[str, numType], anchor2: Dict[str, numType], t: numType) -> Dict[str, numType]:
    return {
      'x': anchor1['x'] + t * (anchor2['x'] - anchor1['x']),
      'y': anchor1['y'] + t * (anchor2['y'] - anchor1['y'])
    }

  def computeBezier(self, anchors: list, tInterval: numType) -> List[Dict[str, numType]]:
    calculatedPoints = []

    interpolatedAnchors = deepcopy(anchors)

    t = 0
    while (t <= 1):
      interpolatedAnchors = deepcopy(anchors)
      for _ in range(len(interpolatedAnchors) - 1):
        tmpAnchors = []
        for i in range(len(interpolatedAnchors) - 1):
          tmpAnchors.append(self.lerpAnchors(interpolatedAnchors[i], interpolatedAnchors[i+1], t))

        interpolatedAnchors = deepcopy(tmpAnchors)

      calculatedPoints.append(deepcopy(interpolatedAnchors[0]))

      t += tInterval

    return calculatedPoints

  def computeLinearBody(self, anchors: list, tInterval: numType) -> List[Dict[str, numType]]:
    calculatedPoints = []

    t = 0
    while (t <= 1):
      calculatedPoints.append(self.lerpAnchors(anchors[0], anchors[1], t))
      t += tInterval

    return calculatedPoints

  def transformBodyPath(self, resMultiplier, resPadding):
    if self.curveType == 'B':
      self.transformedBezier = []
      totalBezierLength = 0

      for curve in self.baseBezier:
        self.transformedBezier.extend([
          {
            'x': (point['x'] * resMultiplier[0]) + resPadding[0],
            'y': (point['y'] * resMultiplier[1]) + resPadding[1]
          } for point in curve
        ])

      ## still doesn't work as well... ##
      lastDistance = 0
      self.bodyPath.append(self.transformedBezier[0])
      targetDistance = 5
      for i in range(1, len(self.transformedBezier)):
        totalBezierLength += dist(self.transformedBezier[i-1]['x'], self.transformedBezier[i-1]['y'], self.transformedBezier[i]['x'], self.transformedBezier[i]['y'])
        if lastDistance == 0:
          p1 = self.bodyPath[-1]
        else:
          p1 = self.transformedBezier[i-1]

        p2 = self.transformedBezier[i]

        segmentLength = dist(p1['x'], p1['y'], p2['x'], p2['y'])

        if (lastDistance + segmentLength) >= targetDistance:
          t = (targetDistance - lastDistance) / segmentLength
          self.bodyPath.append(self.lerpAnchors(p1, p2, t))
          lastDistance = 0
        else:
          lastDistance += segmentLength
    elif self.curveType == 'L':
      self.transformedLinear = [
        {
          'x': (point['x'] * resMultiplier[0]) + resPadding[0],
          'y': (point['y'] * resMultiplier[1]) + resPadding[1]
        } for point in self.baseLinear
      ]
      self.bodyPath = self.transformedLinear
    elif self.curveType == 'P':
      pass

  def renderBody(self):
    CR = self.beatmap.circleRadius
    minX = minY = maxX = maxY = 0
    translatedBodyPath = []

    for point in self.bodyPath:
      if minX > (point['x'] - CR):
        minX = (point['x'] - CR)

      if maxX < (point['x'] + CR):
        maxX = (point['x'] + CR)

      if minY > (point['y'] - CR):
        minY = (point['y'] - CR)

      if maxY < (point['y'] + CR):
        maxY = (point['y'] + CR)

    bodySize = (maxX - minX, maxY - minY)

    self.bodySurface = pg.surface.Surface(bodySize, flags=pg.SRCALPHA)

    translatedBodyPath = [
      {
        'x': point['x'] - minX,
        'y': point['y'] - minY
      } for point in self.bodyPath
    ]

    self.bodySurfacePos = (minX, minY)
    self.bodySurface.fill((0, 0, 0, 0))

    ## idk how I'm gonna do this the right way... gotta figure out something tho ##
    for point in translatedBodyPath:
      pg.draw.circle(self.bodySurface, (255, 255, 255, 32), (point['x'], point['y']), CR)

class Spinner:
  def __init__(self, objectDict: dict, map):
    self.rawDict = objectDict
    self.map = map
    self.time = self.rawDict['time']
    self.endTime = self.rawDict['endTime']
    self.comboIndex = 0
    self.comboColorIndex = 0
