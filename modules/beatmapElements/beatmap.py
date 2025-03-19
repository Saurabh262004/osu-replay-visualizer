from typing import List, Dict, Union, Optional
from copy import deepcopy
from pygame import Color as pgColor, transform as pgTransform
from modules.misc.helpers import tintImage
from modules.readers.beatmapReader import readMap
from modules.readers.replayReader import getReplayData
from modules.readers.importSkin import importSkin
from modules.beatmapElements.hitobjects import *

# stores all the data about beatmap and replay #
class Beatmap:
  def __init__(self, osuURL: str, mapURL: str, skinName: str, replayURL: str = None):
    # print('creating a new beatmap...\nreading map data...')
    self.map = readMap(mapURL)
    # print('done.\nimporting skin...')
    self.skin = importSkin(skinName, osuURL)
    # print('done.\nreading replay data again...')
    self.replay = getReplayData(replayURL) if replayURL else None
    # print('done.')

    # sort out hitobjects #
    self.hitobjects: List[Union[Hitcircle, Slider, Spinner]] = []
    self.hitcircles: List[Hitcircle] = []
    self.sliders: List[Slider] = []
    self.spinners: List[Spinner] = []

    # print('initializing all the hitobjects...')
    for hitobject in self.map['hitobjects']:
      if hitobject['type'] == 'hitcircle':
        self.hitobjects.append(Hitcircle(hitobject, self))
        self.hitcircles.append(self.hitobjects[-1])
      elif hitobject['type'] == 'slider':
        self.hitobjects.append(Slider(hitobject, self))
        self.sliders.append(self.hitobjects[-1])
      elif hitobject['type'] == 'spinner':
        self.hitobjects.append(Spinner(hitobject, self))
        self.spinners.append(self.hitobjects[-1])
    # print('done.')

    if self.replay is None:
      self.mode = 'preview'
    else:
      self.mode = 'replay'

    # process replay array #
    if self.mode == 'replay':
      self.replayArray = self.replay['replayArray']
      self.replayArray.pop()
      self.replayArrayByTime = [
        {
          'x': self.replayArray[0]['x'],
          'y': self.replayArray[0]['y'],
          'time': self.replayArray[0]['interval'],
          'keys': self.replayArray[0]['keys']
        }
      ]

      for i in range(1, len(self.replayArray)):
        currentPos = self.replayArray[i]
        lastStamp = self.replayArrayByTime[-1]['time']
        currentInterval = currentPos['interval']

        self.replayArrayByTime.append(
          {
            'x': currentPos['x'],
            'y': currentPos['y'],
            'time': lastStamp + currentInterval,
            'keys': currentPos['keys']
          }
        )

      self.replayArrayByTime.sort(key = lambda x: x['time'])

    # get some map data #
    self.HP = self.map['difficulty']['HPDrainRate']
    self.CS = self.map['difficulty']['CircleSize']
    self.AR = self.map['difficulty']['ApproachRate']
    self.OD = self.map['difficulty']['OverallDifficulty']
    self.sliderMultiplier = self.map['difficulty']['SliderMultiplier']
    self.sliderTickRate = self.map['difficulty']['SliderTickRate']
    self.objectFadeout = 200
    self.stackLeniency = self.map['general']['StackLeniency']

    # calculate some needed values #
    # self.requiredRPM = 60000 / (self.mapDict['timingPoints'][0]['bpm'] * self.sliderMultiplier)
    self.circleRadius = 54.4 - 4.48 * self.CS

    if self.AR < 5:
      self.preempt = 1200 + 600 * (5 - self.AR) / 5
      self.fadeIn = 800 + 400 * (5 - self.AR) / 5
    elif self.AR > 5:
      self.preempt = 1200 - 750 * (self.AR - 5) / 5
      self.fadeIn = 800 - 500 * (self.AR - 5) / 5
    else:
      self.preempt = 1200
      self.fadeIn = 800

    self.hitWindow300 = 80 - 6 * self.OD
    self.hitWindow100 = 140 - 8 * self.OD
    self.hitWindow50 = 200 - 10 * self.OD
    self.missWindow = 400

    if self.OD < 5:
      self.requiredRPS = 5 - 2 * (5 - self.OD) / 5
    elif self.OD > 5:
      self.requiredRPS = 5 + 2.5 * (self.OD - 5) / 5
    else:
      self.requiredRPS = 5

    # calculate slider slide times (the time it takes for the slider to complete one slide) #
    for slider in self.sliders:
      timingPoints = self.effectiveTimingPointAtTime(slider.time)

      if not (timingPoints[1] is None):
        SV = -100 / timingPoints[1]['inverseSliderVelocityMultiplier']
      else:
        SV = 1

      slider.slideTime = slider.length / (self.map['difficulty']['SliderMultiplier'] * 100 * SV) * timingPoints[0]['beatLength']
      slider.endTime = slider.time + (slider.slideTime * slider.slides)

    # calculating stacks #
    # the algorithm is taken straight from peppy: https://gist.github.com/peppy/1167470 #
    stackOffset = self.circleRadius / 10

    STACK_LENIENCE = 3

    for i in range(len(self.hitobjects) - 1, -1, -1):
      n = i
      objectI = self.hitobjects[i]

      if isinstance(objectI, Spinner) or not (objectI.stackCount == 0): continue

      if isinstance(objectI, Hitcircle):
        while n > 0:
          n -= 1

          objectN = self.hitobjects[n]

          if isinstance(objectN, Spinner): continue

          if (objectI.time - (self.preempt * self.stackLeniency) > objectN.endTime): break

          if isinstance(objectN, Slider) and dist(objectN.endX, objectN.endY, objectI.x, objectI.y) < STACK_LENIENCE:
            offset = objectI.stackCount - objectN.stackCount + 1

            for j in range(n + 1, i + 1):
              if (dist(objectN.endX, objectN.endY, self.hitobjects[j].x, self.hitobjects[j].y) < STACK_LENIENCE):
                self.hitobjects[j].stackCount -= offset

            break

          if dist(objectN.x, objectN.y, objectI.x, objectI.y) < STACK_LENIENCE:
            objectN.stackCount = objectI.stackCount + 1
            objectI = objectN
      elif isinstance(objectI, Slider):
        while n > 0:
          n -= 1

          objectN = self.hitobjects[n]

          if isinstance(objectN, Spinner): continue

          if (objectI.time - (self.preempt * self.stackLeniency) > objectN.time): break

          if (dist(objectN.endX, objectN.endY, objectI.x, objectI.y) < STACK_LENIENCE):
            objectN.stackCount = objectI.stackCount + 1
            objectI = objectN

    for obj in self.hitobjects:
      if not isinstance(obj, Spinner) and not (obj.stackCount == 0):
        obj.stackOffset = (stackOffset * obj.stackCount)

        if isinstance(obj, Slider):
          obj.head.stackOffset = obj.stackOffset

    # calculating hit judgments #
    ## !!! WIP !!! ##
    if self.mode == 'replay':
      k1 = k1In = k1Out = k2 = k2In = k2Out = False
      for pos in self.replayArrayByTime:
        if 'k1' in pos['keys'] or 'm1' in pos['keys']:
          if not k1:
            k1 = True
            k1In = True
          else:
            k1In = False
        elif k1:
          k1 = False
          k1Out = True
        else:
          k1Out = False

        if 'k2' in pos['keys'] or 'm2' in pos['keys']:
          if not k2:
            k2 = True
            k2In = True
          else:
            k2In = False
        elif k2:
          k2 = False
          k2Out = True
        else:
          k2Out = False

        time = pos['time']
        hitobjects = self.hitobjectsAtTime(time)
        for i in range(len(hitobjects)):
          obj = hitobjects[i]

          if isinstance(obj, Spinner):
            continue

          insideUpperHitwindow = (time < (obj.time + self.hitWindow50))
          insideLowerHitwindow = (time > (obj.time - self.missWindow))
          inHitArea = dist(pos['x'], pos['y'], obj.x, obj.y) <= self.circleRadius

          if obj.hit or not insideUpperHitwindow or not insideLowerHitwindow:
            continue
          elif inHitArea and (k1In or k2In):
            hitError = abs(obj.time - time)
            hit = False

            if hitError < self.hitWindow300:
              obj.judgment = 300
              hit = obj.hit = True
              # print('300')
            elif hitError < self.hitWindow100:
              obj.judgment = 100
              hit = obj.hit = True
              # print('100')
            elif hitError < self.hitWindow50:
              obj.judgment = 50
              hit = obj.hit = True
              # print('50')
            elif hitError < self.missWindow:
              obj.judgment = 0
              hit = obj.hit = True
              # print('0')

            if hit:
              obj.hitTime = time
              break

      for obj in self.hitobjects:
        if not isinstance(obj, Spinner) and not obj.hit:
          obj.hitTime = obj.time + self.hitWindow50
          obj.judgment = 0

    # get combo colors #
    if 'Colours' in self.map:
      self.comboColors = [pgColor(*self.map['Colours'][color]) for color in self.map['Colors']]
    else:
      self.comboColors = []
      i = 1
      while f'Combo{i}' in self.skin['config']:
        self.comboColors.append(pgColor(*self.skin['config'][f'Combo{i}']))
        i += 1

    # set combo indexes and color combo indexes for hitobjects #
    comboIndex = 1
    totalCombo = -1
    for hitobject in self.hitobjects:
      if hitobject.rawDict['newCombo']:
        comboIndex = 1
        totalCombo += 1 + hitobject.rawDict['comboColorsSkip']
      else:
        comboIndex += 1

      hitobject.comboIndex = comboIndex
      hitobject.comboColorIndex = totalCombo % len(self.comboColors)
      if isinstance(hitobject, Slider):
        hitobject.head.comboIndex = hitobject.comboIndex
        hitobject.head.comboColorIndex = hitobject.comboColorIndex

    # print('processing skin elements...')

    # the multiplier for scaling all in-game elements (such as hitobjects) #
    self.elementsScaleMultiplier = (self.circleRadius * 2) / self.skin['elements']['hitcircle'].get_width()

    # import and process needed skin elements #
    self.hitcircleOverlay = self.skin['elements']['hitcircleoverlay']
    self.hitcircleOverlay = pgTransform.smoothscale_by(self.hitcircleOverlay, self.elementsScaleMultiplier)
    self.cursor = self.skin['elements']['cursor']
    self.cursor = pgTransform.smoothscale_by(self.cursor, self.elementsScaleMultiplier)
    self.cursorTrail = self.skin['elements']['cursortrail']
    self.cursorTrail = pgTransform.smoothscale_by(self.cursorTrail, self.elementsScaleMultiplier)
    self.reverseArrow = self.skin['elements']['reversearrow']
    self.reverseArrow = pgTransform.smoothscale_by(self.reverseArrow, self.elementsScaleMultiplier)

    # create combo colored hitcircles, approachcircles, and slider balls #
    self.hitcircleCombos = []
    self.approachcircleCombos = []
    self.sliderBallCombos = []
    for i in range(len(self.comboColors)):
      self.hitcircleCombos.append(self.skin['elements']['hitcircle'].copy())
      self.hitcircleCombos[-1] = pgTransform.smoothscale_by(self.hitcircleCombos[-1], self.elementsScaleMultiplier)
      tintImage(self.hitcircleCombos[-1], self.comboColors[i])

      self.approachcircleCombos.append(self.skin['elements']['approachcircle'].copy())
      self.approachcircleCombos[-1] = pgTransform.smoothscale_by(self.approachcircleCombos[-1], self.elementsScaleMultiplier)
      tintImage(self.approachcircleCombos[-1], self.comboColors[i])

      if isinstance(self.skin['elements']['sliderb'], pg.Surface):
        self.sliderBallCombos.append(self.skin['elements']['sliderb'].copy())
        self.sliderBallCombos[-1] = pgTransform.smoothscale_by(self.sliderBallCombos[-1], self.elementsScaleMultiplier)
        tintImage(self.sliderBallCombos[-1], self.comboColors[i])
      elif isinstance(self.skin['elements']['sliderb'], list):
        self.sliderBallCombos.append([])
        for ball in self.skin['elements']['sliderb']:
          self.sliderBallCombos[-1].append(ball.copy())
          self.sliderBallCombos[-1][-1] = pgTransform.smoothscale_by(self.sliderBallCombos[-1][-1], self.elementsScaleMultiplier)
          tintImage(self.sliderBallCombos[-1][-1], self.comboColors[i])

    # print('done.')

  # get the timing points that are in effect at a certain time #
  def effectiveTimingPointAtTime(self, time: int) -> List[Dict[str, Union[int, float]]]:
    possibleUninheritedTimingPoint = None
    possibleInheritedTimingPoint = None

    for timingPoint in self.map['timingPoints']:
      if timingPoint['time'] <= time:
        if timingPoint['uninherited'] == 1:
          possibleUninheritedTimingPoint = deepcopy(timingPoint)
        else:
          possibleInheritedTimingPoint = deepcopy(timingPoint)
      else:
        break

    return [possibleUninheritedTimingPoint, possibleInheritedTimingPoint]

  # get the hitobjects that are active / on screen at a certain time #
  def hitobjectsAtTime(self, time: int) -> List[Union[Hitcircle, Slider, Spinner]]:
    returnHitobjects = []

    timeClose = time + self.preempt
    timeOpenHitcircle = (time - self.hitWindow50) - self.objectFadeout

    for hitobject in self.hitobjects:
      if hitobject.time > timeClose: break
      if isinstance(hitobject, Hitcircle) and hitobject.time < timeOpenHitcircle: continue
      if isinstance(hitobject, Slider) and (hitobject.time + (hitobject.slideTime * hitobject.slides) + self.objectFadeout) < time: continue
      if isinstance(hitobject, Spinner) and hitobject.endTime < time: continue

      returnHitobjects.append(hitobject)

    return returnHitobjects

  def transformCursorData(self, resMultiplier: Union[int, float], xPadding: Union[int, float], yPadding: Union[int, float]):
    self.transformedCusrorData = [{
      'x': (pos['x'] * resMultiplier) + xPadding,
      'y': (pos['y'] * resMultiplier) + yPadding,
      'time': pos['time']
    } for pos in self.replayArrayByTime]

  def getCursorTrailAtTimeTransformed(self, time: int, trailLength: Optional[int] = 10) -> List[Dict[str, Union[int, float]]]:
    if not self.transformedCusrorData:
      return None

    returnTrail = []

    for pos in self.transformedCusrorData:
      if pos['time'] > time: break
      returnTrail.append(pos)

    if len(returnTrail) > trailLength:
      returnTrail = returnTrail[-trailLength:]

    return returnTrail

  def getInputsAtTime(self, time: int) -> Dict[str, Union[int, float]]:
    pass

  def getCursorTrailAtTime(self, time: int, trailLength: Optional[int] = 10) -> List[Dict[str, Union[int, float]]]:
    returnTrail = []

    for pos in self.replayArrayByTime:
      if pos['time'] > time: break
      returnTrail.append(pos)

    if len(returnTrail) > trailLength:
      returnTrail = returnTrail[-trailLength:]

    return returnTrail
