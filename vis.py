import json
# from copy import copy
import pygame as pg
from modules.osuToJson import getJsonByOsu

def startMap(mapURL):
  pg.init()
  pg.mixer.init()

  ## setting up variables ##
  # icon = pg.image.load('assets/images/icon.png')
  # pg.display.set_icon(icon)

  pg.display.set_caption('test-1')

  time = pg.time

  clock = time.Clock()

  totalTime = time.get_ticks()

  bootTime = 0

  getBootTime = True

  fps = 60

  screenResMultiplier = 2

  screen_width, screen_height = 512*screenResMultiplier, 384*screenResMultiplier

  screen = pg.display.set_mode((screen_width, screen_height))

  map = json.loads(getJsonByOsu(mapURL))

  # hitobjectIndex = 0

  hitobjectList = []

  removeHitobjectsList = []

  hitobjectVisualWindow = 1000

  running = True
  while(running):
    if getBootTime:
      bootTime = time.get_ticks()
      getBootTime = False
    totalTime = time.get_ticks() - bootTime

    for event in pg.event.get():
      if event.type == pg.QUIT:
        running = False

    for i in range(len(hitobjectList)):
      if totalTime >= hitobjectList[i]:
        removeHitobjectsList.append(i)
        print(f'-{i}')

    for i in removeHitobjectsList:
      hitobjectList.remove(i)

    removeHitobjectsList = []

    for i in range(len(map['hitobjects'])):
      if totalTime >= map['hitobjects'][i]['time'] - hitobjectVisualWindow:
        hitobjectList.append(i)
        print(f'+{i}')

    pg.draw.rect(screen, '#000000', pg.Rect(0, 0, screen_width, screen_height))

    for i in hitobjectList:
      hitobjectX = map['hitobjects'][i]['x']*screenResMultiplier
      hitobjectY = map['hitobjects'][i]['y']*screenResMultiplier

      pg.draw.circle(screen, '#ff0000', (hitobjectX, hitobjectY), 50)

    # hitobject = map['hitobjects'][hitobjectIndex]
    # if (totalTime >= hitobject['time'] - hitobjectVisualWindow):
    #   hitobjectX = hitobject['x']*screenResMultiplier
    #   hitobjectY = hitobject['y']*screenResMultiplier

    #   # hitobjectColor = pg.color()

    #   pg.draw.circle(screen, '#ff0000', (hitobjectX, hitobjectY), 10)

    #   hitobjectIndex += 1

    #   if hitobjectIndex >= len(map['hitobjects']):
    #     running = False

    pg.display.flip()
    clock.tick(fps)

startMap('Ayane - GO Love&Peace (Gleipnir) [Insane].osu')