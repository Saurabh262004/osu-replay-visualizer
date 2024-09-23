import json
import os
# from copy import copy
import pygame as pg
from modules.helper import mapRange
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

  data = open('data/data.dat', 'r')

  osuURL = data.readline()

  mapURLs = [
    f'{osuURL}\\Songs\\{map['metadata']['BeatmapSetID']} {map['metadata']['Artist']} - {map['metadata']['Title']} [no video]',
    f'{osuURL}\\Songs\\{map['metadata']['BeatmapSetID']} {map['metadata']['Artist']} - {map['metadata']['Title']}',
    f'{osuURL}\\Songs\\{map['metadata']['BeatmapSetID']}'
  ]

  # check if map exists
  validMapURL = None

  for url in mapURLs:
    if (os.path.exists(url)):
      validMapURL = url

  if not validMapURL:
    print('map not found')
    return -1
  
  # check if audio file exists
  if not (os.path.isfile(f'{validMapURL}\\{map['audioFileName']}')):
    print('audio file not found')
    return -1
  
  audioURL = f'{validMapURL}\\{map['audioFileName']}'

  hitobjectList = []

  removeHitobjectsList = []

  hitobjectVisualWindow = 1000

  running = True
  while(running):
    if getBootTime:
      bootTime = time.get_ticks()
      getBootTime = False
      pg.mixer.music.load(audioURL)
      pg.mixer.music.play()

    totalTime = time.get_ticks() - bootTime

    for event in pg.event.get():
      if event.type == pg.QUIT:
        running = False

    for i in hitobjectList:
      if totalTime > map['hitobjects'][i]['time']:
        removeHitobjectsList.append(i)

    for i in removeHitobjectsList:
      hitobjectList.remove(i)

    removeHitobjectsList = []

    for i in range(len(map['hitobjects'])):
      if (totalTime >= map['hitobjects'][i]['time'] - hitobjectVisualWindow) and (totalTime <= map['hitobjects'][i]['time']):
        hitobjectList.append(i)

    pg.draw.rect(screen, '#000000', pg.Rect(0, 0, screen_width, screen_height))

    for i in hitobjectList:
      hitobjectX = map['hitobjects'][i]['x']*screenResMultiplier
      hitobjectY = map['hitobjects'][i]['y']*screenResMultiplier
      col = pg.Color(int(mapRange(map['hitobjects'][i]['time'] - totalTime, 0, 1000, 255, 0)), 0, 0)

      pg.draw.circle(screen, col, (hitobjectX, hitobjectY), int(mapRange(map['hitobjects'][i]['time'] - totalTime, 0, 1000, 0, 100)) + 60)
      pg.draw.circle(screen, '#000000', (hitobjectX, hitobjectY), int(mapRange(map['hitobjects'][i]['time'] - totalTime, 0, 1000, 0, 100)) + 54)
      pg.draw.circle(screen, col, (hitobjectX, hitobjectY), 50)

    pg.display.flip()
    clock.tick(fps)

startMap('map1.osu')