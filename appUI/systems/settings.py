from appUI.colors import AppColors
from modules.UI.UIElements import DynamicValue as DV, Section, System, TextBox, Toggle
from modules.UI.windowManager import Window

def addOption(text: str, id: str, pos: int, callback: callable, callbackParams, system: System, window: Window):
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

def addSettings(window: Window):
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
  addOption(hqSliderOptionText, 't1', 1, changeUserData, (window.customData['userData'], 'highQualitySliders'), system, window)
  system.elements['t1-tgl'].toggled = window.customData['userData']['highQualitySliders']
  system.elements['t1-tgl'].updateInnerBox()

  addOption('Display Playfield Border', 't2', 2, changeUserData, (window.customData['userData'], 'playfieldBorder'), system, window)
  system.elements['t2-tgl'].toggled = window.customData['userData']['playfieldBorder']
  system.elements['t2-tgl'].updateInnerBox()

  addOption('Render Default Skin Cursor', 't3', 3, changeUserData, (window.customData['userData'], 'renderSkinCursor'), system, window)
  system.elements['t3-tgl'].toggled = window.customData['userData']['renderSkinCursor']
  system.elements['t3-tgl'].updateInnerBox()

  addOption('Render Cursor Tracker', 't4', 4, changeUserData, (window.customData['userData'], 'renerCursorTracker'), system, window)
  system.elements['t4-tgl'].toggled = window.customData['userData']['renerCursorTracker']
  system.elements['t4-tgl'].updateInnerBox()

  addOption('Render Hit Judgments', 't5', 5, changeUserData, (window.customData['userData'], 'renderHitJudgments'), system, window)
  system.elements['t5-tgl'].toggled = window.customData['userData']['renderHitJudgments']
  system.elements['t5-tgl'].updateInnerBox()

  window.addSystem(system, 'settings')
