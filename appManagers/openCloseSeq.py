from typing import Union
import os
import json
from time import sleep
from easygui import diropenbox

def validOsuURL(url: str) -> bool:
  testURLs = [
    os.path.join(url, 'osu!.exe'),
    os.path.join(url, 'osu!.db'),
    os.path.join(url, 'Songs'),
  ]

  for testURL in testURLs:
    if not os.path.exists(testURL): return False

  return True

# try to find the osu! installation and return all the urls of installations found else return False
def detectOsuFolder() -> Union[str, bool]:
  usersFolder = 'C:\\Users'

  allUsers = os.listdir(usersFolder)

  allPossibleURLs = []

  for user in allUsers:
    appDataFolder = os.path.join(usersFolder, user, 'AppData')

    if os.path.exists(appDataFolder):
      appDataScopeFolders = os.listdir(appDataFolder)

      for appDataScope in appDataScopeFolders:
        allPossibleURLs.append(os.path.join(appDataFolder, appDataScope, 'osu!'))

  allValidURLs = []

  for possibleURL in allPossibleURLs:
    if os.path.exists(possibleURL):
      allValidURLs.append(possibleURL)

  allOsuFolders = []

  for validURL in allValidURLs:
    if validOsuURL(validURL):
      allOsuFolders.append(validURL)

  if len(allOsuFolders) > 0: return allOsuFolders
  return False

# setup userdata on the first boot on the device
def firstBootSetup(userData: dict):
  detectedOsuFolders = detectOsuFolder()

  folderPath = ""
  if not detectedOsuFolders:
    while not validOsuURL(folderPath):
      folderPath = diropenbox('Could not detect your osu! installation! please select your osu! folder.')
  else:
    folderPath = detectedOsuFolders[0]

  userData['URLs']['osuFolder'] = folderPath
  print('Selected osu! Folder:', folderPath)

  userData['firstBoot'] = False

# save the user data and close the application
def closingSetup(userData: dict):
  print('closing the application...')

  userDataFilePath = 'data/userData.json'

  os.makedirs(os.path.dirname(userDataFilePath), exist_ok=True)

  saveAttempts = 2
  for attempt in range(saveAttempts):
    try:
      with open(userDataFilePath, 'w') as userDataFile:
        userDataFile.write(json.dumps(userData, indent=2))

        print('Successfully updated user data.')
        break
    except Exception as e:
      print(f'Failed to save user data: {e}')

      if attempt < saveAttempts - 1:
        print('trying again in 1 second...')
        sleep(1)
      else:
        print(e)
        print("Exiting the app anyway.")
