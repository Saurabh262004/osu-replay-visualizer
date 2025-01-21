from appUI.colors import AppColors
from modules.UI.UIElements import DynamicValue as DV, Section, System
from modules.UI.windowManager import Window

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

  window.addSystem(system, 'settings')
