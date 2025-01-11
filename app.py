from appUI.windowManager import Window
from appUI.main import addMain
from appUI.replayList import addReplayList

window = Window('Replay Veiwer', (800, 450))

addMain(window)

addReplayList(window)

window.openWindow('main')
