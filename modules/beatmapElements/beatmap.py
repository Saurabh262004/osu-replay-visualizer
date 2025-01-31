from typing import List, Dict, Union
from copy import deepcopy
from pygame import Color as pgColor, transform as pgTransform
from modules.misc.helpers import mapRange, tintImage
from modules.readers.beatmapReader import readMap
from modules.readers.replayReader import getReplayData
from modules.readers.importSkin import importSkin
from modules.beatmapElements.hitobjects import *

numType = Union[int, float]

class Beatmap:
  def __init__(self, mapURL: str, skinURL: str, replayURL: str = None):
    self.map = readMap(mapURL)
    self.skin = importSkin(skinURL, 'testFiles')
    self.replay = getReplayData(replayURL) if replayURL else None

    self.hitobjects: List[Union[Hitcircle, Slider, Spinner]] = []
    self.hitcircles: List[Hitcircle] = []
    self.sliders: List[Slider] = []
    self.spinners: List[Spinner] = []

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

    if self.replay is None:
      self.mode = 'preview'
    else:
      self.mode = 'replay'

    self.HP = self.map['difficulty']['HPDrainRate']
    self.CS = self.map['difficulty']['CircleSize']
    self.AR = self.map['difficulty']['ApproachRate']
    self.OD = self.map['difficulty']['OverallDifficulty']
    self.sliderMultiplier = self.map['difficulty']['SliderMultiplier']
    self.sliderTickRate = self.map['difficulty']['SliderTickRate']
    self.objectFadeout = 200

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

    if self.OD < 5:
      self.requiredRPS = 5 - 2 * (5 - self.OD) / 5
    elif self.OD > 5:
      self.requiredRPS = 5 + 2.5 * (self.OD - 5) / 5
    else:
      self.requiredRPS = 5

    if 'Colours' in self.map:
      self.comboColors = [pgColor(*self.map['Colours'][color]) for color in self.map['Colors']]
    else:
      self.comboColors = []
      i = 1
      while f'Combo{i}' in self.skin['config']:
        self.comboColors.append(pgColor(*self.skin['config'][f'Combo{i}']))
        i += 1

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

    self.elementsScaleMultiplier = (self.circleRadius * 2) / self.skin['elements']['hitcircle'].get_width()

    self.hitcircleOverlay = self.skin['elements']['hitcircleoverlay']
    self.hitcircleOverlay = pgTransform.smoothscale_by(self.hitcircleOverlay, self.elementsScaleMultiplier)

    self.hitcircleCombos = []
    self.approachcircleCombos = []
    for i in range(len(self.comboColors)):
      self.hitcircleCombos.append(self.skin['elements']['hitcircle'].copy())

      self.hitcircleCombos[-1] = pgTransform.smoothscale_by(self.hitcircleCombos[-1], self.elementsScaleMultiplier)
      tintImage(self.hitcircleCombos[-1], self.comboColors[i])

      self.approachcircleCombos.append(self.skin['elements']['approachcircle'].copy())
      self.approachcircleCombos[-1] = pgTransform.smoothscale_by(self.approachcircleCombos[-1], self.elementsScaleMultiplier)

      tintImage(self.approachcircleCombos[-1], self.comboColors[i])

    for slider in self.sliders:
      timingPoints = self.effectiveTimingPointAtTime(slider.time)

      if timingPoints[1] is not None:
        SV = (.01 * timingPoints[1]['inverseSliderVelocityMultiplier']) + 1
        SV = 1 if SV <= 0 else SV
      else:
        SV = 1

      slider.slideTime = slider.length / (self.map['difficulty']['SliderMultiplier'] * 100 * SV) * timingPoints[0]['beatLength']

  def effectiveTimingPointAtTime(self, time: int) -> List[Dict[str, numType]]:
    possibleUninheritedTimingPoint = None
    possibleInheritedTimingPoint = None

    for timingPoint in self.map['timingPoints']:
      if timingPoint['time'] < time:
        if timingPoint['uninherited'] == 1:
          possibleUninheritedTimingPoint = deepcopy(timingPoint)
        else:
          possibleInheritedTimingPoint = deepcopy(timingPoint)
      break

    return [possibleUninheritedTimingPoint, possibleInheritedTimingPoint]

  def hitObjectsAtTime(self, time: int) -> List[Union[Hitcircle, Slider, Spinner]]:
    returnHitobjects = []

    timeClose = time + self.preempt
    timeOpenHitcircle = (time - self.hitWindow50) - self.objectFadeout

    for hitobject in self.hitobjects:
      if hitobject.time > timeClose: break
      if isinstance(hitobject, Hitcircle) and hitobject.time < timeOpenHitcircle: continue
      if isinstance(hitobject, Slider) and (hitobject.time + (hitobject.slideTime * hitobject.slides)) < time: continue
      if isinstance(hitobject, Spinner) and hitobject.endTime < time: continue

      returnHitobjects.append(hitobject)

    return returnHitobjects
