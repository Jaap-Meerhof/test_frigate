# -*- coding: utf-8 -*-
"""
"""

import requests
import json

class FrigateMonitorClient:

    def __init__(self, monitor_host, monitor_port):
        self.monitor_uri = f"http://{monitor_host}:{monitor_port}"

    def start_monitor(self):
                
        url = f"{self.monitor_uri}/start"
        r = requests.get(url)

        if r.status_code == 200:
            return True
        elif r.status_code == 201:
            return False
        else:
            raise Exception(f"ERROR: Frigate Monitor returned {r.status_code}")
