from typing import List, Union
from modules.misc.helpers import tintImage
from modules.readers.beatmapReader import readMap
from modules.beatmapElements.hitobjects import Hitcircle, Slider, Spinner
from modules.readers.importSkin import importSkin
from pygame import Color as pgColor, transform as pgTransform

class Beatmap:
  def __init__(self, mapURL: str, skinURL: str):
    self.mapDict = readMap(mapURL)
    self.skin = importSkin(skinURL, 'C:\\Users\\SPEED\\Documents\\GitHub\\osu-map-visualizer\\testFiles')

    self.totalHitobjects = len(self.mapDict['hitobjects'])
    self.hitcircles: List[Hitcircle] = []
    self.sliders: List[Slider] = []
    self.spinners: List[Spinner] = []
    self.hitobjects: List[Union[Hitcircle, Slider, Spinner]] = []

    for hitobject in self.mapDict['hitobjects']:
      if hitobject['type'] == 'hitcircle':
        self.hitobjects.append(Hitcircle(hitobject, self))
        self.hitcircles.append(self.hitobjects[-1])
      elif hitobject['type'] == 'slider':
        self.hitobjects.append(Slider(hitobject, self))
        self.sliders.append(self.hitobjects[-1])
      elif hitobject['type'] == 'spinner':
        self.hitobjects.append(Spinner(hitobject, self))
        self.spinners.append(self.hitobjects[-1])

    self.HP = self.mapDict['difficulty']['HPDrainRate']
    self.CS = self.mapDict['difficulty']['CircleSize']
    self.AR = self.mapDict['difficulty']['ApproachRate']
    self.OD = self.mapDict['difficulty']['OverallDifficulty']
    self.sliderMultiplier = self.mapDict['difficulty']['SliderMultiplier']
    self.sliderTickRate = self.mapDict['difficulty']['SliderTickRate']

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

    if 'Colours' in self.mapDict:
      self.comboColors = [pgColor(*self.mapDict['Colours'][color]) for color in self.mapDict['Colors']]
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

    self.elementsScaleMultiplier = self.circleRadius / self.skin['elements']['hitcircle'].get_width()

    self.hitcircleOverlay = self.skin['elements']['hitcircleoverlay']
    pgTransform.smoothscale_by(self.hitcircleOverlay, self.elementsScaleMultiplier)

    self.hitcircleCombos = []
    self.approachcircleCombos = []
    for i in range(len(self.comboColors)):
      self.hitcircleCombos.append(self.skin['elements']['hitcircle'].copy())

      pgTransform.smoothscale_by(self.hitcircleCombos[-1], self.elementsScaleMultiplier)
      tintImage(self.hitcircleCombos[-1], self.comboColors[i])

      self.approachcircleCombos.append(self.skin['elements']['approachcircle'].copy())
      tintImage(self.approachcircleCombos[-1], self.comboColors[i])

    # print(f'hitobjects: {self.totalHitobjects}, hitcircles: {self.totalHitcircles}, sliders: {self.totalSliders}, spinners: {self.totalSpinners}')

  def hitObjectsAtTime(self, time: int) -> List[Union[Hitcircle, Slider, Spinner]]:
    returnObjects = []
    timeStart = time
    timeEnd = time + self.preempt

    for hitObject in self.hitobjects:
      if hitObject.time < timeStart: continue
      elif hitObject.time > timeEnd: break
      else: returnObjects.append(hitObject)

    return returnObjects
