import json
import logging
import requests
from configuration import ENDPOINT_SERVER_HOST, ENDPOINT_SERVER_PORT


logging.basicConfig(level=logging.WARNING,
                    format='%(asctime)s - %(levelname)s - %(name)s - %(message)s'
                    )
logger = logging.getLogger(__name__)


#TODO: load this configuration from a common module
#ENDPOINT_SERVER_HOST = "localhost"
#ENDPOINT_SERVER_PORT = 5000 
 
class EndPointClient():

    def __init__(self):
        self.endpoint_server_string = "http://%s:%d" % (ENDPOINT_SERVER_HOST, int(ENDPOINT_SERVER_PORT))

    def send_status(self, vehicle_id, edge_id, speed, dest_edge_id):
        
        payload = {"vehicle_id":vehicle_id, "edge_id": edge_id, "speed": speed, "dest_edge_id": dest_edge_id}
        url = "%s/status" % (self.endpoint_server_string)

        logger.info('sending: %s'%json.dumps(payload))
        r = requests.post(url, json=payload)

        if r.status_code == 200:
            return True
        else:
            raise Exception("ERROR: EndPoint Server returned %d" %
                            r.status_code)

    def send_qtable_init_request(self):
                
        url = "%s/qtableinit" % (self.endpoint_server_string)

        logger.info('requesting Q-Table initialization')
        r = requests.get(url)

        if r.status_code == 200:
            return True
        else:
            raise Exception("ERROR: EndPoint Server returned %d" %
                            r.status_code)

    def is_qtable_initialized(self):
        
        url = "%s/isqtableinitialized" % (self.endpoint_server_string)
        logger.info('querying to see if the Q-Table is fully initialized')
        r = requests.get(url)

        if r.status_code == 200:            
            return json.loads(r.content)["initialized"]
        else:
            raise Exception("ERROR: EndPoint Server returned %d" %
                            r.status_code)

    def get_qtable_entry(self, node_id):
        
        payload = {"node_id":node_id}
        url = "%s/qtable" % (self.endpoint_server_string)

        logger.info(f'requesting the Q-Table entry for {node_id}')
        r = requests.post(url, json=payload)

        if r.status_code == 200:
            return json.loads(r.content)
        else:
            raise Exception("ERROR: EndPoint Server returned %d" %
                            r.status_code)
    
    def get_vehicle_table_entry(self, vehicle_id):
        
        payload = {"vehicle_id":vehicle_id}
        url = "%s/vehicle" % (self.endpoint_server_string)

        logger.info(f'requesting the Vehicle Table entry for {vehicle_id}')
        r = requests.post(url, json=payload)

        if r.status_code == 200:
            return json.loads(r.content)
        else:
            raise Exception("ERROR: EndPoint Server returned %d" %
                            r.status_code)

    def get_vehicle_table_entries(self, vehicle_ids):
        #TODO: move this logic to the EndPoint Server
        table_entries = []
        for vehicle_id in vehicle_ids:  
            table = self.get_vehicle_table_entry(vehicle_id)
            logger.info(table)
            table = json.loads(table)[vehicle_id]
            table["vehicle_id"] = vehicle_id
            table_entries.append(table)
        return table_entries
        
  
    def send_vehicles_initialization(self, vehicle_ids):
        
        url = "%s/vehiclesinit" % (self.endpoint_server_string)
        logger.info('requesting vehicles initialization')
        payload = {"vehicle_ids" : vehicle_ids}
        r = requests.post(url, json=payload)

        if r.status_code == 200:
            return True
        else:
            raise Exception("ERROR: EndPoint Server returned %d" %
                            r.status_code)
    

    def are_vehicles_initialized(self, vehicle_ids):
        
        url = "%s/arevehiclesinitialized" % (self.endpoint_server_string)
        logger.info('querying to see if the entries of the vehicles are in the Vehicle Table')
        payload = {"vehicle_ids" : vehicle_ids}
        r = requests.post(url, json=payload)

        if r.status_code == 200:            
            return json.loads(r.content)["initialized"]
        else:
            raise Exception("ERROR: EndPoint Server returned %d" %
                            r.status_code)

    def have_vehicles_arrived(self, vehicle_ids):
        
        url = "%s/havearrived" % (self.endpoint_server_string)
        logger.info('querying for arrivals ...')
        payload = {"vehicle_ids" : vehicle_ids}
        r = requests.post(url, json=payload)

        if r.status_code == 200:            
            return json.loads(r.content)
        else:
            raise Exception("ERROR: EndPoint Server returned %d" %
                            r.status_code)


    def send_arrival_notifications(self, vehicle_ids):
                
        url = "%s/arrival" % (self.endpoint_server_string)

        logger.info('sending arrival notifications')
        payload = {"vehicle_ids": vehicle_ids}
        r = requests.post(url, json=payload)

        if r.status_code == 200:
            return True
        else:
            raise Exception("ERROR: EndPoint Server returned %d" %
                            r.status_code)               
    

    def get_route(self, source_edge_id, dest_edge_id):
        
        url = "%s/route" % (self.endpoint_server_string)
        logger.info(f'querying route from {source_edge_id} to {dest_edge_id}')
        payload = {"source_edge_id" : source_edge_id,
                    "dest_edge_id" : dest_edge_id
        }
        r = requests.post(url, json=payload)
        logger.info("returned: {r.content}")

        if r.status_code == 200:            
            return json.loads(r.content)
        else:
            raise Exception("ERROR: EndPoint Server returned %d" %
                            r.status_code)