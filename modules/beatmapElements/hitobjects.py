from typing import Union, List, Dict, Optional
import math
from copy import deepcopy
from modules.misc.helpers import dist
import pygame as pg

numType = Union[int, float]

class Hitcircle:
  def __init__(self, objectDict: dict, beatmap, hitTime: Optional[numType] = None):
    self.rawDict = objectDict
    self.beatmap = beatmap
    self.x = self.rawDict['x']
    self.y = self.rawDict['y']
    self.time = self.rawDict['time']
    self.comboIndex = 0
    self.comboColorIndex = 0

    if not hitTime is None:
      self.hit = hitTime
    else:
      self.hit = self.time

class Slider:
  def __init__(self, objectDict: dict, beatmap, hitTime: Optional[numType] = None):
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
    self.slideTime = 0
    self.bodySurface = None
    self.bodySurfacePos = (0, 0)
    self.bodyPath = []
    self.baseBodyPath = []
    self.transformedBodyPath = []

    if not hitTime is None:
      self.hit = hitTime
    else:
      self.hit = self.time

    self.head = Hitcircle(self.rawDict, self.beatmap, self.hit)

    self.anchors = [
      {
        'x': self.x,
        'y': self.y,
        'red': False
      }
    ]

    self.anchors.extend([anchor for anchor in self.rawDict['curvePoints']])

    self.totalAnchors = len(self.anchors)

    if self.totalAnchors == 2:
      del self.curveType
      self.curveType = 'L'

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
        self.baseBodyPath.append(self.computeBezier(curve, 0.005))
    elif self.curveType == 'L':
      self.baseBodyPath = self.computeLinearBody(self.anchors, 0.005)
    elif self.curveType == 'P':
      self.baseBodyPath = self.computeCircleBody(self.anchors, 0.005)

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

  def computeCircleBody(self, anchors: list, radianInterval: numType):
    calculatedPoints = []

    if not len(anchors) == 3:
      print(self.totalAnchors)
      print(anchors)

    centerXtop = ((anchors[0]['x']**2 + anchors[0]['y']**2) * (anchors[1]['y'] - anchors[2]['y'])) + ((anchors[1]['x']**2 + anchors[1]['y']**2) * (anchors[2]['y'] - anchors[0]['y'])) + ((anchors[2]['x']**2 + anchors[2]['y']**2) * (anchors[0]['y'] - anchors[1]['y']))
    centerYtop = ((anchors[0]['x']**2 + anchors[0]['y']**2) * (anchors[2]['x'] - anchors[1]['x'])) + ((anchors[1]['x']**2 + anchors[1]['y']**2) * (anchors[0]['x'] - anchors[2]['x'])) + ((anchors[2]['x']**2 + anchors[2]['y']**2) * (anchors[1]['x'] - anchors[0]['x']))

    coordBottom = 2*((anchors[0]['x'] * (anchors[1]['y'] - anchors[2]['y'])) + (anchors[1]['x'] * (anchors[2]['y'] - anchors[0]['y'])) + (anchors[2]['x'] * (anchors[0]['y'] - anchors[1]['y'])))

    bodyCircleMidpoint = {
      'x': centerXtop / coordBottom,
      'y': centerYtop / coordBottom
    }

    self.centerX = bodyCircleMidpoint['x']
    self.centerY = bodyCircleMidpoint['y']

    bodyCircleRadius = dist(anchors[0]['x'], anchors[0]['y'], bodyCircleMidpoint['x'], bodyCircleMidpoint['y'])

    startAngle = math.atan2(anchors[0]['y'] - bodyCircleMidpoint['y'],anchors[0]['x'] - bodyCircleMidpoint['x'])
    middleAngle = math.atan2(anchors[1]['y'] - bodyCircleMidpoint['y'],anchors[1]['x'] - bodyCircleMidpoint['x'])
    endAngle = math.atan2(anchors[2]['y'] - bodyCircleMidpoint['y'], anchors[2]['x'] - bodyCircleMidpoint['x'])

    radianInterval = abs(radianInterval)
    radianIntervalDirectional = radianInterval
    if (startAngle < endAngle < middleAngle) or (middleAngle < startAngle < endAngle) or (endAngle < middleAngle < startAngle):
      radianIntervalDirectional *= -1

    straightPath = False
    if (startAngle < middleAngle < endAngle) or (endAngle < middleAngle < startAngle):
      straightPath = True

    progressStart = min(startAngle, endAngle) if straightPath else 0
    progressEnd = max(startAngle, endAngle) if straightPath else ((math.pi * 2) - (max(startAngle, endAngle) - min(startAngle, endAngle)))
    currentAngle = startAngle
    while (progressStart <= progressEnd):
      newX = bodyCircleMidpoint['x'] + math.cos(currentAngle) * bodyCircleRadius
      newY = bodyCircleMidpoint['y'] + math.sin(currentAngle) * bodyCircleRadius

      calculatedPoints.append({'x': newX, 'y': newY})

      currentAngle += radianIntervalDirectional
      progressStart += radianInterval

    return calculatedPoints

  def transformBodyPath(self, resMultiplier, resPadding):
    if self.curveType == 'B':
      self.transformedBodyPath = []
      totalBezierLength = 0

      for curve in self.baseBodyPath:
        self.transformedBodyPath.extend([
          {
            'x': (point['x'] * resMultiplier[0]) + resPadding[0],
            'y': (point['y'] * resMultiplier[1]) + resPadding[1]
          } for point in curve
        ])

      ## don't think this is still good enough... ##
      lastDistance = 0
      self.bodyPath.append(self.transformedBodyPath[0])
      targetDistance = 5
      for i in range(1, len(self.transformedBodyPath)):
        totalBezierLength += dist(self.transformedBodyPath[i-1]['x'], self.transformedBodyPath[i-1]['y'], self.transformedBodyPath[i]['x'], self.transformedBodyPath[i]['y'])

        if lastDistance == 0:
          p1 = self.bodyPath[-1]
        else:
          p1 = self.transformedBodyPath[i-1]

        p2 = self.transformedBodyPath[i]

        segmentLength = dist(p1['x'], p1['y'], p2['x'], p2['y'])

        if (lastDistance + segmentLength) >= targetDistance:
          t = (targetDistance - lastDistance) / segmentLength
          self.bodyPath.append(self.lerpAnchors(p1, p2, t))
          lastDistance = 0
        else:
          lastDistance += segmentLength
    elif self.curveType == 'L' or self.curveType == 'P':
      self.transformedBodyPath = [
        {
          'x': (point['x'] * resMultiplier[0]) + resPadding[0],
          'y': (point['y'] * resMultiplier[1]) + resPadding[1]
        } for point in self.baseBodyPath
      ]
      self.bodyPath = self.transformedBodyPath

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
