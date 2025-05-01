import os
from typing import Union, List
from easygui import diropenbox, fileopenbox
from modules.readers.importSkin import importSkin
from appUI.colors import AppColors
from modules.UI.UIElements import DynamicValue as DV, Section, System, TextBox, Toggle, Button, Slider
from modules.UI.windowManager import Window
from replayHandlers.loader import loadRendererWithReplay
from appManagers.manageAlerts import deactivateAlert
import sharedWindow

def changeSkin():
  window: Window = sharedWindow.window
  skinURL = ''

  skinURL = diropenbox('Please select a valid skin folder')

  if skinURL is not None:
    skinName = os.path.basename(skinURL)
  else:
    return

  try:
    window.customData['skin'] = importSkin(skinName, 'assets/defaultSkin', window.customData['userData']['URLs']['osuFolder'])
    window.customData['userData']['skin'] = skinName

    for hitsound in window.customData['skin']['hitsounds']:
      window.customData['skin']['hitsounds'][hitsound].set_volume(window.customData['userData']['volume'] / 3)

    deactivateAlert()
  except Exception as e:
    if window.customData['debug']:
      print(e)

def loadDefaultSkin():
  window: Window = sharedWindow.window

  try:
    window.customData['skin'] = importSkin('assets/defaultSkin', 'assets/defaultSkin', window.customData['userData']['URLs']['osuFolder'], True)
    window.customData['userData']['skin'] = 'default'

    for hitsound in window.customData['skin']['hitsounds']:
      window.customData['skin']['hitsounds'][hitsound].set_volume(window.customData['userData']['volume'] / 3)

    deactivateAlert()
  except Exception as e:
    if window.customData['debug']:
      print(e)

def loadReplay():
  replayURL: str = fileopenbox('Please select a replay file to load')

  if replayURL is not None and replayURL.endswith('.osr'):
    loadRendererWithReplay(customURL=replayURL)
  else:
    return

numType = Union[int, float]
def getOptionYpos(optionNumber: numType) -> numType:
  window: Window = sharedWindow.window
  scrollOffset: numType = 0

  if 'settings' in window.systems and 'optionScroller' in window.systems['settings'].elements:
    scrollOffset = window.systems['settings'].elements['optionScroller'].value

  actualPosition = optionNumber - scrollOffset
  toggleHeight = (window.screenHeight / 100) * 3
  relativePadding = toggleHeight
  absolutePadding = window.systems['nav'].elements['topNav'].height + relativePadding

  return (actualPosition * (toggleHeight + relativePadding)) + absolutePadding

def getScrollerHeight():
  window: Window = sharedWindow.window
  navHeight = window.systems['nav'].elements['topNav'].height
  bottomPadding = window.screenHeight / 10
  
  return (window.screenHeight - navHeight) - bottomPadding

def addOption(text: str, pos: int, toggleID: str, system: System):
  window: Window = sharedWindow.window
  callbackParams = [window.customData['userData'], toggleID]
  id = f't{pos}'
  callback = changeUserData

  optionToggleSectionWidth = DV('classPer', window, classAttr='screenHeight', percent=6)

  optionToggleSection = Section(
    {
      'x': DV('classPer', window, classAttr='screenWidth', percent=2),
      'y': DV('customCallable', getOptionYpos, pos),
      'width': optionToggleSectionWidth,
      'height': DV('classPer', optionToggleSectionWidth, classAttr='value', percent=50)
    },
    AppColors.listElement1Heighlight2,
    10
  )

  optionToggle = Toggle(
    optionToggleSection,
    AppColors.gray,
    None,
    None,
    callback,
    callbackParams,
    True,
    0
  )

  system.addElement(optionToggle, f'{id}-tgl')

  textBoxSection = Section(
    {
      'x': DV('customCallable', lambda toggleSection: toggleSection.x + toggleSection.width + 10, optionToggleSection),
      'y': DV('customCallable', lambda toggleSection: toggleSection.y - (toggleSection.height * .35), optionToggleSection),
      'width': DV('number', 200),
      'height': DV('classPer', optionToggleSection, classAttr='height', percent=170)
    },
    AppColors.gray
  )

  optionText = TextBox(
    textBoxSection,
    text,
    'helvetica',
    AppColors.gray,
    False,
    False
  )

  system.addElement(optionText, f'{id}-txt')

  system.elements[f'{id}-tgl'].toggled = window.customData['userData'][callbackParams[1]]
  system.elements[f'{id}-tgl'].updateInnerBox()

def toggleHighQualitySliders(userData: dict, val: bool):
  userData['highQualitySliders'] = val

def togglePlayfieldBorder(userData: dict, val: bool):
  userData['playfieldBorder'] = val

def changeUserData(userDataAndKey, val):
  userDataAndKey[0][userDataAndKey[1]] = val

def addSettings():
  window: Window = sharedWindow.window

  system = System(preLoadState=True)

  system.addElement(
    Section({
      'x': DV('number', 1),
      'y': DV('number', 1),
      'width': DV('number', 1),
      'height': DV('number', 1)
    }, AppColors.background1), 'mainSection'
  )

  togglesInfo = [
    {
      'text': 'High Quality Sliders *might take a long time to process on slow devices*',
      'id': 'highQualitySliders'
    },
    {
      'text': 'Display playfield border',
      'id': 'playfieldBorder'
    },
    {
      'text': 'Display sldier anchors',
      'id': 'sliderAnchors'
    },
    {
      'text': 'Render default skin cursor',
      'id': 'renderSkinCursor'
    },
    {
      'text': 'Render cursor tracker',
      'id': 'renderCursorTracker'
    },
    {
      'text': 'Render hit judgments *not fully implemented yet*',
      'id': 'renderHitJudgments'
    },
    {
      'text': 'Render key overlay',
      'id': 'renderKeyOverlay'
    },
    {
      'text': 'Show mods',
      'id': 'renderModsDisplay'
    },
    {
      'text': 'Only play normal hitsounds',
      'id': 'normalHitsounds'
    }
  ]

  optionScrollerSectionDim = {
    'x': DV('customCallable', lambda mainSection: mainSection.width - 8, system.elements['mainSection']),
    'y': DV('classNum', window.systems['nav'].elements['topNav'], classAttr='height'),
    'width': DV('number', 8),
    'height': DV('customCallable', getScrollerHeight)
  }

  optionScrollerDragDim = {
    'x': DV('number', 0),
    'y': DV('number', 0),
    'width': DV('number', 8),
    'height': DV('number', 16)
  }

  optionScroller = Slider(
    'vertical',
    Section(optionScrollerSectionDim, AppColors.listElement1),
    Section(optionScrollerDragDim, AppColors.primary1),
    (0, len(togglesInfo)-1),
    -2,
    AppColors.listElement1,
    {
      'callable': system.update,
      'params': None,
      'sendValue': False
    },
    False
  )

  system.addElement(optionScroller, 'optionScroller')

  for i, toggleInfo in enumerate(togglesInfo):
    addOption(toggleInfo['text'], i, toggleInfo['id'], system)

  buttonsSectionDim = {
    'x': DV('number', 0),
    'y': DV('classPer', window, classAttr='screenHeight', percent=90),
    'width': DV('classNum', window, classAttr='screenWidth'),
    'height': DV('classPer', window, classAttr='screenHeight', percent=10)
  }

  buttonsSection = Section(
    buttonsSectionDim,
    AppColors.listElement1
  )

  system.addElement(buttonsSection, 'buttonsSection')

  LSK_HEIGHT = DV('classPer', window, classAttr='screenHeight', percent=5)
  LSK_WIDTH = DV('classPer', LSK_HEIGHT, classAttr='value', percent=320)
  LSK_Y = DV('customCallable', lambda params: params[0].screenHeight - (params[1].value * 1.5), callableParameters=(window, LSK_HEIGHT))
  LSK_X = DV('customCallable', lambda params: params[0].screenWidth - params[1].value - (params[2].value * .5), callableParameters=(window, LSK_WIDTH, LSK_HEIGHT))

  loadSkinDim = {
    'x': LSK_X,
    'y': LSK_Y,
    'width': LSK_WIDTH,
    'height': LSK_HEIGHT
  }

  loadSkinBTN = Button(
    Section(loadSkinDim, AppColors.gray, 3),
    AppColors.darkGray,
    None,
    None,
    'Change Skin',
    'Helvetica',
    AppColors.background1,
    changeSkin
  )

  system.addElement(loadSkinBTN, 'loadSkinBTN')

  loadReplayDim = {
    'x': DV('customCallable', lambda params: params[0].value - (params[1].value * 1.1), callableParameters=(LSK_X, LSK_WIDTH)),
    'y': LSK_Y,
    'width': LSK_WIDTH,
    'height': LSK_HEIGHT
  }

  loadReplayBTN = Button(
    Section(loadReplayDim, AppColors.gray, 3),
    AppColors.darkGray,
    None,
    None,
    'Load Replay',
    'Helvetica',
    AppColors.background1,
    loadReplay
  )

  system.addElement(loadReplayBTN, 'loadReplayBTN')

  defaultSkinDim = {
    'x': DV('customCallable', lambda params: params[0].value - (params[1].value * 2.5), callableParameters=(LSK_X, LSK_WIDTH)),
    'y': LSK_Y,
    'width': DV('classPer', LSK_WIDTH, classAttr='value', percent=130),
    'height': LSK_HEIGHT
  }

  defaultSkinBTN = Button(
    Section(defaultSkinDim, AppColors.gray, 3),
    AppColors.darkGray,
    None,
    None,
    'Load Default Skin',
    'Helvetica',
    AppColors.background1,
    loadDefaultSkin
  )

  system.addElement(defaultSkinBTN, 'defaultSkinBTN')

  window.addSystem(system, 'settings')
