# -*- coding: utf-8 -*-
"""
"""

import sys
import pyqtgraph as pg
from pyqtgraph.Qt import QtCore, QtGui
from .monitor_client import WorkerStatsClient
from .monitor_plot import WorkerStatPlot

win = pg.GraphicsLayoutWidget(show=True)
win.setWindowTitle('Faust worker monitor')

stats_client_worker1 = WorkerStatsClient("localhost", 6066)
stats_client_worker2 = WorkerStatsClient("localhost", 6067)

PLOTS = [
    # row 1
    WorkerStatPlot(win, stats_client=stats_client_worker1,
                   stat_name="events_active", left_label="events_active", bottom_label="time", new_row=True),
    WorkerStatPlot(win, stats_client=stats_client_worker1,
                   stat_name="events_total", left_label="events_total", bottom_label="time"),
    WorkerStatPlot(win, stats_client=stats_client_worker1,
                   stat_name="events_s", left_label="events_s", bottom_label="time"),
    WorkerStatPlot(win, stats_client=stats_client_worker1,
                   stat_name="events_runtime_avg", left_label="events_runtime_avg", bottom_label="time"),
    # row 2
    WorkerStatPlot(win, stats_client=stats_client_worker2,
                   stat_name="events_active", left_label="events_active", bottom_label="time", new_row=True),
    WorkerStatPlot(win, stats_client=stats_client_worker2,
                   stat_name="events_total", left_label="events_total", bottom_label="time"),
    WorkerStatPlot(win, stats_client=stats_client_worker2,
                   stat_name="events_s", left_label="events_s", bottom_label="time"),
    WorkerStatPlot(win, stats_client=stats_client_worker2,
                   stat_name="events_runtime_avg", left_label="events_runtime_avg", bottom_label="time")
]


def update():
    """
    Update all plots.
    """
    for plot in PLOTS:
        plot.update()


# Start Qt event loop unless running in interactive mode or using pyside.
if __name__ == '__main__':

    timer = pg.QtCore.QTimer()
    timer.timeout.connect(update)
    timer.start(50)

    if (sys.flags.interactive != 1) or not hasattr(QtCore, 'PYQT_VERSION'):
        QtGui.QApplication.instance().exec_()
