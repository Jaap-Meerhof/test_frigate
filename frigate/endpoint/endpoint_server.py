from flask import Flask, Response, request
import os
import sys
import json
import logging
import requests
import pprint
from configuration import SUMO_TOOLS_HOME, KAFKA_BROKER_URL, STREAM_SERVICE_WEB_URL, SUMO_ROADNET_PATH, ENDPOINT_SERVER_HOST, ENDPOINT_SERVER_PORT
from kafka import KafkaProducer

app = Flask(__name__)

logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s - %(levelname)s - %(name)s - %(message)s'
                    )
logger = logging.getLogger(__name__)

sys.path.append(SUMO_TOOLS_HOME)
import sumolib

#TODO: load this configuration from a common module
#KAFKA_BROKER_URL = "localhost:9092"
#STREAM_SERVICE_WEB_URL = "localhost:6066"

print(KAFKA_BROKER_URL)
producer = KafkaProducer(bootstrap_servers=KAFKA_BROKER_URL)

###################################
### Auxiliary functions
###################################

def get_qtable(node_id):
    """
    Get the Q-Table dictionary for a given node_id from the Stream Service.
    """
    logger.info("get_qtable()")
    url = f"http://%s/qtable/{node_id}/" % (STREAM_SERVICE_WEB_URL)
    
    logger.info(f"querying the Stream Service for the Q-Table of entry {node_id}")
    #payload = {"node_id" : node_id}
    #r = requests.get(url, params=payload)
    r = requests.get(url)
    
    if r.status_code == 200:
        return json.loads(r.content)
    else:
        raise Exception("ERROR: Stream Service returned %d" %
                        r.status_code)

def get_vehicle(vehicle_id):
    """
    Get the vehicle dictionary for a given vehicle_id from the Stream Service.
    """
    logger.info("get_vehicle()")
    url = f"http://%s/vehicle/{vehicle_id}/" % (STREAM_SERVICE_WEB_URL)
    
    logger.info(f"querying the Stream Service for the vehicle entry {vehicle_id}")
    #payload = {"vehicle_id" : vehicle_id}
    #r = requests.get(url, params=payload)
    r = requests.get(url)
    
    if r.status_code == 200:
        return json.loads(r.content)
    else:
        raise Exception("ERROR: Stream Service returned %d" %
                        r.status_code)


###################################
### Root and status routing functions
###################################

@app.route('/')
def hello_world():
    return 'Hello, this is the Endpoint Server!'

@app.route('/status', methods=['POST']) 
def status():
    logger.info("/status")
    req_data = request.get_json()
    req_data_str = json.dumps(req_data)    
    logger.info(f'sending record to Kafka vehicle-status-topic: {req_data_str}')
    producer.send('vehicle-status-topic', value=req_data_str.encode())
    json_str = json.dumps({"message":"OK"})
    return Response(response=json_str, status=200)

###################################
### Q-Table routing functions
###################################

@app.route('/qtable', methods=['POST']) 
def qtable():
    logger.info("/qtable")
    node_id = request.get_json()["node_id"]

    # get the Q-Table entry
    qtable = get_qtable(node_id)
        
    # return it to the client
    json_string = json.dumps(json.dumps(qtable))
    return Response(response=json_string, status=200)

@app.route('/qtableinit', methods=['GET']) 
def qtable_initialize():    
    logger.info("/qtableinit")
    logger.info("sending records to initialize all Q-Table entries")

    road_net = sumolib.net.readNet(SUMO_ROADNET_PATH)
    
    # for each node_id in the road_net:
    #   issue a record to the qtable-entry-init-topic to initialize node_id in the Q-Table
    for node in road_net.getNodes():         
        node_id = node.getID()        
        req_data = {"node_id" : node_id}
        req_data_str = json.dumps(req_data)
        logger.info(f'sending record to Kafka qtable-entry-init-topic: {req_data_str}')
        producer.send('qtable-entry-init-topic', value=req_data_str.encode())
    
    json_str = json.dumps({"message":"OK"})
    return Response(response=json_str, status=200)

@app.route('/isqtableinitialized', methods=['GET']) 
def is_qtable_initialized():
    logger.info("/isqtableinitialized")
    
    road_net = sumolib.net.readNet(SUMO_ROADNET_PATH)
    
    qtable_initialized = True
    for node in road_net.getNodes(): # for each node in road_net
        node_id = node.getID()
        # query the Stream Service to see if node_id is initialized
        logger.info(f"querying Q-Table for {node_id}")
        qtable = get_qtable(node_id)             
        logger.info(f"obtained: {qtable}")
        if len(qtable[node_id].keys()) == 0:
            logger.info(f"Q-Table entry {node_id} NOT initialized!")
            qtable_initialized = False 
            break            
             
    logger.info(f"is the Q-Table initialized?: {qtable_initialized}")
    json_str = json.dumps({"initialized" : qtable_initialized})
    return Response(response=json_str, status=200)   

###################################
### Vehicle routing functions
###################################

@app.route('/vehicle', methods=['POST']) 
def vehicle():
    logger.info("/vehicle")
    vehicle_id = request.get_json()["vehicle_id"]

    # get the vehicle table entry
    vehicle_table_entry = get_vehicle(vehicle_id)
        
    # return it to the client
    json_string = json.dumps(json.dumps(vehicle_table_entry))
    return Response(response=json_string, status=200)

@app.route('/vehiclesinit', methods=['POST']) 
def vehicles_initialization():    
    """
    Request the initialization of one or more just departed (new) vehicles.
    """
    logger.info("/vehiclesinit")
    logger.info("sending records to initialize vehicles")

    vehicle_ids = request.get_json()["vehicle_ids"]
    
    for vehicle_id in vehicle_ids:                 
        req_data = {"vehicle_id" : vehicle_id}
        req_data_str = json.dumps(req_data)
        logger.info(f'sending record to Kafka vehicle-entry-init-topic: {req_data_str}')
        producer.send('vehicle-entry-init-topic', value=req_data_str.encode())
    
    json_str = json.dumps({"message":"OK"})
    return Response(response=json_str, status=200)

@app.route('/arevehiclesinitialized', methods=['POST']) 
def are_vehicles_initialized():
    logger.info("/arevehiclesinitialized")
    
    vehicle_ids = request.get_json()["vehicle_ids"]
    
    initialized = True
    for vehicle_id in vehicle_ids:   
        logger.info(f"querying vehicle table for {vehicle_id}")
        vehicle_table_entry = get_vehicle(vehicle_id)
        logger.info(f"obtained: {vehicle_table_entry}")
        if len(vehicle_table_entry[vehicle_id].keys()) == 0:
            logger.info(f"Vehicle table entry {vehicle_id} NOT initialized!")
            initialized = False 
            break            
       
    logger.info(f"are vehicles initialized?: {initialized}")
    json_str = json.dumps({"initialized" : initialized})
    return Response(response=json_str, status=200)

@app.route('/havearrived', methods=['POST']) 
def have_vehicles_arrived():
    logger.info("/havearrived")
    
    vehicle_ids = request.get_json()["vehicle_ids"]
    not_arrived = []
    
    arrived = True
    for vehicle_id in vehicle_ids:   
        logger.info(f"querying vehicle table for {vehicle_id}")
        vehicle_table_entry = get_vehicle(vehicle_id)
        logger.info(f"obtained: {vehicle_table_entry}")
        if vehicle_table_entry[vehicle_id]["has_arrived"] != True:
            logger.info(f"Vehicle {vehicle_id} has not arrived!")
            not_arrived.append(vehicle_id)
            arrived = False 
            
    logger.info(f"have all arrived?: {arrived}")
    json_str = json.dumps({"arrived" : arrived , "not_arrived": not_arrived})
    return Response(response=json_str, status=200)

@app.route('/arrival', methods=['POST']) 
def send_vehicles_arrival_notifications():    
    logger.info("/arrival")
    logger.info("sending notification of vehicles arrival")
    
    vehicle_ids = request.get_json()["vehicle_ids"]   
    for vehicle_id in vehicle_ids:         
        logger.info(f"sending arrival notification for {vehicle_id}")
        json_str = json.dumps({"vehicle_id" : vehicle_id})
        producer.send('vehicle-arrival-topic', value=json_str.encode())
         
    json_str = json.dumps({"message":"OK"})
    return Response(response=json_str, status=200)

###################################
### Route routing functions
###################################

@app.route('/route', methods=['POST']) 
def get_route():
    logger.info("/route")
    req_data = request.get_json()
    source_edge_id = req_data["source_edge_id"]
    dest_edge_id = req_data["dest_edge_id"]
    
    # calculate source_node_id and dest_node_id
    
    road_net = sumolib.net.readNet(SUMO_ROADNET_PATH)
    
    # below we take as start node the "toNode" of the source_edge_id 
    # since the vehicle is already traversing source_edge_id
    # (source_node) -> [source_edge] -> (start_node) -> .... -> (dest_node)

    start_node_id = road_net.getEdge(source_edge_id).getToNode().getID() 
    dest_node_id = road_net.getEdge(dest_edge_id).getToNode().getID()
     
    logger.info(f"start node = {start_node_id} dest node = {dest_node_id}")

    route_nodes = []
    route_nodes.append(start_node_id)

    next_node_id = start_node_id
    prev_node_id = None
    
    # the preset route is made of only one edge, so there is nothing to do,
    # return an empty path
    if next_node_id == dest_node_id:
        res = {"error" : 0, "route" : []}
        res_json = json.dumps(res)
        return Response(response=res_json, status=200) 
        
    loop_detected = False
    while next_node_id != dest_node_id:
        next_node_qtable = get_qtable(next_node_id)
        #logger.info(pprint.pprint(next_node_qtable))        
        
        nei_node_ids = list(next_node_qtable[next_node_id][dest_node_id].keys())

        # NOTE: heuristic to not to create loops, but there is no guarantee
        if prev_node_id in nei_node_ids:
            nei_node_ids.remove(prev_node_id) # don't go back
                
        min_node_id = None
        min_dist = float('inf')
        for nei_node_id in nei_node_ids:       
            logger.info(f"next_node_id = {next_node_id} - dest_node_id {dest_node_id} - nei_node_id = {nei_node_id}")
            if next_node_qtable[next_node_id][dest_node_id][nei_node_id] < min_dist:
                min_dist = next_node_qtable[next_node_id][dest_node_id][nei_node_id]
                min_node_id = nei_node_id
        assert min_node_id != None
        prev_node_id = next_node_id
        next_node_id = min_node_id

        if next_node_id in route_nodes:
            logger.warning(f"loop detected! aborting and notifying the client")
            loop_detected = True
            break
        
        logger.info(f"next node is {next_node_id}")        
        route_nodes.append(next_node_id)
        logger.info(f"node route so far: {route_nodes}")

    if loop_detected:
        res = {"error" : 1, "route" : []}
        res_json = json.dumps(res)
        return Response(response=res_json, status=200)


    # convert the node route to edge route
    route_edges = []
    for i in range(len(route_nodes) - 1):
        u_id = route_nodes[i]
        v_id = route_nodes[i+1]
        u = road_net.getNode(u_id)
        # search for edge u->v 
        found = False
        for out_edge in u.getOutgoing():
            if out_edge.getToNode().getID() == v_id:
                route_edges.append(out_edge.getID())
                found = True
                break
        assert found # edge not found??

    res = {"error" : 0, "route" : route_edges}
    res_json = json.dumps(res)
    return Response(response=res_json, status=200)

if __name__ == '__main__':
    logger.info(f"starting EndPoint Server ...")
    app.run(host=ENDPOINT_SERVER_HOST, port=int(ENDPOINT_SERVER_PORT))