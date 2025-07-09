from typing import List, Dict, Union, Optional
from copy import deepcopy
from pygame import Color as pgColor, transform as pgTransform
from modules.misc.helpers import tintImage
from modules.readers.beatmapReader import readMap
from modules.beatmapElements.hitobjects import *
from modules.UI.windowManager import Window
import sharedWindow

# stores all the data about beatmap and replay #
class Beatmap:
  def __init__(self, mapURL: str, skin: dict, replayData: Optional[dict]):
    self.window: Window = sharedWindow.window

    if self.window.customData['debug']:
      print('creating a new beatmap...\nreading map data...')

    self.map = readMap(mapURL)

    self.replay = replayData

    self.skin = skin
    # sort out hitobjects #
    self.hitobjects: List[Union[Hitcircle, Slider, Spinner]] = []
    self.hitcircles: List[Hitcircle] = []
    self.sliders: List[Slider] = []
    self.spinners: List[Spinner] = []

    # mirroring objects when HR is enabled #
    if 'HR' in self.replay['mods']:
      for obj in self.map['hitobjects']:
        obj['y'] = 384 - obj['y']

        if not obj['type'] == 'slider': continue

        for i in range(len(obj['curvePoints'])):
          obj['curvePoints'][i]['y'] = 384 - obj['curvePoints'][i]['y']

    if self.window.customData['debug']:
      print('initializing all the hitobjects...')

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

    if self.window.customData['debug']:
      print('done.')

    if self.replay is None:
      self.mode = 'preview'
    else:
      self.mode = 'replay'

    # process replay array #
    if self.window.customData['debug']:
      print('processing replay data...')

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

    if self.window.customData['debug']:
      print('done.')

    # get some map data #
    if self.window.customData['debug']:
      print('calculating beatmap difficulty data + some required data...')

    self.HP = self.map['difficulty']['HPDrainRate']
    self.CS = self.map['difficulty']['CircleSize']
    self.AR = self.map['difficulty']['ApproachRate']
    self.OD = self.map['difficulty']['OverallDifficulty']
    self.sliderMultiplier = self.map['difficulty']['SliderMultiplier']
    self.sliderTickRate = self.map['difficulty']['SliderTickRate']
    self.objectFadeout = 200
    self.stackLeniency = self.map['general']['StackLeniency']

    if 'EZ' in self.replay['mods']:
      self.CS /= 2
      self.AR /= 2
      self.OD /= 2
      self.HP /= 2
    elif 'HR' in self.replay['mods']:
      newCS = self.CS * 1.3
      self.CS = newCS if newCS <= 10 else 10

      newAR = self.AR * 1.4
      self.AR = newAR if newAR <= 10 else 10

      newOD = self.OD * 1.4
      self.OD = newOD if newOD <= 10 else 10

      newHP = self.HP * 1.4
      self.HP = newHP if newHP <= 10 else 10

    # calculate some needed values #
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
    
    self.hitWindow300Rounded = round(self.hitWindow300)
    self.hitWindow100Rounded = round(self.hitWindow100)
    self.hitWindow50Rounded = round(self.hitWindow50)

    if self.OD < 5:
      self.requiredRPS = 5 - 2 * (5 - self.OD) / 5
    elif self.OD > 5:
      self.requiredRPS = 5 + 2.5 * (self.OD - 5) / 5
    else:
      self.requiredRPS = 5

    if self.window.customData['debug']:
      print('done.')

    # calculate slider slide times #
    if self.window.customData['debug']:
      print('calculating slider slide times...')

    for slider in self.sliders:
      timingPoints = self.effectiveTimingPointAtTime(slider.time)
      UI_TimingPoint = timingPoints[0]
      inheritedTimingPoint = timingPoints[1]

      if (UI_TimingPoint is not None) and (inheritedTimingPoint is not None):
        if UI_TimingPoint['time'] > inheritedTimingPoint['time']:
          inheritedTimingPoint = None

      if inheritedTimingPoint is not None:
        SV = -100 / inheritedTimingPoint['inverseSliderVelocityMultiplier']
      else:
        SV = 1

      slider.slideTime = slider.length / (self.map['difficulty']['SliderMultiplier'] * 100 * SV) * UI_TimingPoint['beatLength']
      slider.totalSlideTime = slider.slideTime * slider.slides
      slider.endTime = slider.time + slider.totalSlideTime

    if self.window.customData['debug']:
      print('done.')

    # calculate slider ticks #
    for slider in self.sliders:
      beatLength = self.effectiveTimingPointAtTime(slider.time)[0]['beatLength']
      tickInterval = beatLength / self.sliderTickRate

      singleSlideTicks = []

      tick = slider.time + tickInterval
      while tick < (slider.time + slider.slideTime):
        if abs(tick - (slider.time + slider.slideTime)) > 10:
          singleSlideTicks.append(tick)

        tick += tickInterval

      for i in range(slider.slides):
        for tick in singleSlideTicks:
          slider.ticks.append(tick + (slider.slideTime * i))

    # calculating stacks #
    # the algorithm is taken straight from peppy: https://gist.github.com/peppy/1167470 #

    if self.window.customData['debug']:
      print('calculating stacks...')
  
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

    if self.window.customData['debug']:
      print('done.')

    # calculating hit judgments #
    ## !!! WIP !!! ##

    if self.window.customData['debug']:
      print('calculating hit judgments [!WIP!]...')

    if self.mode == 'replay':
      k1 = k1In = k1Out = k2 = k2In = k2Out = False
      for pos in self.replayArrayByTime:
        # setup key change states
        k1Pressed = 'k1' in pos['keys'] or 'm1' in pos['keys']

        if k1Pressed:
          k1In = not k1
          k1Out = False
          k1 = True
        else:
          k1Out = k1
          k1In = False
          k1 = False

        k2Pressed = 'k2' in pos['keys'] or 'm2' in pos['keys']
        if k2Pressed:
          k2In = not k2
          k2Out = False
          k2 = True
        else:
          k2Out = k2
          k2In = False
          k2 = False

        time = pos['time']
        hitobjects = self.hitobjectsAtTime(time)
        activeObject = None

        requiredCalcs = 1

        if k1In and k2In:
          requiredCalcs = 2

        for _ in range(requiredCalcs):
          # get the current active hitcircle
          for hitobject in hitobjects:
            if isinstance(hitobject, Spinner) or hitobject.hit or (time > (hitobject.time + self.hitWindow50)):
              continue

            activeObject = hitobject

            break

          if activeObject == None: continue

          inHitArea = dist(pos['x'], pos['y'], activeObject.x, activeObject.y) <= self.circleRadius

          # check judgment if the avtive object has been hit
          if inHitArea and (k1In or k2In):
            hitError = abs(activeObject.time - time)

            judgment = 'lock'

            if hitError < self.hitWindow300Rounded:
              judgment = 300
            elif hitError < self.hitWindow100Rounded:
              judgment = 100
            elif hitError < self.hitWindow50Rounded:
              judgment = 50
            elif hitError >= self.missWindow:
              judgment = 0
            else: continue

            activeObject.judgment = judgment
            activeObject.hitTime = time
            activeObject.hit = True

      for obj in self.hitobjects:
        if not isinstance(obj, Spinner) and not obj.hit:
          obj.hitTime = obj.time + self.hitWindow50
          obj.judgment = 0

    if self.window.customData['debug']:
      print('done.')

      print('setting combo colors...')
 
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

    if self.window.customData['debug']:
      print('done.')

      print('processing skin elements...')

    # the multiplier for scaling all in-game elements (such as hitobjects) #
    hitcircleSkinSize = 0

    self.baseImage = self.skin['elements']['hitcircleoverlay']

    self.baseImage.lock()

    imgW, imgH = self.baseImage.get_size()

    for x in range(imgW):
      y = imgH / 2
      _, _, _, alpha = self.baseImage.get_at((x, y))

      if alpha > 200:
        hitcircleSkinSize = dist(x, y, imgW / 2, imgH / 2)
        break

    self.baseImage.unlock()

    self.elementsScaleMultiplier = self.circleRadius / hitcircleSkinSize

    # import and process needed skin elements #
    self.approachcircle = pgTransform.smoothscale_by(self.skin['elements']['approachcircle'], self.elementsScaleMultiplier)

    self.hitcircle = pgTransform.smoothscale_by(self.skin['elements']['hitcircle'], self.elementsScaleMultiplier)

    self.hitcircleOverlay = pgTransform.smoothscale_by(self.skin['elements']['hitcircleoverlay'], self.elementsScaleMultiplier)

    self.cursor = pgTransform.smoothscale_by(self.skin['elements']['cursor'], self.elementsScaleMultiplier)

    self.cursorTrail = pgTransform.smoothscale_by(self.skin['elements']['cursortrail'], self.elementsScaleMultiplier)

    self.reverseArrow = self.skin['elements']['reversearrow']

    # create combo colored hitcircles, approachcircles, and slider balls #
    self.hitcircleCombos = []
    self.approachcircleCombos = []
    self.sliderBallCombos = []
    for i in range(len(self.comboColors)):
      self.hitcircleCombos.append(self.hitcircle.copy())
      tintImage(self.hitcircleCombos[-1], self.comboColors[i])

      self.approachcircleCombos.append(self.approachcircle.copy())
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

    # set hitsounds for all objects
    for obj in self.hitobjects:
      if isinstance(obj, Spinner): continue

      UI_TimingPoint = self.effectiveTimingPointAtTime(obj.time)[0]

      if not UI_TimingPoint is None:
        sampleSet = UI_TimingPoint['sampleSet']
      else:
        sampleSet = self.map['general']['SampleSet'].lower()

      obj.sampleSet = sampleSet

      for hitsound in obj.rawDict['hitSound']:
        hitsoundKey = f'{sampleSet}-hit{hitsound}'

        if hitsoundKey in self.skin['hitsounds']:
          obj.hitsounds.append(self.skin['hitsounds'][hitsoundKey])

    if self.window.customData['debug']:
      print('done.')

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

  def cursorTrailAtTimeTransformed(self, time: int, trailLength: Optional[int] = 10) -> List[Dict[str, Union[int, float]]]:
    if not self.transformedCusrorData:
      return None

    returnTrail = []

    for pos in self.transformedCusrorData:
      if pos['time'] > time: break
      returnTrail.append(pos)

    if len(returnTrail) > trailLength:
      returnTrail = returnTrail[-trailLength:]

    return returnTrail

  def cursorTrailAtTime(self, time: int, trailLength: Optional[int] = 10) -> List[Dict[str, Union[int, float]]]:
    returnTrail = []

    for pos in self.replayArrayByTime:
      if pos['time'] > time: break
      returnTrail.append(pos)

    if len(returnTrail) > trailLength:
      returnTrail = returnTrail[-trailLength:]

    return returnTrail

  def lastObjectAtTimeByHitTime(self, time: int) -> Union[Hitcircle, Slider, Spinner, bool]:

    for i in range(len(self.hitobjects) - 1, -1, -1):
      obj = self.hitobjects[i]
      if isinstance(obj, Spinner): continue

      if obj.hitTime <= time:
        return obj

    return False
