import pygame as pg
from appUI.colors import AppColors
from modules.UI.UIElements import DynamicValue as DV, Section, Circle, Slider, System
from modules.UI.windowManager import Window

def toggleActivation(system: System):
  system.elements['replayListButton'].active = not system.elements['replayListButton'].active

def addMain(window: Window):
  system = System(preLoadState=True)

  mainDim = {
    'x': DV('number', 0),
    'y': DV('number', 0),
    'width': DV('number', 0),
    'height': DV('number', 0)
  }

  system.addElement(
    Section(mainDim, AppColors.background1), 'mainSection'
  )

  # slider1 = Slider(
  #   'horizontal',
  #   Section(
  #     {
  #       'x': DV('classPer', system.elements['mainSection'], classAttr='width', percent=25),
  #       'y': DV('classPer', system.elements['mainSection'], classAttr='height', percent=70),
  #       'width': DV('classPer', system.elements['mainSection'], classAttr='width', percent=50),
  #       'height': DV('number', 8)
  #     }, AppColors.listElement1Heighlight1, 5
  #   ),
  #   Circle(
  #     {
  #       'x': DV('number', 0),
  #       'y': DV('number', 0),
  #       'radius': DV('number', 8)
  #     }, AppColors.primary1
  #   ),
  #   (0, 99),
  #   5,
  #   AppColors.primary1,
  #   {
  #     'callable': lambda param: print(f'slider value: {param}'),
  #     'params': None,
  #     'sendValue': True
  #   }
  # )

  # slider2 = Slider(
  #   'vertical',
  #   Section(
  #     {
  #       'x': DV('classPer', system.elements['mainSection'], classAttr='width', percent=90),
  #       'y': DV('classPer', system.elements['mainSection'], classAttr='height', percent=20),
  #       'width': DV('number', 8),
  #       'height': DV('classPer', system.elements['mainSection'], classAttr='height', percent=60)
  #     }, AppColors.listElement1Heighlight1
  #   ),
  #   Section(
  #     {
  #       'x': DV('number', 0),
  #       'y': DV('number', 0),
  #       'width': DV('number', 8),
  #       'height': DV('number', 14)
  #     }, AppColors.primary1
  #   ),
  #   (0, 99),
  #   -5,
  #   AppColors.listElement1Heighlight1,
  #   {
  #     'callable': lambda param: print(f'slider value: {param}'),
  #     'params': None,
  #     'sendValue': True
  #   }
  # )

  # system.addElement(slider1, 'newTestSlider1')
  # system.addElement(slider2, 'newTestSlider2')

  window.addSystem(system, 'main')
