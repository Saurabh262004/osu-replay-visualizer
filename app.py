import os
import json
from appUI.windowManager import Window
from appUI.main import addMain
from appUI.replayList import addReplayList

try:
  with open('data/userData.json', 'r') as rawData:
    userData = json.load(rawData)

    for url in userData['URLs']:
      if not os.path.isdir(userData['URLs'][url]):
        print(f'The {url} : {userData['URLs'][url]} is not a valid url.')
        # do something

    window = Window('Replay Veiwer', (800, 450))

    addMain(window)

    addReplayList(window, userData)

    window.openWindow('replayList')
except Exception as e:
  # do something
  print(e)
