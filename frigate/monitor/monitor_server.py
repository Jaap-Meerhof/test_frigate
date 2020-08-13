from flask import Flask, Response, request
import logging
import time
import threading
import json
from configuration import STATSD_METRICS, OUTPUT_FOLDER, GRAPHITE_HOST, GRAPHITE_PORT
from graphite_client import GraphiteClient

app = Flask(__name__)

logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s - %(levelname)s - %(name)s - %(message)s'
                    )
logger = logging.getLogger(__name__)

monitor_thread = None

graphite_client = GraphiteClient(
    graphite_host=GRAPHITE_HOST, graphite_port=GRAPHITE_PORT)


def monitor_thread_fun():

    global graphite_client

    logging.info("[monitor_thread_fun] Monitor thread starting ...")
    while True:
        for metric in STATSD_METRICS:
            logging.info(f"[monitor_thread_fun] gathering metric {metric} ...")
            res = graphite_client.get_metric_json(metric)
            res_json = json.dumps(res)
            logging.info(f"[monitor_thread_fun] saving ...")
            filep = open(f"{OUTPUT_FOLDER}/{metric}.json", "w+")
            filep.write(res_json)
            filep.flush()
            filep.close()
        logging.info(f"[monitor_thread_fun] sleeping ...")
        time.sleep(1)


@app.route('/')
def hello_world():
    return 'Hello, this is the Monitor Server!'


@app.route('/start', methods=['GET'])
def start():
    global monitor_thread

    logger.info("[start] /start")

    if monitor_thread:

        logger.info(
            "[start] monitor thread is already runnning! doing nothing.")
        json_str = json.dumps({"message": "ALREADY_RUNNING"})
        return Response(response=json_str, status=201)

    else:

        logger.info("[start] starting monitor thread ...")
        monitor_thread = threading.Thread(
            target=monitor_thread_fun, daemon=True)
        monitor_thread.start()
        logger.info("[start] monitor thread started!")
        json_str = json.dumps({"message": "STARTED"})
        return Response(response=json_str, status=200)


if __name__ == '__main__':
    logger.info(f"starting Monitor Server ...")
    app.run(host="0.0.0.0", port=83)
