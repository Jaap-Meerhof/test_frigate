import os, sys
import pprint
import logging
import time
import copy
import statsd
from configuration import SUMO_TOOLS_HOME, SUMO_STEPS, SUMO_BINARY, SUMO_SIM_FILE, SUMO_CMD, VEHICLES_TO_ROUTE, ROUTING_STEP_PERIOD
from endpoint_client import EndPointClient


sys.path.append(SUMO_TOOLS_HOME)
import traci

logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s - %(levelname)s - %(name)s - %(message)s'
                    )
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
endpoint = EndPointClient()


# move this conf
DOCKER_HOST_IP = "192.168.8.4"
STATSD_PORT = 8125
c = statsd.StatsClient(DOCKER_HOST_IP, STATSD_PORT, prefix="frigate-simulator")
#c.gauge('are-vehicle-init-errors-gauge', 0)
#c.gauge('reroute-errors-gauge', 0)
#c.gauge('are-vehicles-init-retrials', 0)

MAX_VEHICLE_INIT_TRIALS = 10

def getVehicleData(running_vehicle_ids):
    """
    Get the speed and the Edge ID of each vehicle active in the current simulation step.
    """
    data = {}
    
    for vehicle_id in running_vehicle_ids:      
        
        # get the destination edge from the vehicle's preset route        
        route_id = traci.vehicle.getRouteID(vehicle_id)
        route = traci.route.getEdges(route_id)
        source_edge_id = route[0]
        dest_edge_id = route[-1]

        status = {"edge_id": traci.vehicle.getRoadID(vehicle_id),
                  "speed": traci.vehicle.getSpeed(vehicle_id),
                  "source_edge_id" : source_edge_id,
                  "dest_edge_id": dest_edge_id,
                  "preset_route" : route}
        
        data[vehicle_id] = status
    return data

def initialize_qtable():
    # initialize all Q-table entries in the Stream Service
    # and wait until all the new Q-Table entries are initialized
    logger.info("requesting initialization of the Q-Table ...")    
    endpoint.send_qtable_init_request()    
    logger.info("waiting for the initialization of the Q-Table ...")    
    while not endpoint.is_qtable_initialized():
        #logger.info("sleeping ...")
        time.sleep(0.5)
        pass    
    logger.info("Q-Table entries initialized!")
    return


def run_simulation(step_by_step=False):
    
    arrived_count = 0
    
    # simulation start
    logger.info("starting SUMO ...")
    print("starting SUMO ...")
    traci.start(SUMO_CMD)   
    
    logger.info("starting simulation ...")
    
    # start simulation
    step = 1
    loops = 0
    sim_vehicle_data = {}
    while step < SUMO_STEPS:
        if step_by_step:
            progress_perc = int( step*100 / float(SUMO_STEPS) )
            logger.info(f"Running step {step}/{SUMO_STEPS} ({progress_perc}%")
            yield {"status": "RUNNING_SIMULATION_STEP", "data":{"step":step, "steps":SUMO_STEPS, "simulation_time":traci.simulation.getTime(), "progress_perc":progress_perc}, "message": f"Running step {step}/{SUMO_STEPS} ({progress_perc}%)"}

        logger.info("Simulation Step: %s" %step)
        traci.simulationStep()
        logger.info("Simulation Time: %s" %str(traci.simulation.getTime()))
        
        running_vehicle_ids = traci.vehicle.getIDList()            
        departed_vehicle_ids = traci.simulation.getDepartedIDList()
        arrived_vehicle_ids = traci.simulation.getArrivedIDList()
        data = getVehicleData(running_vehicle_ids) # get the data for all running vehicles

        # initialize all the newly DEPARTED vehicles in the Stream Service
        #if len(departed_vehicle_ids) > 0:           
        #    logger.info(f"initializing newly departed vehicles: {departed_vehicle_ids} ...")        
        #    endpoint.send_vehicles_initialization(departed_vehicle_ids)
        #    
        #    #TODO: IMPORTANT: find the problem that causes this with many stream servers. This is just a temporary hack to measure performance.                
        #    #UPDATE: problem found, patched applied to Faust.
        #    vehicle_init_trials = 0
        #   while True:        
        #       
        #        # this is to address the problem which arises when many stream workers servers
        #        # are running and not all vehicles get initialized, preventing 
        #        # the simulation to continue.
        #        if vehicle_init_trials == MAX_VEHICLE_INIT_TRIALS:
        #            logger.info(f"initializing newly departed vehicles (again): {departed_vehicle_ids} ...")        
        #            endpoint.send_vehicles_initialization(departed_vehicle_ids)
        #            c.gauge('are-vehicles-init-retrials', 1, delta=True)
        #            vehicle_init_trials = 0                    
        #            time.sleep(0.5)                    
        #        try:
        #            res = endpoint.are_vehicles_initialized(departed_vehicle_ids)
        #            if res:
        #                break
        #            #logger.info("sleeping ...")
        #            time.sleep(0.5)                    
        #            vehicle_init_trials += 1
        #            continue
        #        except Exception as e:
        #            logger.warning(f"Error while checking if all vehicles are initialized. IGNORING and TRYING AGAIN.")
        #            c.incr('are-vehicle-init-errors')
        #            c.gauge('are-vehicle-init-errors-gauge', 1, delta=True)                    
        #            vehicle_init_trials += 1
        #            continue
        #        
        #    c.incr('init-vehicle-stages-done')
        
        # add new vehicles to the vehicle simulation data dictionary
        for vehicle_id in departed_vehicle_ids:
            sim_vehicle_data[vehicle_id] = {"edge_id" : data[vehicle_id]["edge_id"]}
        # get IDs of vehicles that changed edge
        vehicles_changed_edge = []
        for vehicle_id in data:
            if data[vehicle_id]["edge_id"] != sim_vehicle_data[vehicle_id]["edge_id"] and not "n" in data[vehicle_id]["edge_id"]:
                logger.info(f"vehicle {vehicle_id} bounded to {data[vehicle_id]['dest_edge_id']} changed edge from {sim_vehicle_data[vehicle_id]['edge_id']} to {data[vehicle_id]['edge_id']}")
                vehicles_changed_edge.append(vehicle_id)
                sim_vehicle_data[vehicle_id]["edge_id"] = data[vehicle_id]["edge_id"]
            
        # determine vehicles that are going to be routed in this step
        vehicles_to_route = None
        if VEHICLES_TO_ROUTE == "CHANGED_EDGE":
            vehicles_to_route = vehicles_changed_edge
        elif VEHICLES_TO_ROUTE == "ONLY_DEPARTED":
            vehicles_to_route = departed_vehicle_ids
        elif VEHICLES_TO_ROUTE == "PERIODICAL_STEP":
            if step % ROUTING_STEP_PERIOD == 0: # this will trigger when step = 0 as well
                vehicles_to_route = []
                for vehicle_id in data:
                    if not "n" in data[vehicle_id]["edge_id"]:
                        vehicles_to_route.append(vehicle_id)
            else:
                vehicles_to_route = []    
        else:
            assert False, "wrong ROUTE_VEHICLE value"

        # override the preset route of all just departed vehicles with q-routing routes
        if len(vehicles_to_route) > 0:
            for vehicle_id in vehicles_to_route:
                source_edge_id = data[vehicle_id]["edge_id"]
                dest_edge_id = data[vehicle_id]["dest_edge_id"]
                logger.info(f"requesting route for {vehicle_id} from {source_edge_id} to {dest_edge_id} ...")               

                #TODO: IMPORTANT: find the problem that causes this with many stream servers. This is just a temporary hack to measure performance.                                
                #while True:                
                #    try:
                #        route_req_res = endpoint.get_route(source_edge_id, dest_edge_id)
                #        break
                #    except Exception as e:
                #        logger.warning(f"Error while retrieving route for vehicle {vehicle_id}: {e}. IGNORING and TRYING AGAIN.")
                #        c.incr('reroute-errors')
                #        c.gauge('reroute-errors-gauge', 1, delta=True)
                #        continue
                #
                
                route_req_res = endpoint.get_route(source_edge_id, dest_edge_id)
                
                if route_req_res["error"] == 0:
                    route = route_req_res["route"]
                    route = [source_edge_id] + route
                    logger.info(f"assigning route {route} to vehicle {vehicle_id} ...")
                    traci.vehicle.setRoute(vehicle_id, route)
                    c.incr('re-routings')
                elif route_req_res["error"] == 1:
                    loops += 1
                    logger.warning(f"loop detected! using preset route [count {loops} source_edge {source_edge_id} vehicle {vehicle_id}]")
                    pass
                else:
                    assert False # we shouldn't be here
                    

        # send a status record for every RUNNING vehicle in this time step to the Stream Service        
        logger.info("sending status for running vehicles")        
        for vehicle in data.keys():
            if not "n" in data[vehicle]["edge_id"]: #TODO: this is a hack, since getRoadId() not only returns edge IDs but also node IDs. review.
                endpoint.send_status(vehicle_id=vehicle, edge_id=data[vehicle]["edge_id"], speed=data[vehicle]["speed"], dest_edge_id=data[vehicle]["dest_edge_id"])
                c.incr('sent-vehicle-statuses')
        
        # send notifications for all ARRIVED vehicles to the Stream Service        
        if len(arrived_vehicle_ids) > 0:
            logger.info("sending arrival notifications ...")        
            endpoint.send_arrival_notifications(arrived_vehicle_ids)
            
            #TODO: we are not synchronizing the arrivals anymore

            #logger.info("waiting for the Stream Service to register all arrivals ...")    
            #res_has_arrived_req = endpoint.have_vehicles_arrived(arrived_vehicle_ids)
            
            # wait for arrivals to be registered in the Stream Service
            #while not res_has_arrived_req["arrived"]:
            #    logger.info("sleeping and resending arrival notifications ...")
            #    endpoint.send_arrival_notifications(res_has_arrived_req["not_arrived"])
            #    res_has_arrived_req = endpoint.have_vehicles_arrived(arrived_vehicle_ids)
            #    time.sleep(0.5)
            #    pass
        
        # NOTE: the stats below are valid only if we waited for all arrivals to be registered above
        # calculate stats for this step
        #logger.info("calculating arrived stats ...")    
        #vt_entries = endpoint.get_vehicle_table_entries(arrived_vehicle_ids)
        #arrival_times = []
        #for vt_entry in vt_entries:
        #    arrival_times.append(vt_entry["total_travel_time"])
        
        #avg_total_travel_time = None
        #if len(arrived_vehicle_ids) > 0:
        #    avg_total_travel_time = sum(arrival_times)/float(len(arrival_times))
        
        num_arrivals = len(arrived_vehicle_ids)
        logger.info("="*100)
        logger.info(f"Num. of arrivals in this step = {num_arrivals}")
        #logger.info(f"Avg. total travel time in this step = {avg_total_travel_time}")
        #logger.info("="*100)
            
        step += 1
        c.incr('steps-done')
    
    logger.info("simulation done.")
    traci.close()
    
    yield {"status": "SIMULATION_DONE", "message":"Simulation done."}
       

if __name__ == "__main__":
    run_simulation()