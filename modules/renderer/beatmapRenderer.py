from typing import Union, Optional
import pygame as pg
from modules.misc.helpers import mapRange
from modules.beatmapElements.hitobjects import Hitcircle, Slider, Spinner
from modules.beatmapElements.beatmap import Beatmap

class MapRenderer:
  def __init__(self, osuURL: str, beatmapURL: dict, skinName: str, replayURL: Optional[str], surface: pg.Surface, playFieldResMultiplier: Union[int, float]):
    # print('creating a new renderer...')
    if replayURL is not None:
      # print('initializing beatmap with replay...')
      self.beatmap = Beatmap(osuURL, beatmapURL, skinName, replayURL)
      # print('initializing beatmap done.')
    else:
      self.beatmap = Beatmap(osuURL, beatmapURL, skinName)

    self.surface = surface
    self.playFieldResMultiplier = playFieldResMultiplier
    self.playFieldRes = (self.playFieldResMultiplier * 512, self.playFieldResMultiplier * 384)
    self.playFieldXpadding = (self.surface.get_width() - self.playFieldRes[0]) / 2
    self.playFieldYpadding = (self.surface.get_height() - self.playFieldRes[1]) / 2
    self.drawSliderAnchors = False

    # print('transforming and rendering slider bodies...')
    for slider in self.beatmap.sliders:
      slider.transformBodyPath((self.playFieldResMultiplier, self.playFieldResMultiplier), (self.playFieldXpadding, self.playFieldYpadding))
      slider.renderBody()
    # print('done.')

  def updateSurface(self, newSurface: pg.Surface, newResMultiplier: Union[int, float]):
    self.surface = newSurface
    self.playFieldResMultiplier = newResMultiplier
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

    if self.beatmap.mode == 'replay':
      self.drawCursor(time)

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
    self.surface.blit(slider.bodySurface, slider.bodySurfacePos)

    if time >= slider.time and time <= slider.time + (slider.slideTime * slider.slides):
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

    if self.drawSliderAnchors:
      for i in range(len(slider.anchors)):
        anchor = slider.anchors[i]
        anchorColor = (255, 0, 0) if anchor['red'] else (255, 255, 255)
        anchorPos = (anchor['x'] * self.playFieldResMultiplier + self.playFieldXpadding, anchor['y'] * self.playFieldResMultiplier + self.playFieldYpadding)
        pg.draw.circle(self.surface, anchorColor, anchorPos, 3)
        if i > 0:
          pg.draw.line(self.surface, (255, 255, 255), (slider.anchors[i - 1]['x'] * self.playFieldResMultiplier + self.playFieldXpadding, slider.anchors[i - 1]['y'] * self.playFieldResMultiplier + self.playFieldYpadding), anchorPos, 1)

    self.drawHitcircle(slider.head, time)

  def drawSpinner(self, spinner: Spinner, time: int):
    ## WIP ##
    center = (self.playFieldXpadding + (self.playFieldRes[0] / 2), self.playFieldYpadding + (self.playFieldRes[1] / 2))

    pg.draw.circle(self.surface, (255, 255, 255), center, 5, 1)
    pg.draw.circle(self.surface, (255, 255, 255), center, self.playFieldRes[1] / 3, 1)

  def drawCursor(self, time: int, trailType: str = 'default'):
    if trailType not in ['default', 'connected']:
      raise ValueError('Invalid trail type')

    trailLength = 10
    cursorTrail = self.beatmap.getCursorTrailAtTime(time, trailLength)

    if len(cursorTrail) == 0:
      return None

    cursorImg = self.beatmap.cursor
    cursorTrailImg = self.beatmap.cursorTrail

    cursorScaled = pg.transform.smoothscale_by(cursorImg, self.playFieldResMultiplier)
    cursorTrailScaled = pg.transform.smoothscale_by(cursorTrailImg, self.playFieldResMultiplier)

    for i in range(len(cursorTrail) - 1):
      if trailType == 'connected':
        pg.draw.line(self.surface, (255, 255, 255), (cursorTrail[i]['x'] + self.playFieldXpadding, cursorTrail[i]['y'] + self.playFieldYpadding), (cursorTrail[i + 1]['x'] + self.playFieldXpadding, cursorTrail[i + 1]['y'] + self.playFieldYpadding), 1)
      else:
        trailAlpha = mapRange(i, 0, trailLength, 0, 255)
        cursorTrailScaled.set_alpha(trailAlpha)
        self.surface.blit(cursorTrailScaled, ((cursorTrail[i]['x'] - (cursorTrailScaled.get_width() / 2)) + self.playFieldXpadding, (cursorTrail[i]['y'] - (cursorTrailScaled.get_height() / 2)) + self.playFieldYpadding))

    self.surface.blit(cursorScaled, ((cursorTrail[-1]['x'] - (cursorScaled.get_width() / 2)) + self.playFieldXpadding, (cursorTrail[-1]['y'] - (cursorScaled.get_height() / 2) + self.playFieldYpadding)))
