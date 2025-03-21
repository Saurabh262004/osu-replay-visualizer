from typing import Union, Optional, List
from concurrent.futures import ThreadPoolExecutor
from math import atan2, degrees
import pygame as pg
import sharedWindow
from modules.misc.helpers import mapRange
from modules.beatmapElements.hitobjects import Hitcircle, Slider, Spinner
from modules.beatmapElements.beatmap import Beatmap

numType = Union[int, float]

class MapRenderer:
  def __init__(self, beatmapURL: dict, replayURL: Optional[str], surface: pg.Surface, playFieldResMultiplier: numType):
    self.window = sharedWindow.window
    self.userData = self.window.customData['userData']

    # print('creating a new renderer...')
    if replayURL is not None:
      # print('initializing beatmap with replay...')
      self.beatmap = Beatmap(beatmapURL, self.window.customData['skin'], replayURL)
      # print('initializing beatmap done.')
    else:
      self.beatmap = Beatmap(beatmapURL, self.window.customData['skin'])

    self.surface = surface
    self.playFieldResMultiplier = playFieldResMultiplier
    self.playFieldRes = (self.playFieldResMultiplier * 512, self.playFieldResMultiplier * 384)
    self.playFieldXpadding = (self.surface.get_width() - self.playFieldRes[0]) / 2
    self.playFieldYpadding = (self.surface.get_height() - self.playFieldRes[1]) / 2
    self.maxImgAlpha = 255

    self.center = (
      self.playFieldXpadding + (self.playFieldRes[0] / 2),
      self.playFieldYpadding + (self.playFieldRes[1] / 2)
    )

    self.cursorScaled = pg.transform.smoothscale_by(self.beatmap.cursor, self.playFieldResMultiplier)
    self.cursorScaledHalfWidth = (self.cursorScaled.get_width() / 2)
    self.cursorScaledHalfHeight = (self.cursorScaled.get_height() / 2)

    self.cursorTrailScaled = pg.transform.smoothscale_by(self.beatmap.cursorTrail, self.playFieldResMultiplier)
    self.cursorTrailScaledHalfWidth = (self.cursorTrailScaled.get_width() / 2)
    self.cursorTrailScaledHalfHeight = (self.cursorTrailScaled.get_height() / 2)

    self.beatmap.transformCursorData(self.playFieldResMultiplier, self.playFieldXpadding, self.playFieldYpadding)

    with ThreadPoolExecutor() as executor:
      transforms = [
          executor.submit(
          slider.transformBodyPath,
          (self.playFieldResMultiplier, self.playFieldResMultiplier),
          (self.playFieldXpadding, self.playFieldYpadding)
        ) for slider in self.beatmap.sliders
      ]

      [t.result() for t in transforms]

      renders = [
        executor.submit(
          slider.renderBody,
          self.playFieldResMultiplier,
          self.userData['highQualitySliders']
        ) for slider in self.beatmap.sliders
      ]

      [r.result() for r in renders]

    # print('post-render')
  def updateSurface(self, newSurface: pg.Surface, newResMultiplier: numType):
    self.surface = newSurface
    self.playFieldResMultiplier = newResMultiplier
    self.playFieldRes = (self.playFieldResMultiplier * 512, self.playFieldResMultiplier * 384)
    self.playFieldXpadding = (self.surface.get_width() - self.playFieldRes[0]) / 2
    self.playFieldYpadding = (self.surface.get_height() - self.playFieldRes[1]) / 2

    self.center = (
      self.playFieldXpadding + (self.playFieldRes[0] / 2),
      self.playFieldYpadding + (self.playFieldRes[1] / 2)
    )

    self.cursorScaled = pg.transform.smoothscale_by(self.beatmap.cursor, self.playFieldResMultiplier)
    self.cursorScaledHalfWidth = (self.cursorScaled.get_width() / 2)
    self.cursorScaledHalfHeight = (self.cursorScaled.get_height() / 2)

    self.cursorTrailScaled = pg.transform.smoothscale_by(self.beatmap.cursorTrail, self.playFieldResMultiplier)
    self.cursorTrailScaledHalfWidth = (self.cursorTrailScaled.get_width() / 2)
    self.cursorTrailScaledHalfHeight = (self.cursorTrailScaled.get_height() / 2)

    self.beatmap.transformCursorData(self.playFieldResMultiplier, self.playFieldXpadding, self.playFieldYpadding)

    with ThreadPoolExecutor() as executor:
      transforms = [
          executor.submit(
          slider.transformBodyPath,
          (self.playFieldResMultiplier, self.playFieldResMultiplier),
          (self.playFieldXpadding, self.playFieldYpadding)
        ) for slider in self.beatmap.sliders
      ]

      [t.result() for t in transforms]

      renders = [
        executor.submit(
          slider.renderBody,
          self.playFieldResMultiplier,
          self.userData['highQualitySliders']
        ) for slider in self.beatmap.sliders
      ]

      [r.result() for r in renders]

  def render(self, time: int):
    renderObjects = self.beatmap.hitobjectsAtTime(time)

    self.surface.fill((0, 0, 0))

    if self.userData['playfieldBorder']:
      pg.draw.rect(self.surface, (200, 200, 200), (self.playFieldXpadding, self.playFieldYpadding, self.playFieldRes[0], self.playFieldRes[1]), 1)

      pg.draw.line(
        self.surface,
        (200, 200, 200),
        (self.playFieldXpadding + (self.playFieldRes[0] / 2), self.playFieldYpadding),
        (self.playFieldXpadding + (self.playFieldRes[0] / 2), self.playFieldYpadding + self.playFieldRes[1]),
        1
      )

      pg.draw.line(
        self.surface,
        (200, 200, 200),
        (self.playFieldXpadding, self.playFieldYpadding + (self.playFieldRes[1] / 2)),
        (self.playFieldXpadding + self.playFieldRes[0], self.playFieldYpadding + (self.playFieldRes[1] / 2)),
        1
      )

    for i in range(len(renderObjects) - 1, -1, -1):
      if isinstance(renderObjects[i], Hitcircle): self.drawHitcircle(renderObjects[i], time)
      elif isinstance(renderObjects[i], Slider): self.drawSlider(renderObjects[i], time)
      elif isinstance(renderObjects[i], Spinner): self.drawSpinner(renderObjects[i], time)

    if self.beatmap.mode == 'replay':
      trails = []

      if self.userData['renerCursorTracker']:
        trails.append('connected')
      if self.userData['renderSkinCursor']:
        trails.append('default')

      self.drawCursor(time, trails)

      if self.userData['renderKeyOverlay']:
        self.drawKeyOverlay(time)

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
      approachCircleMultiplier = self.playFieldResMultiplier * mapRange(time, drawWindowStart, hitcircle.time, 4, 1)
      hitcircleMultiplier = 1
      hitobjectAlpha = mapRange(time, drawWindowStart, fadeWindowEnd, 0, self.maxImgAlpha)
    else:
      approachCircleMultiplier = 0

      if hitcircle.hitTime >= time:
        hitcircleMultiplier = 1
        hitobjectAlpha = self.maxImgAlpha
      else:
        hitcircleMultiplier = mapRange(time, hitcircle.hitTime, hitcircle.hitTime + self.beatmap.objectFadeout, 1, 1.5)
        hitobjectAlpha = mapRange(time, hitcircle.hitTime, hitcircle.hitTime + self.beatmap.objectFadeout, self.maxImgAlpha, 0)

    if approachCircleMultiplier < 0:
      approachCircleMultiplier = 0

    hitcircleScaled = pg.transform.smoothscale_by(hitcircleImage, self.playFieldResMultiplier * hitcircleMultiplier)
    hitcircleOverlayScaled = pg.transform.smoothscale_by(hitcircleOverlayImage, self.playFieldResMultiplier * hitcircleMultiplier)

    hitcircleScaled.set_alpha(hitobjectAlpha)
    hitcircleOverlayScaled.set_alpha(hitobjectAlpha)

    hitcirclePos = (
      ((hitcircle.x - hitcircle.stackOffset) * self.playFieldResMultiplier) + self.playFieldXpadding,
      ((hitcircle.y - hitcircle.stackOffset) * self.playFieldResMultiplier) + self.playFieldYpadding
    )

    hitcircleImgPos = (
      hitcirclePos[0] - (hitcircleScaled.get_width() / 2),
      hitcirclePos[1] - (hitcircleScaled.get_height() / 2)
    )

    hitcircleOverlayPos = (
      hitcirclePos[0] - (hitcircleOverlayScaled.get_width() / 2),
      hitcirclePos[1] - (hitcircleOverlayScaled.get_height() / 2)
    )

    self.surface.blit(hitcircleScaled, hitcircleImgPos)

    if hitcircle.hitTime >= time:
      comboImagesScaled = [pg.transform.smoothscale_by(comboImage, self.beatmap.elementsScaleMultiplier * self.playFieldResMultiplier) for comboImage in comboImages]
      # comboImagesScaled = [pg.transform.smoothscale_by(comboImage, self.playFieldResMultiplier) for comboImage in comboImages]

      for comboImage in comboImagesScaled:
        comboImage.set_alpha(hitobjectAlpha)

      comboWidth = comboImagesScaled[0].get_width()

      firstComboPosX = hitcircleImgPos[0] + ((hitcircleScaled.get_width() - (comboWidth * comboLength)) / 2)
      comboPosesX = [firstComboPosX + (comboWidth * i) for i in range(comboLength)]

      comboPosY = hitcircleImgPos[1] + ((hitcircleScaled.get_height() - comboImagesScaled[0].get_height()) / 2)

      for i in range(comboLength):
        self.surface.blit(comboImagesScaled[i], (comboPosesX[i], comboPosY))

    if hitcircle.time >= time:
      approachcircleScaled = pg.transform.smoothscale_by(approachcircleImage, approachCircleMultiplier)
      approachcircleScaled.set_alpha(hitobjectAlpha)

      approachCirclePos = (
        hitcirclePos[0] - (approachcircleScaled.get_width() / 2),
        hitcirclePos[1] - (approachcircleScaled.get_height() / 2)
      )

      self.surface.blit(approachcircleScaled, approachCirclePos)

    self.surface.blit(hitcircleOverlayScaled, hitcircleOverlayPos)

    if self.userData['renderHitJudgments']:
      self.drawJudgments(hitcircle, hitcirclePos)

  def drawJudgments(self, hitcircle: Hitcircle, hitcirclePos: List[numType]):
    ## !!! WIP !!! ##
    
    if not hitcircle.judgment == -1:
      judgmentCol = (255, 255, 255)

      if hitcircle.judgment == 0:
        judgmentCol = (255, 0, 0)
      elif hitcircle.judgment == 50:
        judgmentCol = (255, 255, 0)
      elif hitcircle.judgment == 100:
        judgmentCol = (0, 255, 0)
      elif hitcircle.judgment == 300:
        judgmentCol = (0, 0, 255)

      pg.draw.circle(self.surface, judgmentCol, hitcirclePos, 5)

  def drawSlider(self, slider: Slider, time: int):
    if slider.time >= time:
      drawWindowStart = slider.time - self.beatmap.preempt
      fadeWindowEnd = drawWindowStart + self.beatmap.fadeIn
      sliderAlpha = mapRange(time, drawWindowStart, fadeWindowEnd, 0, self.maxImgAlpha)
    else:
      if slider.endTime <= time:
        sliderAlpha = mapRange(time, slider.endTime, slider.endTime + self.beatmap.objectFadeout, self.maxImgAlpha, 0)
      else:
        sliderAlpha = self.maxImgAlpha

    slider.bodySurface.set_alpha(sliderAlpha)
    
    scaledStackOffset = slider.stackOffset * self.playFieldResMultiplier

    self.surface.blit(slider.bodySurface, (slider.bodySurfacePos[0] - scaledStackOffset, slider.bodySurfacePos[1] - scaledStackOffset))

    slide = 1
    if time >= slider.time and time <= slider.endTime + self.beatmap.objectFadeout:
      if time <= slider.endTime:
        slide = mapRange(time, slider.time, slider.endTime, 1, slider.slides + 1)
        pointPos = int(abs((slide % 2) - 1) * (len(slider.bodyPath) - 1))

        sliderBall = self.beatmap.sliderBallCombos[slider.comboColorIndex]

        # temporary fix before adding animation support for in-game elements #
        if isinstance(sliderBall, list):
          sliderBall = sliderBall[0]

        sliderBallScaled = pg.transform.smoothscale_by(sliderBall, self.playFieldResMultiplier)

        sliderBallPos = (
          slider.bodyPath[pointPos]['x'] - (sliderBallScaled.get_width() / 2) - scaledStackOffset,
          slider.bodyPath[pointPos]['y'] - (sliderBallScaled.get_height() / 2) - scaledStackOffset
        )

        self.surface.blit(sliderBallScaled, sliderBallPos)
      else:
        pointPos = -(slider.slides % 2)

      sliderFollowCircle = self.beatmap.skin['elements']['sliderfollowcircle']

      sliderFollowCircleScaled = pg.transform.smoothscale_by(sliderFollowCircle, self.beatmap.elementsScaleMultiplier * self.playFieldResMultiplier)
      # sliderFollowCircleScaled = pg.transform.smoothscale_by(sliderFollowCircle, self.playFieldResMultiplier)

      alphaAndScaleMult = 1
      if time > slider.endTime:
        alphaAndScaleMult = mapRange(time, slider.endTime, slider.endTime + self.beatmap.objectFadeout, 1, 0)
      elif time < slider.time + self.beatmap.objectFadeout:
        alphaAndScaleMult = mapRange(time, slider.time, slider.time + self.beatmap.objectFadeout, 0, 1)

      if alphaAndScaleMult > 1:
        alphaAndScaleMult = 1
      elif alphaAndScaleMult < 0:
        alphaAndScaleMult = 0

      if not alphaAndScaleMult == 1:
        sliderFollowCircleScaled.set_alpha(self.maxImgAlpha * alphaAndScaleMult)
        sliderFollowCircleScaled = pg.transform.smoothscale_by(sliderFollowCircleScaled, mapRange(alphaAndScaleMult, 0, 1, .7, 1))

      sliderFollowCirclePos = (
        slider.bodyPath[pointPos]['x'] - (sliderFollowCircleScaled.get_width() / 2) - scaledStackOffset,
        slider.bodyPath[pointPos]['y'] - (sliderFollowCircleScaled.get_height() / 2) - scaledStackOffset
      )

      self.surface.blit(sliderFollowCircleScaled, sliderFollowCirclePos)

    if self.userData['sliderAnchors']:
      for i in range(len(slider.anchors)):
        anchor = slider.anchors[i]
        anchorColor = (255, 0, 0) if anchor['red'] else (255, 255, 255)

        anchorPos = (
          (anchor['x'] - scaledStackOffset) * self.playFieldResMultiplier + self.playFieldXpadding,
          (anchor['y'] - scaledStackOffset) * self.playFieldResMultiplier + self.playFieldYpadding
        )

        pg.draw.circle(self.surface, anchorColor, anchorPos, 3)

        if i > 0:
          pg.draw.line(
            self.surface,
            (255, 255, 255),
            (
              (slider.anchors[i - 1]['x'] - scaledStackOffset) * self.playFieldResMultiplier + self.playFieldXpadding,
              (slider.anchors[i - 1]['y'] - scaledStackOffset) * self.playFieldResMultiplier + self.playFieldYpadding
            ),
            anchorPos,
            1
          )

    if slider.slides > 1 and time <= slider.endTime:
      currentTimingPoints = self.beatmap.effectiveTimingPointAtTime(time)

      if len(currentTimingPoints) > 0 and (currentTimingPoints[0] is not None):
        currentUITimingPoint = currentTimingPoints[0]

        timeSinceUIPoint = (time - currentUITimingPoint['time'])

        beatLength = currentUITimingPoint['beatLength']

        currentTotalBeatsComplete = int(timeSinceUIPoint / beatLength)

        timeAtLastBeat = currentUITimingPoint['time'] + (currentTotalBeatsComplete * beatLength)

        reverseArrowSizeMultiplier = mapRange(time, timeAtLastBeat, timeAtLastBeat + beatLength, .3, 0)
      else:
        reverseArrowSizeMultiplier = 0

      currentSlide = int(slide)
      remainingSlides = slider.slides - currentSlide
      doubleArrows = (remainingSlides > 1) and (time > slider.time)

      if remainingSlides > 0:
        evenSlide = currentSlide / 2 == int(currentSlide / 2)
        if evenSlide:
          p1 = slider.bodyPath[0]
          p2 = slider.bodyPath[1]
        else:
          p1 = slider.bodyPath[-1]
          p2 = slider.bodyPath[-2]

        reverseArrow = self.beatmap.reverseArrow

        dx, dy = p2['x'] - p1['x'], p2['y'] - p1['y']

        radiansAngle = atan2(-dy, dx)
        degreesAngle = degrees(radiansAngle)

        reverseArrowNow = pg.transform.smoothscale_by(reverseArrow, (1 + reverseArrowSizeMultiplier) * self.playFieldResMultiplier)
        reverseArrowNow = pg.transform.rotate(reverseArrowNow, degreesAngle)
        reverseArrowNow.set_alpha(sliderAlpha)

        reverseArrowNowPos = (
          p1['x'] - (reverseArrowNow.get_width() / 2) - scaledStackOffset,
          p1['y'] - (reverseArrowNow.get_height() / 2) - scaledStackOffset
        )

        self.surface.blit(reverseArrowNow, reverseArrowNowPos)

        if doubleArrows:
          if evenSlide:
            p1Nxt = slider.bodyPath[-1]
            p2Nxt = slider.bodyPath[-2]
          else:
            p1Nxt = slider.bodyPath[0]
            p2Nxt = slider.bodyPath[1]

          dxNxt, dyNxt = p2Nxt['x'] - p1Nxt['x'], p2Nxt['y'] - p1Nxt['y']

          radiansAngleNxt = atan2(-dyNxt, dxNxt)
          degreesAngleNxt = degrees(radiansAngleNxt)

          reverseArrowNxt = pg.transform.smoothscale_by(reverseArrow, (1 + (.3 - reverseArrowSizeMultiplier)) * self.playFieldResMultiplier)
          reverseArrowNxt = pg.transform.rotate(reverseArrowNxt, degreesAngleNxt)
          reverseArrowNxt.set_alpha(sliderAlpha)

          reverseArrowNxtPos = (
            p1Nxt['x'] - (reverseArrowNxt.get_width() / 2) - scaledStackOffset,
            p1Nxt['y'] - (reverseArrowNxt.get_height() / 2) - scaledStackOffset
          )

          self.surface.blit(reverseArrowNxt, reverseArrowNxtPos)

    self.drawHitcircle(slider.head, time)

  def drawSpinner(self, spinner: Spinner, time: int):
    ## WIP ##

    pg.draw.circle(self.surface, (255, 255, 255), self.center, 5, 1)
    pg.draw.circle(self.surface, (255, 255, 255), self.center, self.playFieldRes[1] / 3, 1)

  def drawCursor(self, time: int, trails: list = ['default']):
    for trail in trails:
      if trail not in ['default', 'connected']:
        raise ValueError('trail types must be \'default\' or \'connected\'')

    trailLength = 15
    cursorTrail = self.beatmap.getCursorTrailAtTimeTransformed(time, trailLength)

    if len(cursorTrail) == 0:
      return None

    if 'default' in trails:
      for i in range(4, len(cursorTrail) - 1):
        trailAlpha = mapRange(i, 0, trailLength, 0, 255)
        self.cursorTrailScaled.set_alpha(trailAlpha)

        cursorTrailPos = (
          cursorTrail[i]['x'] - self.cursorTrailScaledHalfWidth,
          cursorTrail[i]['y'] - self.cursorTrailScaledHalfHeight
        )

        self.surface.blit(self.cursorTrailScaled, cursorTrailPos)

      lastTrailPos = (
        cursorTrail[-1]['x'] - self.cursorScaledHalfWidth,
        cursorTrail[-1]['y'] - self.cursorScaledHalfHeight
      )

      self.surface.blit(self.cursorScaled, lastTrailPos)

    if 'connected' in trails:
      for i in range(len(cursorTrail) - 1):
        cursorTrailPos1 = (cursorTrail[i]['x'] , cursorTrail[i]['y'])
        cursorTrailPos2 = (cursorTrail[i + 1]['x'], cursorTrail[i + 1]['y'])

        pg.draw.line(self.surface, (255, 255, 255), cursorTrailPos1, cursorTrailPos2, 1)
        pg.draw.circle(self.surface, (0, 128, 200), cursorTrailPos1, 2)

      lastTrailPos = (cursorTrail[-1]['x'] , cursorTrail[-1]['y'])

      pg.draw.circle(self.surface, (255, 0, 0), lastTrailPos, 4)
  
  def drawKeyOverlay(self, time: int):
    pass
