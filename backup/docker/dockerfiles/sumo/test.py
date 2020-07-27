import os
import sys

if 'SUMO_HOME' in os.environ:
    tools = os.path.join(os.environ['SUMO_HOME'], "tools")
    sys.path.append(tools)
else:   
    print("please declare environment variable 'SUMO_HOME'")
import traci

SUMO_BINARY = os.environ['SUMO_HOME'] + "/bin/sumo"
SUMO_SIM_FILE = "corridor.sumocfg"
SUMO_CMD = [SUMO_BINARY, "-c", SUMO_SIM_FILE, "--save-state.period", "10", "--save-state.suffix", ".xml"]

traci.start(SUMO_CMD)
step = 0
while step < 500:  
    traci.simulationStep()
    print("Simulation Time: %s" %str(traci.simulation.getTime()))
    print("Number of arrived vehicles: %d"%len(traci.vehicle.getIDList()))
    step += 1
traci.close()
print("done.")
