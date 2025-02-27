from typing import Union
from math import atan2
import pygame as pg
from modules.misc.helpers import mapRange
from modules.beatmapElements.hitobjects import Hitcircle, Slider, Spinner
from modules.beatmapElements.beatmap import Beatmap

class MapRenderer:
  def __init__(self, beatmapURL: dict, skinURL: str, surface: pg.Surface, playFieldResMultiplier: Union[int, float]):
    self.beatmap = Beatmap(beatmapURL, skinURL)
    self.surface = surface
    self.playFieldResMultiplier = playFieldResMultiplier
    self.playFieldRes = (self.playFieldResMultiplier * 512, self.playFieldResMultiplier * 384)
    self.playFieldXpadding = (self.surface.get_width() - self.playFieldRes[0]) / 2
    self.playFieldYpadding = (self.surface.get_height() - self.playFieldRes[1]) / 2

    for slider in self.beatmap.sliders:
      slider.transformBodyPath((self.playFieldResMultiplier, self.playFieldResMultiplier), (self.playFieldXpadding, self.playFieldYpadding))
      slider.renderBody()

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

    if hitcircle.time >= time:
      approachCircleMultiplier = self.playFieldResMultiplier * mapRange(time, drawWindowStart, hitcircle.time, 3, 1)
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

    hitcircleScaled = pg.transform.smoothscale_by(hitcircleImage, self.playFieldResMultiplier * hitcircleMultiplier)
    hitcircleOverlayScaled = pg.transform.smoothscale_by(hitcircleOverlayImage, self.playFieldResMultiplier * hitcircleMultiplier)

    hitcircleScaled.set_alpha(hitobjectAlpha)
    hitcircleOverlayScaled.set_alpha(hitobjectAlpha)

    hitcirclePos = ((hitcircle.x * self.playFieldResMultiplier) - (hitcircleScaled.get_width() / 2) + self.playFieldXpadding, (hitcircle.y * self.playFieldResMultiplier) - (hitcircleScaled.get_height() / 2) + self.playFieldYpadding)
    hitcircleOverlayPos = ((hitcircle.x * self.playFieldResMultiplier) - (hitcircleOverlayScaled.get_width() / 2) + self.playFieldXpadding, (hitcircle.y * self.playFieldResMultiplier) - (hitcircleOverlayScaled.get_height() / 2) + self.playFieldYpadding)

    self.surface.blit(hitcircleScaled, hitcirclePos)

    if hitcircle.hit >= time:
      comboImagesScaled = [pg.transform.smoothscale_by(comboImage, self.beatmap.elementsScaleMultiplier * self.playFieldResMultiplier) for comboImage in comboImages]
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
      approachCirclePos = ((hitcircle.x * self.playFieldResMultiplier) - (approachcircleScaled.get_width() / 2) + self.playFieldXpadding, (hitcircle.y * self.playFieldResMultiplier) - (approachcircleScaled.get_height() / 2) + self.playFieldYpadding)
      self.surface.blit(approachcircleScaled, approachCirclePos)

    self.surface.blit(hitcircleOverlayScaled, hitcircleOverlayPos)

  def drawSlider(self, slider: Slider, time: int):
    if slider.curveType == 'L' or slider.curveType == 'B' or slider.curveType == 'P':
      self.surface.blit(slider.bodySurface, slider.bodySurfacePos)

      if time >= slider.time and time <= slider.time + (slider.slideTime * slider.slides):
        # pointPos = (int(mapRange(time, slider.time, slider.time + (slider.slideTime * slider.slides), 0, len(slider.bodyPath) - 1)) * slider.slides) % len(slider.bodyPath)

        slide = mapRange(time, slider.time, slider.time + slider.slideTime * slider.slides, 1, slider.slides + 1)
        pointPos = int(abs((slide % 2) - 1) * (len(slider.bodyPath) - 1))

        sliderBall = self.beatmap.sliderBallCombos[slider.comboColorIndex]
        sliderBallScaled = pg.transform.smoothscale_by(sliderBall, self.playFieldResMultiplier)
        sliderBallPos = (slider.bodyPath[pointPos]['x'] - (sliderBallScaled.get_width() / 2), slider.bodyPath[pointPos]['y'] - (sliderBallScaled.get_height() / 2))

        sliderFollowCircle = self.beatmap.skin['elements']['sliderfollowcircle']
        sliderFollowCircleScaled = pg.transform.smoothscale_by(sliderFollowCircle, self.beatmap.elementsScaleMultiplier * self.playFieldResMultiplier)
        sliderFollowCirclePos = (slider.bodyPath[pointPos]['x'] - (sliderFollowCircleScaled.get_width() / 2), slider.bodyPath[pointPos]['y'] - (sliderFollowCircleScaled.get_height() / 2))

        self.surface.blit(sliderBallScaled, sliderBallPos)
        self.surface.blit(sliderFollowCircleScaled, sliderFollowCirclePos)

    if slider.curveType == 'P':
      pg.draw.circle(self.surface, (255, 0, 0), ((slider.centerX * self.playFieldResMultiplier) + self.playFieldXpadding, (slider.centerY * self.playFieldResMultiplier) + self.playFieldYpadding), 5)

    # else:
    #   circleCenterScaled = ((slider.centerX * self.playFieldResMultiplier) + self.playFieldXpadding, (slider.centerY * self.playFieldResMultiplier) + self.playFieldYpadding)
    #   circleRadScaled = slider.radius * self.playFieldResMultiplier

    #   anchorsScaled = [
    #     {
    #       'x': (anchor['x'] * self.playFieldResMultiplier) + self.playFieldXpadding,
    #       'y': (anchor['y'] * self.playFieldResMultiplier) + self.playFieldYpadding
    #     } for anchor in slider.anchors
    #   ]

    #   elipseRect = (
    #     (circleCenterScaled[0] - circleRadScaled, circleCenterScaled[1] - circleRadScaled),
    #     (circleRadScaled * 2, circleRadScaled * 2)
    #   )

    #   startAngle = atan2(anchorsScaled[2]['y'] - circleCenterScaled[1], anchorsScaled[2]['x'] - circleCenterScaled[0])
    #   stopAngle = atan2(anchorsScaled[0]['y'] - circleCenterScaled[1], anchorsScaled[0]['x'] - circleCenterScaled[1])

      # pg.draw.rect(self.surface, (255, 0, 0), elipseRect)

      # pg.draw.arc(self.surface, (255, 255, 255), elipseRect, startAngle, stopAngle, 1)
      # pg.draw.circle(self.surface, (0, 255, 0), circleCenterScaled, slider.radius, 1)

    for i in range(slider.totalAnchors):
      currentAnchor = slider.anchors[i]
      currentAnchorPos = ((currentAnchor['x'] * self.playFieldResMultiplier) + self.playFieldXpadding, (currentAnchor['y'] * self.playFieldResMultiplier) + self.playFieldYpadding)

      if currentAnchor['red']:
        col = (255, 0, 0)
      else:
        col = (255, 255, 255)

      pg.draw.circle(self.surface, col, currentAnchorPos, 2)

      if i != 0:
        lastAnchorPos = ((slider.anchors[i-1]['x'] * self.playFieldResMultiplier) + self.playFieldXpadding, (slider.anchors[i-1]['y'] * self.playFieldResMultiplier) + self.playFieldYpadding)
        pg.draw.line(self.surface, (255, 255, 255), lastAnchorPos, currentAnchorPos, 1)

    self.drawHitcircle(slider.head, time)

  def drawSpinner(self, spinner: Spinner, time: int):
    ## WIP ##
    center = (self.playFieldXpadding + (self.playFieldRes[0] / 2), self.playFieldYpadding + (self.playFieldRes[1] / 2))

    pg.draw.circle(self.surface, (255, 255, 255), center, 5, 1)
    pg.draw.circle(self.surface, (255, 255, 255), center, self.playFieldRes[1] / 3, 1)
