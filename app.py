import os
import json
from modules.UI.windowManager import Window
from appUI.systems.nav import addNav
from appUI.systems.main import addMain
from appUI.systems.replayList import addReplayList
from appUI.systems.settings import addSettings

def systemSwitch():
  if not window.loggedSystemSwitch is None:

    if window.loggedSystemSwitch in window.activeSystems:
      return None

    deavtivateSystemIDs = []

    for activeSystemID in window.activeSystems:
      if activeSystemID != 'nav':
        deavtivateSystemIDs.append(activeSystemID)

    window.deactivateSystems(deavtivateSystemIDs)
    window.activateSystems(window.loggedSystemSwitch)

    window.loggedSystemSwitch = None

def windowCustomLoop():
  systemSwitch()

userData = None
with open('data/userData.json', 'r') as rawData:
  userData = json.load(rawData)

for url in userData['URLs']:
  if not os.path.isdir(userData['URLs'][url]):
    print(f'The {url} : {userData['URLs'][url]} is not a valid url.')
    # do something

window = Window('Replay Veiwer', (800, 450), customLoopProcess=windowCustomLoop)

## add systems ##
addNav(window)
addMain(window)
addReplayList(window, userData)
addSettings(window)

## define system z indexes ##
window.setSystemZ('nav', 9)
window.setSystemZ('main', 0)
window.setSystemZ('replayList', 1)
window.setSystemZ('settings', 2)

window.activateSystems(['nav', 'main'])

window.openWindow()
