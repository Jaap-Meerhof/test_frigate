# -*- coding: utf-8 -*-
"""
"""

import numpy as np

class WorkerStatPlot:
    def __init__(self, win, stats_client, stat_name, left_label="", bottom_label="", new_row=False):
        if new_row:
            win.nextRow()
        self.stats_client = stats_client
        self.stat_name = stat_name
        self.p = win.addPlot()
        self.p.setLabels(left=left_label, bottom=bottom_label)        
        self.p.setDownsampling(mode='peak')
        self.p.setClipToView(True)
        self.curve = self.p.plot()
        self.ptr = 0        
        self.data = []
    
    def update(self):
        stats = self.stats_client.get_stats()["Sensor0"]
        self.data.append(float(stats[self.stat_name]))
        self.ptr += 1    
        self.curve.setData(self.data[:self.ptr])