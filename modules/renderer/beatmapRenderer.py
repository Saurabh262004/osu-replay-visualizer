from typing import Union, Optional, List
from math import atan2, degrees, ceil
import pygame as pg
from modules.misc.gameLists import MODS, MODS_ABRV
from modules.UI.windowManager import Window
import sharedWindow
from modules.misc.helpers import mapRange, find
from modules.beatmapElements.hitobjects import Hitcircle, Slider, Spinner
from modules.beatmapElements.beatmap import Beatmap

numType = Union[int, float]

class BeatmapRenderer:
  def __init__(self, beatmapURL: dict, replayData: Optional[dict], surface: pg.Surface, playFieldResMultiplier: numType):
    self.window: Window = sharedWindow.window
    self.userData = self.window.customData['userData']
    self.debug = self.window.customData['debug']

    if self.debug:
      print('creating a new renderer...')

    if replayData is not None:
      if self.debug:
        print('initializing beatmap with replay...')

      self.beatmap = Beatmap(beatmapURL, self.window.customData['skin'], replayData)

      if self.debug:
        print('initializing beatmap done.')
    else:
      self.beatmap = Beatmap(beatmapURL, self.window.customData['skin'])

    self.maxImgAlpha = 255
    self.keyHighlight1 = pg.Color(190, 145, 214)
    self.keyHighlight2 = pg.Color(76, 228, 101)
    self.keyOff = pg.Color(30, 30, 30)

    # self.customTrailIntervalCol = pg.Color(0, 128, 200)
    self.customTrailIntervalCol = pg.Color(249, 243, 118)
    self.customCursorCol = pg.Color(199, 0, 57)

    self.supportedModsDisplay = [
      'AP',
      'CN',
      'DT',
      'EZ',
      'FL',
      'HT',
      'HR',
      'HD',
      'NC',
      'NF',
      'RX',
      'AP',
      'V2',
      'SO'
    ]

    self.timeDivisor = 1
    if 'DT' in self.beatmap.replay['mods'] or 'NC' in self.beatmap.replay['mods']:
      self.timeDivisor = 2 / 3
    elif 'HT' in self.beatmap.replay['mods']:
      self.timeDivisor = 4 / 3

    self.updateSurface(surface, playFieldResMultiplier)

  def updateSurface(self, newSurface: pg.Surface, newResMultiplier: numType):
    # updating resolution variables
    self.surface = newSurface
    self.playFieldResMultiplier = newResMultiplier
    self.playFieldRes = (self.playFieldResMultiplier * 512, self.playFieldResMultiplier * 384)
    self.screenWidth, self.screenHeight = self.surface.get_size()
    self.playFieldXpadding = (self.screenWidth - self.playFieldRes[0]) / 2
    self.playFieldYpadding = ((self.screenHeight - self.playFieldRes[1]) / 2) - (self.screenHeight * .05)

    self.center = (
      self.playFieldXpadding + (self.playFieldRes[0] / 2),
      self.playFieldYpadding + (self.playFieldRes[1] / 2)
    )

    # scaling cursor images
    self.cursorScaled = pg.transform.smoothscale_by(self.beatmap.cursor, self.playFieldResMultiplier)
    self.cursorScaledHalfWidth = (self.cursorScaled.get_width() / 2)
    self.cursorScaledHalfHeight = (self.cursorScaled.get_height() / 2)

    self.cursorTrailScaled = pg.transform.smoothscale_by(self.beatmap.cursorTrail, self.playFieldResMultiplier)
    self.cursorTrailScaledHalfWidth = (self.cursorTrailScaled.get_width() / 2)
    self.cursorTrailScaledHalfHeight = (self.cursorTrailScaled.get_height() / 2)

    # transform cursor data to new resolution
    self.beatmap.transformCursorData(self.playFieldResMultiplier, self.playFieldXpadding, self.playFieldYpadding)

    # transform and render slider bodies to new resolution
    if self.debug:
      print('creating slider bodies...')

    for slider in self.beatmap.sliders:
      slider.transformBodyPath((self.playFieldResMultiplier, self.playFieldResMultiplier), (self.playFieldXpadding, self.playFieldYpadding))
      slider.renderBody(self.playFieldResMultiplier, self.userData['highQualitySliders'])

    if self.debug:
      print('done.')

    self.customCursorRadius = max(int((self.beatmap.circleRadius * self.playFieldResMultiplier) / 8), 3)
    self.customCursorTrailRadius = int(self.customCursorRadius / 3)

    # setup the key overlay
    keySize = int(self.playFieldRes[0] / 25)
    self.keyBorderRadius = int(keySize * .15)

    self.k1Rect = pg.Rect(
      int(self.screenWidth - (keySize * 1.2)),
      int((self.screenHeight * .5) - (keySize * 1.1)),
      keySize,
      keySize
    )

    self.k2Rect = pg.Rect(
      int(self.screenWidth - (keySize * 1.2)),
      int((self.screenHeight * .5) + (keySize * 0.1)),
      keySize,
      keySize
    )

    # setup mod display
    self.modDisplays = []
    size = int(keySize * 2)
    padding = int(size / 4)

    for mod in self.beatmap.replay['mods']:
      if mod in self.supportedModsDisplay:
        currentModIndex = len(self.modDisplays)

        modListIndex = find(mod, MODS_ABRV['arr'])

        modName = 'relax2' if mod == 'AP' else MODS['arr'][modListIndex].lower()

        modImage = self.beatmap.skin['elements'][f'selection-mod-{modName}']

        self.modDisplays.append(
          {
            'pos': (int(self.screenWidth - ((padding + size) * (currentModIndex + 1))), padding),
            'img': pg.transform.smoothscale(modImage, (size, size))
          }
        )

  def render(self, time: int):
    renderObjects = self.beatmap.hitobjectsAtTime(time / self.timeDivisor)

    self.surface.fill((0, 0, 0))

    if self.userData['playfieldBorder']:
      pg.draw.rect(self.surface, (128, 128, 128), (self.playFieldXpadding, self.playFieldYpadding, self.playFieldRes[0], self.playFieldRes[1]), 1)

    for i in range(len(renderObjects) - 1, -1, -1):
      if isinstance(renderObjects[i], Hitcircle): self.drawHitcircle(renderObjects[i], time / self.timeDivisor)
      elif isinstance(renderObjects[i], Slider): self.drawSlider(renderObjects[i], time / self.timeDivisor)
      elif isinstance(renderObjects[i], Spinner): self.drawSpinner(renderObjects[i], time / self.timeDivisor)

    if self.beatmap.mode == 'replay':
      trails = []

      if self.userData['renderCursorTracker']:
        trails.append('connected')
      if self.userData['renderSkinCursor']:
        trails.append('default')

      self.drawCursor(time / self.timeDivisor, trails)

      if self.userData['renderKeyOverlay']:
        self.drawKeyOverlay(time / self.timeDivisor)

      if self.userData['renderModsDisplay']:
        self.drawModsDisplay()

  def drawHitcircle(self, hitcircle: Hitcircle, time: int):
    comboStr = str(hitcircle.comboIndex)
    comboLength = len(comboStr)

    hitcircleImage = self.beatmap.hitcircleCombos[hitcircle.comboColorIndex]
    comboImages = [self.beatmap.skin['elements'][f'default-{comboNumber}'] for comboNumber in comboStr]
    hitcircleOverlayImage = self.beatmap.hitcircleOverlay

    drawWindowStart = hitcircle.time - self.beatmap.preempt
    fadeWindowEnd = drawWindowStart + self.beatmap.fadeIn

    if (not 'HD' in self.beatmap.replay['mods']) or self.userData['disableHidden']:
      if hitcircle.time >= time:
        hitcircleMultiplier = 1
        hitobjectAlpha = mapRange(time, drawWindowStart, fadeWindowEnd, 0, self.maxImgAlpha)
      else:
        if hitcircle.hitTime >= time:
          hitcircleMultiplier = 1
          hitobjectAlpha = self.maxImgAlpha
        else:
          hitcircleMultiplier = mapRange(time, hitcircle.hitTime, hitcircle.hitTime + self.beatmap.objectFadeout, 1, 1.5)
          hitobjectAlpha = mapRange(time, hitcircle.hitTime, hitcircle.hitTime + self.beatmap.objectFadeout, self.maxImgAlpha, 0)
    else:
      hitcircleMultiplier = 1

      if time < fadeWindowEnd:
        hitobjectAlpha = mapRange(time, drawWindowStart, fadeWindowEnd, 0, self.maxImgAlpha)
      else:
        hitobjectAlpha = mapRange(time, fadeWindowEnd, hitcircle.time - ((hitcircle.time - fadeWindowEnd) * .5), self.maxImgAlpha, 0)

    if hitobjectAlpha > self.maxImgAlpha:
      hitobjectAlpha = self.maxImgAlpha
    elif hitobjectAlpha < 0:
      hitobjectAlpha = 0

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
      comboImagesScaled = [pg.transform.smoothscale_by(comboImage, (self.beatmap.elementsScaleMultiplier * self.playFieldResMultiplier) * .6) for comboImage in comboImages]

      for comboImage in comboImagesScaled:
        comboImage.set_alpha(hitobjectAlpha)

      comboWidth = comboImagesScaled[0].get_width()

      firstComboPosX = hitcircleImgPos[0] + ((hitcircleScaled.get_width() - (comboWidth * comboLength)) / 2)
      comboPosesX = [firstComboPosX + (comboWidth * i) for i in range(comboLength)]

      if comboLength > 1:
        comboPosXScaled = []

        j = 0
        for i in range(-int(comboLength/2), ceil(comboLength/2), 1):
          shrinkingFactor = .3

          currentMidPos = comboPosesX[j] + (comboWidth / 2)

          currentMidPos -= i * comboWidth * shrinkingFactor

          comboPosXScaled.append(currentMidPos - ((comboWidth * (1 + shrinkingFactor)) / 2))

          j += 1

        comboPosesX = comboPosXScaled

      comboPosY = hitcircleImgPos[1] + ((hitcircleScaled.get_height() - comboImagesScaled[0].get_height()) / 2)

      for i in range(comboLength):
        self.surface.blit(comboImagesScaled[i], (comboPosesX[i], comboPosY))

    if (not 'HD' in self.beatmap.replay['mods']) or self.userData['disableHidden']:
      approachcircleImage = self.beatmap.approachcircleCombos[hitcircle.comboColorIndex]

      if hitcircle.time >= time:
        approachCircleMultiplier = self.playFieldResMultiplier * mapRange(time, drawWindowStart, hitcircle.time, 4, 1)
      else:
        approachCircleMultiplier = 0

      if approachCircleMultiplier < 0:
        approachCircleMultiplier = 0

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
    drawWindowStart = slider.time - self.beatmap.preempt
    fadeWindowEnd = drawWindowStart + self.beatmap.fadeIn

    if slider.time >= time:
      sliderAlpha = mapRange(time, drawWindowStart, fadeWindowEnd, 0, self.maxImgAlpha)
    else:
      if slider.endTime <= time:
        sliderAlpha = mapRange(time, slider.endTime, slider.endTime + self.beatmap.objectFadeout, self.maxImgAlpha, 0)
      else:
        sliderAlpha = self.maxImgAlpha

    if ('HD' in self.beatmap.replay['mods']) and (not self.userData['disableHidden']):
      if time < fadeWindowEnd:
        sliderAlphaHD = mapRange(time, drawWindowStart, fadeWindowEnd, 0, self.maxImgAlpha)
      elif time < slider.time:
        sliderAlphaHD = self.maxImgAlpha
      else:
        sliderAlphaHD = mapRange(time, slider.time, slider.time + (slider.slideTime * slider.slides * .9), self.maxImgAlpha, 0)

      if sliderAlphaHD > self.maxImgAlpha:
        sliderAlpha = self.maxImgAlpha
      elif sliderAlphaHD < 0:
        sliderAlphaHD = 0

    if sliderAlpha > self.maxImgAlpha:
      sliderAlpha = self.maxImgAlpha
    elif sliderAlpha < 0:
      sliderAlpha = 0

    if ('HD' in self.beatmap.replay['mods']) and (not self.userData['disableHidden']):
      slider.bodySurface.set_alpha(sliderAlphaHD)
    else:
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
      anchorLineCol = (255, 255, 255)

      if slider.curveType == 'B':
        anchorLineCol = (0, 255, 0)
      elif slider.curveType == 'P':
        anchorLineCol = (0, 0, 255)

      for i in range(len(slider.anchors)):
        anchor = slider.anchors[i]
        anchorColor = (255, 0, 0) if anchor['red'] else (255, 255, 255)

        anchorPos = (
          (anchor['x'] - scaledStackOffset) * self.playFieldResMultiplier + self.playFieldXpadding,
          (anchor['y'] - scaledStackOffset) * self.playFieldResMultiplier + self.playFieldYpadding
        )

        pg.draw.circle(self.surface, anchorColor, anchorPos, 3)

        if i > 0:
          pg.draw.aaline(
            self.surface,
            anchorLineCol,
            (
              (slider.anchors[i - 1]['x'] - scaledStackOffset) * self.playFieldResMultiplier + self.playFieldXpadding,
              (slider.anchors[i - 1]['y'] - scaledStackOffset) * self.playFieldResMultiplier + self.playFieldYpadding
            ),
            anchorPos,
            1
          )

    if slider.slides > 1 and time <= slider.endTime:
      currentTimingPoints = self.beatmap.effectiveTimingPointAtTime(time)

      maxArrowSizeMult = .5
      if len(currentTimingPoints) > 0 and (currentTimingPoints[0] is not None):
        currentUITimingPoint = currentTimingPoints[0]

        timeSinceUIPoint = (time - currentUITimingPoint['time'])

        beatLength = currentUITimingPoint['beatLength']

        currentTotalBeatsComplete = int(timeSinceUIPoint / beatLength)

        timeAtLastBeat = currentUITimingPoint['time'] + (currentTotalBeatsComplete * beatLength)

        reverseArrowSizeMultiplier = mapRange(time, timeAtLastBeat, timeAtLastBeat + beatLength, maxArrowSizeMult, 0)
      else:
        reverseArrowSizeMultiplier = 0

      currentSlide = int(slide)
      remainingSlides = slider.slides - currentSlide
      doubleArrows = (remainingSlides > 1) and (time > slider.time)

      if remainingSlides > 0:
        evenSlide = currentSlide / 2 == int(currentSlide / 2)
        if evenSlide:
          p1 = slider.bodyPath[0]
          p2 = slider.bodyPath[2]
        else:
          p1 = slider.bodyPath[-1]
          p2 = slider.bodyPath[-3]

        reverseArrow = self.beatmap.reverseArrow

        dx, dy = p2['x'] - p1['x'], p2['y'] - p1['y']

        radiansAngle = atan2(-dy, dx)
        degreesAngle = degrees(radiansAngle)

        reverseArrowNow = pg.transform.smoothscale_by(reverseArrow, (1 + reverseArrowSizeMultiplier) * self.playFieldResMultiplier * self.beatmap.elementsScaleMultiplier)
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
            p2Nxt = slider.bodyPath[-3]
          else:
            p1Nxt = slider.bodyPath[0]
            p2Nxt = slider.bodyPath[2]

          dxNxt, dyNxt = p2Nxt['x'] - p1Nxt['x'], p2Nxt['y'] - p1Nxt['y']

          radiansAngleNxt = atan2(-dyNxt, dxNxt)
          degreesAngleNxt = degrees(radiansAngleNxt)

          reverseArrowNxt = pg.transform.smoothscale_by(reverseArrow, (1 + (maxArrowSizeMult - reverseArrowSizeMultiplier)) * self.playFieldResMultiplier * self.beatmap.elementsScaleMultiplier)
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

    trailLength = 20
    cursorTrail = self.beatmap.cursorTrailAtTimeTransformed(time, trailLength)

    if len(cursorTrail) == 0:
      return None

    if 'default' in trails:
      for i in range(9, len(cursorTrail) - 1):
        trailAlpha = mapRange(i, 9, trailLength, 0, 255)
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

        # line to connect cursor positions
        pg.draw.line(self.surface, (255, 255, 255), cursorTrailPos1, cursorTrailPos2, 1)
        
        # points on cursor position intervals
        pg.draw.circle(self.surface, self.customTrailIntervalCol, cursorTrailPos1, self.customCursorTrailRadius)

      lastTrailPos = (cursorTrail[-1]['x'] , cursorTrail[-1]['y'])

      # current cursor position
      pg.draw.circle(self.surface, self.customCursorCol, lastTrailPos, self.customCursorRadius)
  
  def drawKeyOverlay(self, time: int):
    cursorNow = self.beatmap.cursorTrailAtTime(time, 1)[0]

    if 'k1' in cursorNow['keys'] or 'm1' in cursorNow['keys']:
      pg.draw.rect(self.surface, self.keyHighlight1, self.k1Rect, border_radius=self.keyBorderRadius)
    else:
      pg.draw.rect(self.surface, self.keyOff, self.k1Rect, border_radius=self.keyBorderRadius)

    if 'k2' in cursorNow['keys'] or 'm2' in cursorNow['keys']:
      pg.draw.rect(self.surface, self.keyHighlight2, self.k2Rect, border_radius=self.keyBorderRadius)
    else:
      pg.draw.rect(self.surface, self.keyOff, self.k2Rect, border_radius=self.keyBorderRadius)

  def drawModsDisplay(self):
    for mod in self.modDisplays:
      modPos = mod['pos']
      modImg = mod['img']

      self.surface.blit(modImg, modPos)
