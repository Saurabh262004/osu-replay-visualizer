from typing import Union, List, Dict, Optional
import math
from copy import deepcopy
from modules.misc.helpers import dist, mapRange
import pygame as pg
import sharedWindow

numType = Union[int, float]

class Hitcircle:
  def __init__(self, objectDict: dict, beatmap, hitTime: Optional[numType] = None):
    self.rawDict = objectDict
    self.beatmap = beatmap
    self.endX = self.x = self.rawDict['x']
    self.endY = self.y = self.rawDict['y']
    self.endTime = self.time = self.rawDict['time']
    self.comboIndex = 0
    self.comboColorIndex = 0
    self.hit = False
    self.judgment = -1
    self.stackCount = 0
    self.stackOffset = 0
    self.triggeredHitSound = False
    self.hitsounds = []
    self.sampleSet = 'Normal'

    if hitTime is not None:
      self.hitTime = hitTime
    else:
      self.hitTime = self.time

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
    self.hit = False
    self.judgment = -1
    self.stackCount = 0
    self.stackOffset = 0
    self.totalSlideTime = 0
    self.endTime = 0
    self.triggeredHitSound = [False for _ in range(self.slides + 1)]
    self.hitsounds = []
    self.sampleSet = 'Normal'
    self.ticks = []
    self.tickPoses = []

    if not hitTime is None:
      self.hitTime = hitTime
    else:
      self.hitTime = self.time

    self.head = Hitcircle(self.rawDict, self.beatmap, self.hitTime)

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
    self.baseBodyPath = []

    if self.curveType == 'B':
      for curve in self.curves:
        self.baseBodyPath.append(self.computeBezier(curve, 0.002))
    elif self.curveType == 'L':
      self.baseBodyPath = self.computeLinearBody(self.anchors, 0.002)
    elif self.curveType == 'P':
      anchors = self.anchors
      coordBottom = 2*((anchors[0]['x'] * (anchors[1]['y'] - anchors[2]['y'])) + (anchors[1]['x'] * (anchors[2]['y'] - anchors[0]['y'])) + (anchors[2]['x'] * (anchors[0]['y'] - anchors[1]['y'])))

      if coordBottom == 0:
        self.curveType = 'L'
        self.baseBodyPath = self.computeLinearBody(self.anchors, 0.002)
      else:
        self.baseBodyPath = self.computeCircleBody(self.anchors)

    # maybe I should reparameterize the body path before this #
    self.calcLength = 0
    self.snappedBaseBody = []
    if not self.curveType == 'B':
      self.snappedBaseBody = [self.baseBodyPath[0]]
      for i in range(1, len(self.baseBodyPath) - 1):
        p1 = self.baseBodyPath[i-1]
        p2 = self.baseBodyPath[i]
        self.calcLength += dist(p1['x'], p1['y'], p2['x'], p2['y'])

        if self.calcLength <= self.length:
          self.snappedBaseBody.append(p1)
        else: break
    else:
      for curve in self.baseBodyPath:
        self.snappedBaseBody.append([curve[0]])

        for i in range(1, len(curve) - 1):
          p1 = curve[i-1]
          p2 = curve[i]
          self.calcLength += dist(p1['x'], p1['y'], p2['x'], p2['y'])

          if self.calcLength <= self.length:
            self.snappedBaseBody[-1].append(p1)
          else: break

    del self.baseBodyPath
    self.baseBodyPath = self.snappedBaseBody

    if self.curveType == 'B':
      if self.slides % 2 == 0:
        self.endX = self.baseBodyPath[0][0]['x']
        self.endY = self.baseBodyPath[0][0]['y']
      else:
        self.endX = self.baseBodyPath[-1][-1]['x']
        self.endY = self.baseBodyPath[-1][-1]['y']
    else:
      if self.slides % 2 == 0:
        self.endX = self.baseBodyPath[0]['x']
        self.endY = self.baseBodyPath[0]['y']
      else:
        self.endX = self.baseBodyPath[-1]['x']
        self.endY = self.baseBodyPath[-1]['y']

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

  def computeCircleBody(self, anchors: list):
    calculatedPoints = []

    if not len(anchors) == 3 and sharedWindow.window.customData['debug']:
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

    radianInterval = 1 / bodyCircleRadius

    startAngle = math.atan2(anchors[0]['y'] - bodyCircleMidpoint['y'],anchors[0]['x'] - bodyCircleMidpoint['x'])
    middleAngle = math.atan2(anchors[1]['y'] - bodyCircleMidpoint['y'],anchors[1]['x'] - bodyCircleMidpoint['x'])
    endAngle = math.atan2(anchors[2]['y'] - bodyCircleMidpoint['y'], anchors[2]['x'] - bodyCircleMidpoint['x'])

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

  def transformBodyPath(self, resMultiplier: numType, resPadding: numType):
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

      ## don't think this is still good enough... but it's fine for now ##
      lastDistance = 0
      self.bodyPath = []
      self.bodyPath.append(self.transformedBodyPath[0])
      targetDistance = 2
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

  def renderBody(self, renderResMultiplier: numType, highQualitySliders: bool):
    highResMultiplier = 2

    CR = self.beatmap.circleRadius * renderResMultiplier
    highResCR = CR * highResMultiplier

    translatedBodyPath = []

    minX = minY = maxX = maxY = 0
    for point in self.bodyPath:
      minX = min(minX, point['x'] - CR)
      maxX = max(maxX, point['x'] + CR)
      minY = min(minY, point['y'] - CR)
      maxY = max(maxY, point['y'] + CR)

    bodySize = (maxX - minX, maxY - minY)

    highResSize = (bodySize[0] * highResMultiplier, bodySize[1] * highResMultiplier)

    highResBodySurface = pg.surface.Surface(highResSize, flags=pg.SRCALPHA)

    translatedBodyPath = [
      {
        'x': (point['x'] - minX) * highResMultiplier,
        'y': (point['y'] - minY) * highResMultiplier
      } for point in self.bodyPath
    ]

    self.bodySurfacePos = (minX, minY)
    highResBodySurface.fill((0, 0, 0, 0))

    sliderOutlineAlpha = 180
    sliderOutlineSize = .15
    totalAlphaIterations = int(highResCR * (1 - sliderOutlineSize))

    for point in translatedBodyPath:
      pg.draw.circle(highResBodySurface, (255, 255, 255, sliderOutlineAlpha), (point['x'], point['y']), highResCR)

    if highQualitySliders:
      maxAlpha = 80
      minAlpha = 10

      for i in range(totalAlphaIterations):
        alpha = mapRange(i, 0, totalAlphaIterations, minAlpha, maxAlpha)
        radius = totalAlphaIterations - i

        for point in translatedBodyPath:
          pg.draw.circle(highResBodySurface, (255, 255, 255, alpha), (point['x'], point['y']), radius)
    else:
      for point in translatedBodyPath:
        pg.draw.circle(highResBodySurface, (255, 255, 255, 15), (point['x'], point['y']), totalAlphaIterations)

    self.bodySurface = pg.transform.smoothscale(highResBodySurface, bodySize)

class Spinner:
  def __init__(self, objectDict: dict, map):
    self.rawDict = objectDict
    self.map = map
    self.time = self.rawDict['time']
    self.endTime = self.rawDict['endTime']
    self.comboIndex = 0
    self.comboColorIndex = 0
