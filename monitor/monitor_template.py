# -*- coding: utf-8 -*-
"""
"""

import pyqtgraph as pg
from pyqtgraph.Qt import QtCore, QtGui
import numpy as np

win = pg.GraphicsLayoutWidget(show=True)
win.setWindowTitle('Frigate Faust worker monitor')
 
class Plot:
    def __init__(self, win, left_label="", bottom_label="", new_row=False):
        if new_row:
            win.nextRow()
        self.p = win.addPlot()
        self.p.setLabels(left=left_label, bottom=bottom_label)        
        self.p.setDownsampling(mode='peak')
        self.p.setClipToView(True)
        self.curve = self.p.plot()
        self.ptr = 0        
        self.data = []
    
    def update(self):
        self.data.append(np.random.normal())
        self.ptr += 1    
        self.curve.setData(self.data[:self.ptr])

PLOTS = [ 
    Plot(win, left_label="y1", bottom_label="x1", new_row=True), Plot(win, bottom_label="x2", left_label="y2"), Plot(win, bottom_label="x3", left_label="y3"),
    Plot(win, left_label="y4", bottom_label="x4", new_row=True), Plot(win, bottom_label="x5", left_label="y5"), Plot(win, bottom_label="x6", left_label="y6"),
    Plot(win, left_label="y7", bottom_label="x7", new_row=True), Plot(win, bottom_label="x8", left_label="y8"), Plot(win, bottom_label="x9", left_label="y9")
]
   
# update all plots
def update():     
    for plot in PLOTS:
        plot.update()
    
timer = pg.QtCore.QTimer()
timer.timeout.connect(update)
timer.start(50)

## Start Qt event loop unless running in interactive mode or using pyside.
if __name__ == '__main__':
    import sys
    if (sys.flags.interactive != 1) or not hasattr(QtCore, 'PYQT_VERSION'):
        QtGui.QApplication.instance().exec_()
s