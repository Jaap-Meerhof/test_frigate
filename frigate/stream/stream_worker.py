# ... --> (x_node_id) --[prev_edge_id]--> (y_node_id) --[current_edge_id]--> (z_node_id) --> ... --> (dest_node_id)
# y_node_id is the (id of the) node that has been crossed when a vehicle changes its edge
# the qtable entry for x_node_id is the one that has to be updated when a vehicle changes its edge


import faust
import logging
import os
import sys
import numpy as np  # to generate really small random numbers
import sumo_dijkstra
from faust.sensors.statsd import StatsdMonitor
from configuration import KAFKA_BROKER_URL_2, ETA, SUMO_TOOLS_HOME, SUMO_ROADNET_PATH, TOPIC_PARTITIONS, FRIGATE_SERVER_NAME
import statsd

#from faust.web.apps.stats import blueprint

sys.path.append(SUMO_TOOLS_HOME)
import sumolib

logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s - %(levelname)s - %(name)s - %(message)s'
                    )
logger = logging.getLogger(__name__)

# statsd
GRAPHITE_HOST = "frigate-graphite"
STATSD_PORT = 8125
statsd_mon = StatsdMonitor(host=GRAPHITE_HOST, port=STATSD_PORT, prefix='frigate-stream-faust') 
#statsd_mon = None

app = faust.App('frigate-stream-app',
                broker=KAFKA_BROKER_URL_2, topic_partitions=TOPIC_PARTITIONS,
                monitor=statsd_mon,
                broker_request_timeout=180)
                #stream_buffer_maxsize=12288)
road_net = sumolib.net.readNet(SUMO_ROADNET_PATH)

c = statsd.StatsClient(GRAPHITE_HOST, STATSD_PORT, prefix="frigate-stream")

c.gauge(f'.{FRIGATE_SERVER_NAME}.process_qtable_entry_init', 0)
c.gauge(f'.{FRIGATE_SERVER_NAME}.process_vehicle_arrival', 0)
c.gauge(f'.{FRIGATE_SERVER_NAME}.process_vehicle_status', 0)
c.gauge(f'.{FRIGATE_SERVER_NAME}.proccess_min_y_qvalue', 0)
c.gauge(f'.{FRIGATE_SERVER_NAME}.process_qtable_entry_update', 0)
c.gauge(f'.{FRIGATE_SERVER_NAME}.get_qtable_entry', 0)
c.gauge(f'.{FRIGATE_SERVER_NAME}.get_vehicle_entry', 0)

#blueprint.register(app, url_prefix='/stats/')

# TODO: move this conf to another file
#KAFKA_BROKER_URL = 'kafka://localhost'
#ETA = 0.5



#########################################
# models
#########################################

class InitQTableEntryRecord(faust.Record, serializer='json'):
    node_id: str


class InitVehicleEntryRecord(faust.Record, serializer='json'):
    vehicle_id: str


class VehicleStatusRecord(faust.Record, serializer='json'):
    vehicle_id: str
    edge_id: str
    speed: float
    dest_edge_id: str


class VehicleArrivalRecord(faust.Record, serializer='json'):
    vehicle_id: str


class EdgeChangeRecord(faust.Record, serializer='json'):
    vehicle_id: str
    vehicle_time: float
    dest_node_id: str
    x_node_id: str
    y_node_id: str


class QTableEntryUpdateRecord(faust.Record, serializer='json'):
    vehicle_id: str
    x_node_id: str
    y_node_id: str
    dest_node_id: str
    min_y_qvalue: float
    vehicle_time: float

#########################################
# topic schemas
#########################################

qtable_entry_init_schema = faust.Schema(
    key_type=str,
    value_type=InitQTableEntryRecord,
    key_serializer='json',
    value_serializer='json'
)

vehicle_entry_init_schema = faust.Schema(
    key_type=str,
    value_type=InitVehicleEntryRecord,
    key_serializer='json',
    value_serializer='json'
)

vehicle_status_schema = faust.Schema(
    key_type=str,
    value_type=VehicleStatusRecord,
    key_serializer='json',
    value_serializer='json'
)

vehicle_arrival_schema = faust.Schema(
    key_type=str,
    value_type=VehicleArrivalRecord,
    key_serializer='json',
    value_serializer='json'
)

edge_change_schema = faust.Schema(
    key_type=str,
    value_type=EdgeChangeRecord,
    key_serializer='json',
    value_serializer='json'
)

qtable_entry_update_schema = faust.Schema(
    key_type=str,
    value_type=QTableEntryUpdateRecord,
    key_serializer='json',
    value_serializer='json'
)

#########################################
# table schemas
#########################################

qtable_schema = faust.Schema(
    key_type=str,
    key_serializer='json',
    value_serializer='json'
)

vehicle_table_schema = faust.Schema(
    key_type=str,
    key_serializer='json',
    value_serializer='json'
)

#########################################
# topics
#########################################


qtable_entry_init_topic = app.topic(
    'qtable-entry-init-topic', schema=qtable_entry_init_schema, partitions=TOPIC_PARTITIONS)

vehicle_entry_init_topic = app.topic('vehicle-entry-init-topic',
                                     schema=vehicle_entry_init_schema, partitions=TOPIC_PARTITIONS)

vehicle_status_topic = app.topic(
    'vehicle-status-topic', value_type=VehicleStatusRecord,
    schema=vehicle_status_schema,
    partitions=TOPIC_PARTITIONS)

vehicle_arrival_topic = app.topic('vehicle-arrival-topic', value_type=VehicleArrivalRecord, schema=vehicle_arrival_schema,
                                 partitions=TOPIC_PARTITIONS)

edge_change_topic = app.topic('edge-change-topic', value_type=EdgeChangeRecord,
                              schema=edge_change_schema,
                              partitions=TOPIC_PARTITIONS)

qtable_entry_update_topic = app.topic('qtable-entry-update-topic',
                                      schema=qtable_entry_update_schema,
                                      value_type=QTableEntryUpdateRecord, partitions=TOPIC_PARTITIONS)

#########################################
# tables
#########################################

vehicle_table = app.Table('vehicle-table', default=dict,
                          help='Table to store data about vehicles (edge, num. of records, speed sum, travel time, has arrived)', partitions=TOPIC_PARTITIONS, schema=vehicle_table_schema)

qtable = app.Table('qtable',
                   default=dict,
                   help='Q-Routing Q-Table.',
                   partitions=TOPIC_PARTITIONS, schema=qtable_schema)

#########################################
# agents
#########################################

# this one does not use dijkstra
@app.agent(qtable_entry_init_topic)
async def process_qtable_entry_init(qtable_entry_init_stream):
    """
    Initializes a single entry 'node_id' of the Q-table.
    The structure of the Q-table is as follows:
    q_table <- { node_id -> { dest_node_id -> { nei_node_id -> float } } }
    """
    async for qtable_entry_init_rec in qtable_entry_init_stream.group_by(InitQTableEntryRecord.node_id):
        logger.info(
            f'[process_qtable_entry_init]')

        c.incr(f'.{FRIGATE_SERVER_NAME}.process_qtable_entry_init')
        c.gauge(f'.{FRIGATE_SERVER_NAME}.process_qtable_entry_init', 1, delta=True)

        # node_id <- Q-Table entry id
        node_id = qtable_entry_init_rec.node_id

        logger.info(
            f'[process_qtable_entry_init] initializing entry {node_id} ...')

        # get the neighbors of 'node_id'
        #road_net = sumolib.net.readNet(SUMO_ROADNET_PATH)
        node_outgoing_edges = road_net.getNode(node_id).getOutgoing()

        # for each possible destination 'dest_node_id' in the road network:
        #   for each node_id's outgoing neighbor 'nei_node_id':
        #       initialize qtable[node_id][dest_node_id][nei_node_id] with a small random number (according to the Q-routing paper)
        logger.info(
            f'[process_qtable_entry_init] initializing Q-Table entry ...')

        qtable[node_id] = {}

        for dest_node in road_net.getNodes():
            dest_node_id = dest_node.getID()
            qtable[node_id][dest_node_id] = {}

            # initialize each outgoing neighbor
            for outgoing_edge in node_outgoing_edges:
                nei_node_id = outgoing_edge.getToNode().getID()

                # destination is not node_id itself?
                if dest_node_id != node_id:
                    qtable[node_id][dest_node_id][nei_node_id] = np.random.uniform(
                        10**(-20), 10**(-16))
                else:
                    qtable[node_id][dest_node_id][nei_node_id] = float("inf")

        logger.info(
            f'[process_qtable_entry_init] entry {node_id} initialized.')


# this one uses dijkstra
# @app.agent(qtable_entry_init_topic)
#async def process_qtable_entry_init2(qtable_entry_init_stream):
#    """
#    Initializes a single entry 'node_id' of the Q-table.
#    The structure of the Q-table is as follows:
#    q_table <- { node_id -> { dest_node_id -> { nei_node_id -> float } } }
#    """
#    async for qtable_entry_init_rec in qtable_entry_init_stream:
#        logger.info(
#            f'[process_qtable_entry_init]')
#
#        # node_id <- Q-Table entry id
#        node_id = qtable_entry_init_rec.node_id
#
#        logger.info(
#            f'[process_qtable_entry_init] initializing entry {node_id} ...')
#
#        # get the neighbors of 'node_id'
#        road_net = sumolib.net.readNet(SUMO_ROADNET_PATH)
#        node_outgoing_edges = road_net.getNode(node_id).getOutgoing()
#
#        # calculate shortest paths between node_id and all other nodes
#        logger.info(
#            f'[process_qtable_entry_init] computing shortest paths ...')
#        shortest_paths = sumo_dijkstra.get_single_source_all_dest_paths(
#            road_net, node_id)
#
#        logger.info(
#            f'[process_qtable_entry_init] {shortest_paths}')
#
#        # for each possible destination 'dest_node_id' in the road network:
#        #   for each node_id's outgoing neighbor 'nei_node_id':
#        #       initialize qtable[node_id][dest_node_id][nei_node_id] with a small random number (according to the Q-routing paper)
#        logger.info(
#            f'[process_qtable_entry_init] initializing Q-Table entry ...')
#        qtable[node_id] = {}
#        for dest_node in road_net.getNodes():
#            dest_node_id = dest_node.getID()
#            qtable[node_id][dest_node_id] = {}
#
#            # get best neighbor from shortest path:
#            best_nei_id = -1
#            if node_id != dest_node_id:
#                best_nei_id = shortest_paths[dest_node_id][1]
#
#            # initialize each outgoing neighbor
#            for outgoing_edge in node_outgoing_edges:
#                nei_node_id = outgoing_edge.getToNode().getID()
#
#                # destination is not node_id itself?
#                if dest_node_id != node_id:
#                    # is this the best (shortest path) neighbor?
#                    if nei_node_id == best_nei_id:  # initialize it with lower value
#                        qtable[node_id][dest_node_id][nei_node_id] = np.random.uniform(
#                            10**(-20), 10**(-16))
#                    else:
#                        qtable[node_id][dest_node_id][nei_node_id] = np.random.uniform(
#                            10**(-14), 10**(-10))
#                else:
#                    qtable[node_id][dest_node_id][nei_node_id] = float("inf")
#
#        logger.info(
#            f'[process_qtable_entry_init] entry {node_id} initialized.')


#@app.agent(vehicle_entry_init_topic)
#async def process_vehicle_entry_init(vehicle_entry_init_stream):
#    """
#    Initializes the entry 'vehicle_id' in the Vehicle Table.    
#    """
#    async for vehicle_entry_init_rec in vehicle_entry_init_stream.group_by(InitVehicleEntryRecord.vehicle_id):
#        logger.info(
#            f'[process_vehicle_entry_init]')
#
#        vehicle_id = vehicle_entry_init_rec.vehicle_id
#
#        logger.info(
#            f'[process_vehicle_entry_init] initializing entry {vehicle_id} ...')
#
#        vehicle_table[vehicle_id] = {
#            "edge_id": "",
#            "edge_speed_sum": 0.0,
#            "edge_num_records": 0,
#            "total_travel_time": 0.0,
#            "traversed_edges": [],
#            "touched_nodes": [],
#            "has_arrived": False
#        }
#
#        logger.info(
#            f'[process_vehicle_entry_init] entry {vehicle_id} initialized.')

# TODO: FIX FOR TELEPORTED VEHICLES
# TODO: WILL THIS WORK IF THE DESTINATION EDGE IS THE SOURCE EDGE?
@app.agent(vehicle_arrival_topic)
async def process_vehicle_arrival(vehicle_arrival_stream):
    async for vehicle_arrival_rec in vehicle_arrival_stream.group_by(VehicleArrivalRecord.vehicle_id):
        logger.info(
            f'[process_vehicle_arrival]')
        """
        Process vehicle arrival (to destination) records.
        Pre-conditions: it is assumed that the vehicle entry in the Vehicle Table has been previously initialized.
        """

        c.incr(f'.{FRIGATE_SERVER_NAME}.process_vehicle_arrival')
        c.gauge(f'.{FRIGATE_SERVER_NAME}.process_vehicle_arrival', 1, delta=True)

        vehicle_id = vehicle_arrival_rec.vehicle_id
        current_edge_id = vehicle_table[vehicle_id]["edge_id"]
        prev_edge_id = current_edge_id

        assert not "n" in current_edge_id, "the destination (arrival) edge is a junction???"
        assert vehicle_table[vehicle_id] != {}, f"Vehicle {vehicle_id} has not been previosly initialized?"

        if vehicle_table[vehicle_id]["edge_num_records"] > 0:

            # new edge traversal detected
            vehicle_table[vehicle_id]["traversed_edges"].append(prev_edge_id)

            # calculate the average speed of the vehicle on the previous (traversed) edge
            vehicle_avg_speed = vehicle_table[vehicle_id]["edge_speed_sum"] / float(
                vehicle_table[vehicle_id]["edge_num_records"])

            # calculate the time taken by the vehicle to traverse the previous edge
            #road_net = sumolib.net.readNet(SUMO_ROADNET_PATH)
            prev_edge_length = road_net.getEdge(prev_edge_id).getLength()
            vehicle_time = prev_edge_length / float(vehicle_avg_speed)
            vehicle_table[vehicle_id]["total_travel_time"] += vehicle_time

            # register that the vehicle has arrived
            vehicle_table[vehicle_id]["has_arrived"] = True

            # calculate dest_node_id, x_node_id and y_node_id
            # by using only the prev_edge_id
            dest_node_id = road_net.getEdge(prev_edge_id).getToNode().getID()
            x_node_id = road_net.getEdge(prev_edge_id).getFromNode().getID()
            y_node_id = dest_node_id

            # register we touched the target node
            vehicle_table[vehicle_id]["touched_nodes"].append(y_node_id)

            # issue an edge change record
            logger.info(
                f'[process_vehicle_arrival] issuing edge_change event')
            edge_change_rec = EdgeChangeRecord(
                vehicle_id=vehicle_id,
                vehicle_time=vehicle_time,
                dest_node_id=dest_node_id,
                x_node_id=x_node_id,
                y_node_id=y_node_id)
            await edge_change_topic.send(value=edge_change_rec)

        else:  # this happens sometimes, due to teleporting? TODO: check

            logger.warning(
                f'[process_vehicle_arrival] number of records for the previous edge is 0!')

            # register that the vehicle has arrived
            vehicle_table[vehicle_id]["has_arrived"] = True

            # register we touched the target node
            vehicle_table[vehicle_id]["touched_nodes"].append(y_node_id)


@app.agent(vehicle_status_topic)
async def process_vehicle_status(vehicle_status_stream):
    async for vehicle_status_rec in vehicle_status_stream.group_by(VehicleStatusRecord.vehicle_id):
        """
        Process vehicle status records.
        Pre-conditions: it is assumed that the vehicle entry in the Vehicle Table has been previously initialized.
        """
        logger.info(
            f'[process_vehicle_status] vehicle_id = {vehicle_status_rec.vehicle_id}')
        
        c.incr(f'.{FRIGATE_SERVER_NAME}.process_vehicle_status')
        c.gauge(f'.{FRIGATE_SERVER_NAME}.process_vehicle_status', 1, delta=True)

        vehicle_id = vehicle_status_rec.vehicle_id

        ##
        # if vehicle is new, initialize it
        if vehicle_table[vehicle_id] == {}:
            logger.info(
            f'[process_vehicle_status] initializing entry {vehicle_id} ...')
            vehicle_table[vehicle_id] = {
                "edge_id": "",
                "edge_speed_sum": 0.0,
                "edge_num_records": 0,
                "total_travel_time": 0.0,
                "traversed_edges": [],
                "touched_nodes": [],
                "has_arrived": False
            }
        ##    
        
        prev_edge_id = vehicle_table[vehicle_id]["edge_id"]
        current_edge_id = vehicle_status_rec.edge_id

        # do nothing for the current record if the current edge is a junction
        if "n" in current_edge_id:
            continue

        #road_net = sumolib.net.readNet(SUMO_ROADNET_PATH)

        # started to traverse the first edge (i.e. it is the very first event for this vehicle)?
        if prev_edge_id == "" and vehicle_table[vehicle_id]["edge_num_records"] == 0:
            # register we touched the source node
            source_node_id = road_net.getEdge(
                current_edge_id).getFromNode().getID()
            vehicle_table[vehicle_id]["touched_nodes"].append(source_node_id)

        # vehicle changed edge?
        if prev_edge_id != current_edge_id and prev_edge_id != "":

            # new edge traversal detected
            vehicle_table[vehicle_id]["traversed_edges"].append(prev_edge_id)

            # x_node_id <- get the id of the 'from' node of the previous edge
            x_node_id = road_net.getEdge(prev_edge_id).getFromNode().getID()
            # y_node_id <- get the id of the 'from' node of the current (new) edge
            y_node_id = road_net.getEdge(current_edge_id).getFromNode().getID()

            # check that x and y are connected,
            # if not the probably vehicle spawned away
            # (b.c. lost messages? SUMO vehicle teleporting?)
            xy_connected = sumo_dijkstra.are_nodes_connected(
                road_net, x_node_id, y_node_id)
            if not xy_connected:

                logger.warning(
                    f"nodes x = {x_node_id} and y = {y_node_id} are not connected! lost messages?")
                pass  # nothing else to do

            else:  # x and y are connected

                # calculate the average speed of the vehicle on the previous (traversed) edge

                if vehicle_table[vehicle_id]["edge_num_records"] > 0:
                    vehicle_avg_speed = vehicle_table[vehicle_id]["edge_speed_sum"] / float(
                        vehicle_table[vehicle_id]["edge_num_records"])
                else: #TODO: check why this condition happens from then to then
                    vehicle_avg_speed = 0
                    logger.warning(
                    f"edge_num_records = 0. Why?")

                vehicle_table[vehicle_id]["edge_speed_sum"] = 0.0
                vehicle_table[vehicle_id]["edge_num_records"] = 0

                # calculate the time taken by the vehicle to traverse the previous edge
                prev_edge_length = road_net.getEdge(prev_edge_id).getLength()
                
                if vehicle_avg_speed > 0: #TODO: this happens if the condition above (edge_num_records = 0) happens.
                    vehicle_time = prev_edge_length / float(vehicle_avg_speed)
                else:
                    vehicle_time = 0

                vehicle_table[vehicle_id]["total_travel_time"] += vehicle_time

                # dest_node_id <- obtain the toNodeId of the dest_edge_id (sumolib.net)
                dest_node_id = road_net.getEdge(
                    vehicle_status_rec.dest_edge_id).getToNode().getID()

                # register we touched the crossed node
                vehicle_table[vehicle_id]["touched_nodes"].append(y_node_id)

                # issue an edge change record
                logger.info(
                    f'[process_vehicle_status] issuing edge_change event')
                edge_change_rec = EdgeChangeRecord(
                    vehicle_id=vehicle_id,
                    vehicle_time=vehicle_time,
                    dest_node_id=dest_node_id,
                    x_node_id=x_node_id,
                    y_node_id=y_node_id)
                await edge_change_topic.send(value=edge_change_rec)
        else:
            # acumulate the speed and number of events of the vehicle for the current edge
            vehicle_table[vehicle_id]["edge_speed_sum"] += vehicle_status_rec.speed
            vehicle_table[vehicle_id]["edge_num_records"] += 1

        # update vehicle current edge
        vehicle_table[vehicle_id]["edge_id"] = current_edge_id


@app.agent(edge_change_topic)
async def proccess_min_y_qvalue(edge_change_stream):
    """
    Get min{Q[y][d]}, according to the Q-routing algorithm.
    """
    async for edge_change_rec in edge_change_stream.group_by(EdgeChangeRecord.y_node_id):
        logger.info(
            f'[proccess_min_y_qvalue]')

        c.incr(f'.{FRIGATE_SERVER_NAME}.proccess_min_y_qvalue')
        c.gauge(f'.{FRIGATE_SERVER_NAME}.proccess_min_y_qvalue', 1, delta=True)
 
        y_node_id = edge_change_rec.y_node_id
        dest_node_id = edge_change_rec.dest_node_id

        min_y_qvalue = 1e10
        for z_node_id in qtable[y_node_id][dest_node_id]:
            if qtable[y_node_id][dest_node_id][z_node_id] < min_y_qvalue:
                min_y_qvalue = qtable[y_node_id][dest_node_id][z_node_id]

        # issue a new Q-Table update record with all the data needed to do so
        q_table_update_rec = QTableEntryUpdateRecord(
            vehicle_id=edge_change_rec.vehicle_id,
            x_node_id=edge_change_rec.x_node_id,
            y_node_id=y_node_id,
            dest_node_id=dest_node_id,
            min_y_qvalue=min_y_qvalue,
            vehicle_time=edge_change_rec.vehicle_time
        )
        await qtable_entry_update_topic.send(value=q_table_update_rec)

# q-routing
@app.agent(qtable_entry_update_topic)
async def process_qtable_entry_update(qtable_entry_update_stream):
    async for qtable_entry_update_rec in qtable_entry_update_stream.group_by(QTableEntryUpdateRecord.x_node_id):
        logger.info(
            f'[process_qtable_entry_update]')
        
        c.incr(f'.{FRIGATE_SERVER_NAME}.process_qtable_entry_update')
        c.gauge(f'.{FRIGATE_SERVER_NAME}.process_qtable_entry_update', 1, delta=True)

        x_node_id = qtable_entry_update_rec.x_node_id
        y_node_id = qtable_entry_update_rec.y_node_id
        dest_node_id = qtable_entry_update_rec.dest_node_id
        min_y_qvalue = qtable_entry_update_rec.min_y_qvalue
        vehicle_time = qtable_entry_update_rec.vehicle_time

        # apply Boyan's Q-Routing value iteration formula to update the x_node_id entry of the Q-Table
        logger.info(
            f'[process_qtable_entry_update] updating Q-Table entry')
        logger.info(
            f'[process_qtable_entry_update] x_node_id = {x_node_id} y_node_id = {y_node_id} dest_node_id = {dest_node_id}')
        old_estimate = qtable[x_node_id][dest_node_id][y_node_id]
        logger.info(f'old_estimate={old_estimate}')
        new_estimate = min_y_qvalue + vehicle_time
        logger.info(f'new_estimate={new_estimate}')
        qtable[x_node_id][dest_node_id][y_node_id] += ETA * \
            (new_estimate - old_estimate)
        logger.info(f'updated q-table entry={qtable[x_node_id][dest_node_id][y_node_id]}')

#########################################
# Web views
#########################################


@app.page('/qtable/{node_id}/')
@app.table_route(table=qtable, match_info='node_id')
async def get_qtable_entry(web, request, node_id):

    logger.info(
            f'[get_qtable_entry] node_id = {node_id}')
    
    c.incr(f'.{FRIGATE_SERVER_NAME}.get_qtable_entry')
    c.gauge(f'.{FRIGATE_SERVER_NAME}.get_qtable_entry', 1, delta=True)

    #node_id = request.query['node_id']
    
    #logger.info(
    #    f'[get_qtable_entry] returning entry for node_id {node_id}')
    return web.json({
        node_id: qtable[node_id],  # this will deliver a dictionary
    })


@app.page('/vehicle/{vehicle_id}/')
@app.table_route(table=vehicle_table, match_info='vehicle_id')
async def get_vehicle_entry(web, request, vehicle_id):
    logger.info(
            f'[get_vehicle_entry] vehicle_id = {vehicle_id}')

    c.incr(f'.{FRIGATE_SERVER_NAME}.get_vehicle_entry')
    c.gauge(f'.{FRIGATE_SERVER_NAME}.get_vehicle_entry', 1, delta=True)

    #vehicle_id = request.query['vehicle_id']
    
    #logger.info(
    #    f'[get_vehicle_entry] returning entry for vehicle_id = {vehicle_id}')
    return web.json({
        # this will deliver a dictionary
        vehicle_id: vehicle_table[vehicle_id],
    })


#@app.page('/debug/')
#async def debug_page(web, request):
#    logger.info(
#        f'[debug_page] app.router.table_metadata(qtable) = {app.router.table_metadata(table_name="qtable")}')
#
#    for i in range(1, 10+1):
#        logger.info(
#            f'[debug_page] app.router.key_store(qtable, n{i}) = {app.router.key_store("qtable", f"n{i}")}')
#
#    return web.json({
#        "message": "ok"
#    })

#########################################
# Main
#########################################

if __name__ == '__main__':
    logger.info("stream service starts")
    app.main()
