from flask import Flask, Response
import logging
import json
from configuration import SIMULATOR_SERVER_HOST, SIMULATOR_SERVER_PORT
from simulator import run_simulation

app = Flask(__name__)

logging.basicConfig(level=logging.DEBUG,
                    format='%(asctime)s - %(levelname)s - %(name)s - %(message)s'
                    )
logger = logging.getLogger(__name__)


@app.route('/')
def hello_world():
    return 'Hello, this is the Simulator HTTP Server!'


@app.route('/run', methods=['GET'])
def run():
    logger.info("/run")
    try:
        for res in run_simulation(step_by_step=False):            
            logger.info(res)
        json_dump = json.dumps( {"result":"success", "message": "OK"} )
        return Response(response=json_dump, status=200)                
    except Exception as e:
        json_dump = json.dumps( {"result":"error", "message": str(e)} )
        return Response(response=json_dump, status=200)

@app.route('/stream', methods=['GET'])
def run_stream():
    def generator():
        for res in run_simulation(step_by_step=True):
            yield json.dumps(res) + "\n"                       
    logger.info("/stream")        
    try:
        return Response(response=generator(), content_type="text/event-stream", headers={'X-Accel-Buffering': 'no'})                     
    except Exception as e:
        json_dump = json.dumps( {"result":"error", "message": str(e)} ) + "\n"
        return Response(response=json_dump, status=200)
         
if __name__ == '__main__':
    logger.info(f"starting Simulator Server ...")
    app.run(host=SIMULATOR_SERVER_HOST, port=int(SIMULATOR_SERVER_PORT))
