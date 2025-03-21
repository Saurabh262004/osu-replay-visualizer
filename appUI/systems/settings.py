import os
from easygui import diropenbox
from modules.readers.importSkin import importSkin
from appUI.colors import AppColors
from modules.UI.UIElements import DynamicValue as DV, Section, System, TextBox, Toggle, Button
from modules.UI.windowManager import Window
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
    deactivateAlert()
  except Exception as e:
    print(e)

def addOption(text: str, id: str, pos: int, callback: callable, callbackParams, system: System):
  window: Window = sharedWindow.window

  optionToggleSectionWidth = DV('classPer', window, classAttr='screenHeight', percent=6)

  optionToggleSection = Section(
    {
      'x': DV('classPer', window, classAttr='screenWidth', percent=2),
      'y': DV('customCallable', lambda params: ((params[1] * params[2].value)) + params[0].height + 5, (window.systems['nav'].elements['topNav'], pos, optionToggleSectionWidth)),
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

  hqSliderOptionText = 'High Quality Sliders *might take a long time to process on slow devices*'
  addOption(hqSliderOptionText, 't1', 1, changeUserData, (window.customData['userData'], 'highQualitySliders'), system)
  system.elements['t1-tgl'].toggled = window.customData['userData']['highQualitySliders']
  system.elements['t1-tgl'].updateInnerBox()

  addOption('Display Playfield Border', 't2', 2, changeUserData, (window.customData['userData'], 'playfieldBorder'), system)
  system.elements['t2-tgl'].toggled = window.customData['userData']['playfieldBorder']
  system.elements['t2-tgl'].updateInnerBox()

  addOption('Display Sldier Anchors', 't3', 3, changeUserData, (window.customData['userData'], 'sliderAnchors'), system)
  system.elements['t3-tgl'].toggled = window.customData['userData']['sliderAnchors']
  system.elements['t3-tgl'].updateInnerBox()

  addOption('Render Default Skin Cursor', 't4', 4, changeUserData, (window.customData['userData'], 'renderSkinCursor'), system)
  system.elements['t4-tgl'].toggled = window.customData['userData']['renderSkinCursor']
  system.elements['t4-tgl'].updateInnerBox()

  addOption('Render Cursor Tracker', 't5', 5, changeUserData, (window.customData['userData'], 'renerCursorTracker'), system)
  system.elements['t5-tgl'].toggled = window.customData['userData']['renerCursorTracker']
  system.elements['t5-tgl'].updateInnerBox()

  addOption('Render Hit Judgments', 't6', 6, changeUserData, (window.customData['userData'], 'renderHitJudgments'), system)
  system.elements['t6-tgl'].toggled = window.customData['userData']['renderHitJudgments']
  system.elements['t6-tgl'].updateInnerBox()

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

  window.addSystem(system, 'settings')
