from frigate_deploy_operator import FrigateDeployOperator, SimulatorVehiclesToRoute

t1 = FrigateDeployOperator(
    name="FrigateDeployOperator_TEST",
    scale=2,
    frigate_path="/home/alberto/Dropbox/alberto/projects/frigate",
    input_sim_folder = "/home/alberto/Dropbox/alberto/projects/frigate/frigate/data/input_test",
    output_sim_folder = "/home/alberto/Dropbox/alberto/projects/frigate/frigate/data/output_test",
    target_nodes = [31, 32, 33],
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