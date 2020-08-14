import os

if 'SUMO_TOOLS_HOME' in os.environ:
    SUMO_TOOLS_HOME = os.environ['SUMO_TOOLS_HOME']    
else:
    raise Exception("please declare environment variable 'SUMO_TOOLS_HOME'")

if 'SUMO_ROADNET_PATH' in os.environ:
    SUMO_ROADNET_PATH = os.environ['SUMO_ROADNET_PATH']    
else:
    raise Exception("please declare environment variable 'SUMO_ROADNET_PATH'")

if 'SUMO_STEPS' in os.environ:
    SUMO_STEPS = int(os.environ['SUMO_STEPS'])
else:
    raise Exception("please declare environment variable 'SUMO_STEPS'")

if 'SUMO_BINARY' in os.environ:
    SUMO_BINARY = os.environ['SUMO_BINARY']    
else:
    raise Exception("please declare environment variable 'SUMO_TOOLS_HOME'")

if 'SUMO_SIM_FILE' in os.environ:
    SUMO_SIM_FILE = os.environ['SUMO_SIM_FILE']    
else:
    raise Exception("please declare environment variable 'SUMO_SIM_FILE'")

# "--summary-output", f"/var/data/output_test/summary.xml"
SUMO_CMD = [SUMO_BINARY, "-c", SUMO_SIM_FILE, "--save-state.period", "10", "--save-state.suffix", ".xml"]

if 'VEHICLES_TO_ROUTE' in os.environ:
    VEHICLES_TO_ROUTE = os.environ['VEHICLES_TO_ROUTE']    
else:
    raise Exception("please declare environment variable 'VEHICLES_TO_ROUTE'")

if 'ROUTING_STEP_PERIOD' in os.environ:
    ROUTING_STEP_PERIOD = int(os.environ['ROUTING_STEP_PERIOD'])
else:
    raise Exception("please declare environment variable 'ROUTING_STEP_PERIOD'")

if 'ENDPOINT_SERVER_HOST' in os.environ:
    ENDPOINT_SERVER_HOST = os.environ['ENDPOINT_SERVER_HOST']    
else:
    raise Exception("please declare environment variable 'ENDPOINT_SERVER_HOST'")

if 'ENDPOINT_SERVER_PORT' in os.environ:
    ENDPOINT_SERVER_PORT = int(os.environ['ENDPOINT_SERVER_PORT'])
else:
    raise Exception("please declare environment variable 'ENDPOINT_SERVER_PORT'")

if 'SIMULATOR_SERVER_HOST' in os.environ:
    SIMULATOR_SERVER_HOST = os.environ['SIMULATOR_SERVER_HOST']
else:
    raise Exception("please declare environment variable 'SIMULATOR_SERVER_HOST'")

if 'SIMULATOR_SERVER_PORT' in os.environ:
    SIMULATOR_SERVER_PORT = int(os.environ['SIMULATOR_SERVER_PORT'])
else:
    raise Exception("please declare environment variable 'SIMULATOR_SERVER_PORT'")

if 'FRIGATE_SERVER_NAME' in os.environ:
    FRIGATE_SERVER_NAME = os.environ['FRIGATE_SERVER_NAME']
else:
    raise Exception("please declare environment variable 'FRIGATE_SERVER_NAME'")




#SUMO_ROADNET_PATH = './sumo/net.net.xml'
#SUMO_STEPS = 10000
#SUMO_BINARY = "/usr/bin/sumo"
#SUMO_SIM_FILE = "./sumo/simulation.sumocfg"
#SUMO_CMD = [SUMO_BINARY, "-c", SUMO_SIM_FILE, "--save-state.period", "10", "--save-state.suffix", ".xml"]
#VEHICLES_TO_ROUTE = "PERIODICAL_STEP"
#ROUTING_STEP_PERIOD = 10

