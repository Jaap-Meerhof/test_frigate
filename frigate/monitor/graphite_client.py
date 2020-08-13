# -*- coding: utf-8 -*-
"""
"""

import requests
import json
import logging

logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s - %(levelname)s - %(name)s - %(message)s'
                    )
logger = logging.getLogger(__name__)

class GraphiteClient:

    def __init__(self, graphite_host, graphite_port):
        self.graphite_host = graphite_host
        self.graphite_port = graphite_port

    def get_metric_json(self, metric, from_time="-1hours"):

        request_url = f"http://{self.graphite_host}:{self.graphite_port}/render?from={from_time}&until=now&target={metric}&format=json"
        logger.info(f"[get_metric_json] requesting: {request_url}")

        r = requests.get(request_url)

        if r.status_code == 200:
            return json.loads(r.content)
        else:
            raise Exception(f"ERROR: Graphite server returned {r.status_code}")

    