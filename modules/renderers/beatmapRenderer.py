from typing import Union
import pygame as pg
from modules.misc.helpers import mapRange
from modules.beatmapElements.hitobjects import Hitcircle, Slider, Spinner
from modules.beatmapElements.beatmap import Beatmap

class MapRenderer:
  def __init__(self, beatmapURL: dict, skinURL: str, surface: pg.Surface, playFielsResMultiplier: Union[int, float]):
    self.beatmap = Beatmap(beatmapURL, skinURL)
    self.surface = surface
    self.playFielsResMultiplier = playFielsResMultiplier
    self.playFieldRes = (self.playFielsResMultiplier * 512, self.playFielsResMultiplier * 384)
    self.playFieldXpadding = (self.surface.get_width() - self.playFieldRes[0]) / 2
    self.playFieldYpadding = (self.surface.get_height() - self.playFieldRes[1]) / 2

  def render(self, time: int):
    renderObjects = self.beatmap.hitObjectsAtTime(time)

    self.surface.fill((0, 0, 0))
    pg.draw.rect(self.surface, (255, 255, 255), (self.playFieldXpadding, self.playFieldYpadding, self.playFieldRes[0], self.playFieldRes[1]), 1)

    for i in range(len(renderObjects) - 1, -1, -1):
      if isinstance(renderObjects[i], Hitcircle):
        self.drawHitcircle(renderObjects[i], time)
      elif (renderObjects[i], Slider):
        self.drawSlider(renderObjects[i], time)
      elif (renderObjects[i], Spinner):
        self.drawSpinner(renderObjects[i], time)

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
      comboImagesScaled = [pg.transform.smoothscale_by(comboImage, self.beatmap.elementsScaleMultiplier) for comboImage in comboImages]
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
    pass

  def drawSpinner(self, spinner: Spinner, time: int):
    pass
