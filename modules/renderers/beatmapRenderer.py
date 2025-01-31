from copy import deepcopy
from typing import Union, List, Dict
import pygame as pg
from modules.misc.helpers import mapRange
from modules.beatmapElements.hitobjects import Hitcircle, Slider, Spinner
from modules.beatmapElements.beatmap import Beatmap

numType = Union[int, float]

def lerp(anchor1: Dict[str, numType], anchor2: Dict[str, numType], t: numType) -> Dict[str, numType]:
  return {
    'x': anchor1['x'] + t * (anchor2['x'] - anchor1['x']),
    'y': anchor1['y'] + t * (anchor2['y'] - anchor1['y'])
  }

def computeBezier(anchors: list, tInterval: numType) -> List[Dict[str, numType]]:
  calculatedPoints = []

  interpolatedAnchors = deepcopy(anchors)

  t = 0
  while (t <= 1):
    interpolatedAnchors = deepcopy(anchors)
    for _ in range(len(interpolatedAnchors) - 1):
      tmpAnchors = []
      for j in range(len(interpolatedAnchors) - 1):
        tmpAnchors.append(lerp(interpolatedAnchors[j], interpolatedAnchors[j+1], t))

      interpolatedAnchors = deepcopy(tmpAnchors)

    calculatedPoints.append(deepcopy(interpolatedAnchors[0]))

    t += tInterval

  return calculatedPoints

class MapRenderer:
  def __init__(self, beatmapURL: dict, skinURL: str, surface: pg.Surface, playFielsResMultiplier: Union[int, float]):
    self.beatmap = Beatmap(beatmapURL, skinURL)
    self.surface = surface
    self.playFielsResMultiplier = playFielsResMultiplier
    self.playFieldRes = (self.playFielsResMultiplier * 512, self.playFielsResMultiplier * 384)
    self.playFieldXpadding = (self.surface.get_width() - self.playFieldRes[0]) / 2
    self.playFieldYpadding = (self.surface.get_height() - self.playFieldRes[1]) / 2

    self.precomputeBezier()

  def precomputeBezier(self):
    for slider in self.beatmap.sliders:
      if slider.curveType == 'B':
        for curve in slider.curves:
          newCurve = [
            {
              'x': (point['x'] * self.playFielsResMultiplier) + self.playFieldXpadding,
              'y': (point['y'] * self.playFielsResMultiplier) + self.playFieldYpadding
            } for point in curve
          ]

          slider.precomputedBezier.append(computeBezier(newCurve, 0.01))

  def render(self, time: int):
    renderObjects = self.beatmap.hitObjectsAtTime(time)

    self.surface.fill((0, 0, 0))
    pg.draw.rect(self.surface, (255, 255, 255), (self.playFieldXpadding, self.playFieldYpadding, self.playFieldRes[0], self.playFieldRes[1]), 1)

    for i in range(len(renderObjects) - 1, -1, -1):
      if isinstance(renderObjects[i], Hitcircle): self.drawHitcircle(renderObjects[i], time)
      elif isinstance(renderObjects[i], Slider): self.drawSlider(renderObjects[i], time)
      elif isinstance(renderObjects[i], Spinner): self.drawSpinner(renderObjects[i], time)

  def drawHitcircle(self, hitcircle: Hitcircle, time: int):
    comboStr = str(hitcircle.comboIndex)
    comboLength = len(comboStr)

    hitcircleImage = self.beatmap.hitcircleCombos[hitcircle.comboColorIndex]
    comboImages = [self.beatmap.skin['elements'][f'score-{comboNumber}'] for comboNumber in comboStr]
    hitcircleOverlayImage = self.beatmap.hitcircleOverlay
    approachcircleImage = self.beatmap.approachcircleCombos[hitcircle.comboColorIndex]

    drawWindowStart = hitcircle.time - self.beatmap.preempt
    fadeWindowEnd = drawWindowStart + self.beatmap.fadeIn

    # print(f'resMultiplier: {self.resMultiplier}')

    if hitcircle.time >= time:
      approachCircleMultiplier = self.playFielsResMultiplier * mapRange(time, drawWindowStart, hitcircle.time, 3, 1)
      hitcircleMultiplier = 1
      hitobjectAlpha = mapRange(time, drawWindowStart, fadeWindowEnd, 0, 255)
    else:
      approachCircleMultiplier = 0

      if hitcircle.hit >= time:
        hitcircleMultiplier = 1
        hitobjectAlpha = 255
      else:
        hitcircleMultiplier = mapRange(time, hitcircle.hit, hitcircle.hit + self.beatmap.objectFadeout, 1, 1.5)
        hitobjectAlpha = mapRange(time, hitcircle.hit, hitcircle.hit + self.beatmap.objectFadeout, 255, 0)

    if approachCircleMultiplier < 0:
      approachCircleMultiplier = 0

    # print(f'drawWindowStart: {drawWindowStart}, fadeWindowEnd: {fadeWindowEnd}, approachCircleMultiplier: {approachCircleMultiplier}')

    hitcircleScaled = pg.transform.smoothscale_by(hitcircleImage, self.playFielsResMultiplier * hitcircleMultiplier)
    hitcircleOverlayScaled = pg.transform.smoothscale_by(hitcircleOverlayImage, self.playFielsResMultiplier * hitcircleMultiplier)

    hitcircleScaled.set_alpha(hitobjectAlpha)
    hitcircleOverlayScaled.set_alpha(hitobjectAlpha)

    hitcirclePos = ((hitcircle.x * self.playFielsResMultiplier) - (hitcircleScaled.get_width() / 2) + self.playFieldXpadding, (hitcircle.y * self.playFielsResMultiplier) - (hitcircleScaled.get_height() / 2) + self.playFieldYpadding)
    hitcircleOverlayPos = ((hitcircle.x * self.playFielsResMultiplier) - (hitcircleOverlayScaled.get_width() / 2) + self.playFieldXpadding, (hitcircle.y * self.playFielsResMultiplier) - (hitcircleOverlayScaled.get_height() / 2) + self.playFieldYpadding)

    self.surface.blit(hitcircleScaled, hitcirclePos)

    if hitcircle.hit >= time:
      comboImagesScaled = [pg.transform.smoothscale_by(comboImage, self.beatmap.elementsScaleMultiplier * self.playFielsResMultiplier) for comboImage in comboImages]
      for comboImage in comboImagesScaled:
        comboImage.set_alpha(hitobjectAlpha)
      comboWidth = comboImagesScaled[0].get_width()
      firstComboPosX = hitcirclePos[0] + ((hitcircleScaled.get_width() - (comboWidth * comboLength)) / 2)
      comboPosY = hitcirclePos[1] + ((hitcircleScaled.get_height() - comboImagesScaled[0].get_height()) / 2)
      comboPosesX = [firstComboPosX + (comboWidth * i) for i in range(comboLength)]

      for i in range(comboLength):
        self.surface.blit(comboImagesScaled[i], (comboPosesX[i], comboPosY))

    if hitcircle.time >= time:
      approachcircleScaled = pg.transform.smoothscale_by(approachcircleImage, approachCircleMultiplier)
      approachcircleScaled.set_alpha(hitobjectAlpha)
      approachCirclePos = ((hitcircle.x * self.playFielsResMultiplier) - (approachcircleScaled.get_width() / 2) + self.playFieldXpadding, (hitcircle.y * self.playFielsResMultiplier) - (approachcircleScaled.get_height() / 2) + self.playFieldYpadding)
      self.surface.blit(approachcircleScaled, approachCirclePos)

    self.surface.blit(hitcircleOverlayScaled, hitcircleOverlayPos)

  def drawSlider(self, slider: Slider, time: int):
    if slider.curveType == 'L':
      for curve in slider.curves:
        pg.draw.line(self.surface, (255, 0, 0), ((curve[0]['x'] * self.playFielsResMultiplier) + self.playFieldXpadding, (curve[0]['y'] * self.playFielsResMultiplier) + self.playFieldYpadding), ((curve[1]['x'] * self.playFielsResMultiplier) + self.playFieldXpadding, (curve[1]['y'] * self.playFielsResMultiplier) + self.playFieldYpadding), 1)
    elif slider.curveType == 'B':
      # for curve in slider.precomputedBezier:
      #   for i in range(len(curve) - 1):
      #     pg.draw.line(self.surface, (0, 0, 255), (curve[i]['x'], curve[i]['y']), (curve[i+1]['x'], curve[i+1]['y']), 1)
      for curve in slider.precomputedBezier:
        for point in curve:
          pg.draw.circle(self.surface, (255, 255, 255, 128), (point['x'], point['y']), (self.beatmap.circleRadius * self.playFielsResMultiplier) * .8)
    else:
      for i in range(1, len(slider.anchors)):
        pg.draw.line(self.surface, (0, 255, 0), ((slider.anchors[i-1]['x'] * self.playFielsResMultiplier) + self.playFieldXpadding, (slider.anchors[i-1]['y'] * self.playFielsResMultiplier) + self.playFieldYpadding), ((slider.anchors[i]['x'] * self.playFielsResMultiplier) + self.playFieldXpadding, (slider.anchors[i]['y'] * self.playFielsResMultiplier) + self.playFieldYpadding), 1)

    self.drawHitcircle(slider.head, time)

  def drawSpinner(self, spinner: Spinner, time: int):
    center = (self.playFieldXpadding + (self.playFieldRes[0] / 2), self.playFieldYpadding + (self.playFieldRes[1] / 2))

    pg.draw.circle(self.surface, (255, 255, 255), center, 5, 1)
    pg.draw.circle(self.surface, (255, 255, 255), center, self.playFieldRes[1] / 3, 1)
