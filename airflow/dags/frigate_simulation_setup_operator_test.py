from frigate_simulation_setup_operator import FrigateSimulationSetupOperator, TRAFFIC_TYPE

t1 = FrigateSimulationSetupOperator(
    name="FrigateSwarmOperator_TEST",
    graphml_roadnet_file="/home/alberto/Dropbox/alberto/projects/frigate/frigate/data/irregular_grid_dag2/irregular_grid_dag2.graphml",
    sim_folder="/home/alberto/Dropbox/alberto/projects/frigate/frigate/data/test",
    num_vehicles=1000,
    source_nodes=[0, 1, 2],
    target_nodes=[33],
    traffic_type=TRAFFIC_TYPE.shortest_path,
    depart_step=1,
    sim_begin=0,
    sim_end=5000,
    sim_step_length=0.2,
    task_id = "1"
)

if __name__ == "__main__":
    print("executing operator ...")
    t1.execute(context={})
    print("done.")