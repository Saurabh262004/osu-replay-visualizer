import sharedWindow
from modules.UI.windowManager import Window

def activateAlert(alertText: str):
  window: Window = sharedWindow.window

  window.systems['main'].elements['alertBox'].activeDraw = True
  window.systems['main'].elements['alertIcon'].activeDraw = True
  alertTextElement = window.systems['main'].elements['alertText']

  alertTextElement.activeDraw = True
  alertTextElement.text = alertText
  alertTextElement.update()

def deactivateAlert():
  window: Window = sharedWindow.window

  window.systems['main'].elements['alertBox'].active = False
  window.systems['main'].elements['alertIcon'].active = False
  window.systems['main'].elements['alertText'].active = False
