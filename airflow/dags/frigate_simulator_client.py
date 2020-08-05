# -*- coding: utf-8 -*-
"""
"""

import requests
import json

class FrigateSimulatorClient:

    def __init__(self, simulator_host, simulator_port):
        self.worker_uri = f"http://{simulator_host}:{simulator_port}"

    def run(self):
                
        url = f"{self.worker_uri}/run"
        r = requests.get(url)

        if r.status_code == 200:
            return json.loads(r.content)
        else:
            raise Exception(f"ERROR: Frigate simulator returned {r.status_code}")

    def initialize_qtable(self):
                
        url = f"{self.worker_uri}/init"
        r = requests.get(url)

        if r.status_code == 200:
            return json.loads(r.content)
        else:
            raise Exception(f"ERROR: Frigate simulator returned {r.status_code}")

    def run_stream(self):
        """
        NOTE: this is a generator.
        """
        url = f"{self.worker_uri}/stream"
        r = requests.get(url, stream=True, timeout=None)
        if r.encoding is None:
            r.encoding = 'utf-8'
        if r.status_code == 200:
            try:
                lines = r.iter_lines(decode_unicode=True)
                first_line = next(lines)
                if first_line:
                    obj = json.loads(first_line)
                    yield obj
                for line in lines: # produce one object at a time
                    if line: # filter out keep-alive new lines                    
                        obj = json.loads(line)
                        yield obj
            except Exception as e:
                raise Exception(f"ERROR: Error while iterating through the stream. Last line: {line}. Error message: {e}")
        else:
            raise Exception(f"ERROR: Frigate simulator returned {r.status_code}")