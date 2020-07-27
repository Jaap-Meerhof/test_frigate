# -*- coding: utf-8 -*-
"""
"""

import requests
import json

class WorkerStatsClient:

    def __init__(self, worker_host, worker_port):
        self.worker_uri = f"http://{worker_host}:{worker_port}"

    def get_stats(self):
                
        url = f"{self.worker_uri}/stats/"        
        r = requests.get(url)

        if r.status_code == 200:
            return json.loads(r.content)
        else:
            raise Exception(f"ERROR: Faust worker returned {r.status_code}")