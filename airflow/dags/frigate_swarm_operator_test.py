from frigate_swarm_operator import FrigateSwarmOperator, SimulatorVehiclesToRoute

t1 = FrigateSwarmOperator(
    name="FrigateSimulatorClient_TEST",
    scale=2,
    frigate_path="/home/alberto/Dropbox/alberto/projects/frigate",
    sim_foldern = "test",
    eta = 0.5,
    routing_step_period = 10,
    sim_steps = 10,
    vehicles_to_route = SimulatorVehiclesToRoute.PERIODICAL_STEP,
    task_id='1'    
)

if __name__ == "__main__":
    print("executing operator ...")
    t1.execute(context={})    
    print("done.")