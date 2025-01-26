# from typing import List
import pygame as pg
from modules.misc.helpers import mapRange
from modules.beatmapElements.hitobjects import Hitcircle, Slider, Spinner
from modules.beatmapElements.beatmap import Beatmap

class MapRenderer:
  def __init__(self, beatmapURL: dict, skinURL: str, resMultiplier: int):
    self.beatmap = Beatmap(beatmapURL, skinURL)
    self.resMultiplier = resMultiplier
    self.surface = pg.Surface((self.resMultiplier * 512, self.resMultiplier * 384))

  def render(self, time: int):
    self.surface.fill((0, 0, 0))

    renderObjects = self.beatmap.hitObjectsAtTime(time)

    for i in range(len(renderObjects) - 1, -1, -1):
      if isinstance(renderObjects[i], Hitcircle):
        self.drawHitcircle(renderObjects[i], time)
      elif (renderObjects[i], Slider):
        self.drawSlider(renderObjects[i], time)
      elif (renderObjects[i], Spinner):
        self.drawSpinner(renderObjects[i], time)

    return self.surface

  def drawHitcircle(self, hitcircle: Hitcircle, time: int):
    comboStr = str(hitcircle.comboIndex)
    # comboLength = len(comboStr)

    hitcircleImage = self.beatmap.hitcircleCombos[hitcircle.comboColorIndex]
    comboImages = [self.beatmap.skin['elements'][f'combo-{comboNumber}'] for comboNumber in comboStr]
    hitcircleOverlayImage = self.beatmap.hitcircleOverlay
    approachcircleImage = self.beatmap.approachcircleCombos[hitcircle.comboColorIndex]

    drawWindowStart = hitcircle.time - self.beatmap.preempt
    fadeWindowEnd = drawWindowStart + self.beatmap.fadeIn

    # print(f'resMultiplier: {self.resMultiplier}')

    approachCircleMultiplier = self.resMultiplier * mapRange(time, drawWindowStart, hitcircle.time, 3, 1)
    
    if approachCircleMultiplier < 0:
      approachCircleMultiplier = 0

    # print(f'drawWindowStart: {drawWindowStart}, fadeWindowEnd: {fadeWindowEnd}, approachCircleMultiplier: {approachCircleMultiplier}')

    hitcircleDraw = pg.transform.smoothscale_by(hitcircleImage, self.resMultiplier)
    comboImagesDraw = [pg.transform.smoothscale_by(comboImage, self.beatmap.elementsScaleMultiplier * 2) for comboImage in comboImages]
    hitcircleOverlayDraw = pg.transform.smoothscale_by(hitcircleOverlayImage, self.resMultiplier)
    approachCircleDraw = pg.transform.smoothscale_by(approachcircleImage, approachCircleMultiplier)
    approachCircleDraw.set_alpha(mapRange(time, drawWindowStart, fadeWindowEnd, 0, 255))

    hitcirclePos = ((hitcircle.x * self.resMultiplier) - (hitcircleDraw.get_width() / 2), (hitcircle.y * self.resMultiplier) - (hitcircleDraw.get_height() / 2))
    hitcircleOverlayPos = ((hitcircle.x * self.resMultiplier) - (hitcircleOverlayDraw.get_width() / 2), (hitcircle.y * self.resMultiplier) - (hitcircleOverlayDraw.get_height() / 2))
    approachCirclePos = ((hitcircle.x * self.resMultiplier) - (approachCircleDraw.get_width() / 2), (hitcircle.y * self.resMultiplier) - (approachCircleDraw.get_height() / 2))

    self.surface.blit(hitcircleDraw, hitcirclePos)
    self.surface.blit(hitcircleOverlayDraw, hitcircleOverlayPos)
    self.surface.blit(approachCircleDraw, approachCirclePos)

  def drawSlider(self, slider: Slider, time: int):
    pass
  
  def drawSpinner(self, spinner: Spinner, time: int):
    pass
