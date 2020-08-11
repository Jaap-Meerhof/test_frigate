from datetime import timedelta
from airflow import DAG
from airflow.operators.bash_operator import BashOperator
from airflow.utils.dates import days_ago
from frigate_setup_operator import FrigateSetupOperator, TRAFFIC_TYPE
from frigate_deploy_operator import FrigateDeployOperator, SimulatorVehiclesToRoute
from frigate_simulation_operator import FrigateSimulationOperator
from frigate_remove_operator import FrigateRemoveOperator
from frigate_initialization_operator import FrigateInitializationOperator

default_args = {
    'owner': 'airflow',
    'depends_on_past': False,
    'start_date': days_ago(2),
    'email': ['agrobledo@gmail.com'],
    'email_on_failure': False,
    'email_on_retry': False,
    'retries': 0,
    'retry_delay': timedelta(minutes=1),
}

SOURCE_NODES = [0, 1, 2]
TARGET_NODES = [33, 33, 33, 33, 33, 33, 33, 33] # the length of this array defines the number of Simulator and Endpoint servers
DEPLOY_SCALE = 8 # number of Stream workers


with DAG(
    'frigate-full-dag3',
    default_args=default_args,
    description='Frigate full DAG',
    schedule_interval=None,
) as dag:
    
    setup_oprs = []
    for simulator_id, target_node in enumerate(TARGET_NODES):
        setup_opr = FrigateSetupOperator(
            name=f"FrigateSetupOperator{simulator_id}",
            graphml_roadnet_file="/home/alberto/Dropbox/alberto/projects/frigate/frigate/data/irregular_grid_dag2/irregular_grid_dag2.graphml",
            sim_folder="/home/alberto/Dropbox/alberto/projects/frigate/frigate/data/dag_test_input",
            num_vehicles=1000,
            source_nodes=SOURCE_NODES,
            target_node=target_node,
            traffic_type=TRAFFIC_TYPE.shortest_path,
            depart_step=1,
            sim_begin=0,
            sim_end=5000,
            sim_step_length=0.2,
            task_id=f"FrigateSetupOperator{simulator_id}",
            vehicle_id_suffix=simulator_id,
            simulator_id=simulator_id
        )
        setup_oprs.append(setup_opr)
             
    deploy_opr = FrigateDeployOperator(
        name="FrigateDeployOperator",
        scale=DEPLOY_SCALE,
        frigate_path="/home/alberto/Dropbox/alberto/projects/frigate",
        input_sim_folder="/home/alberto/Dropbox/alberto/projects/frigate/frigate/data/dag_test_input",
        output_sim_folder="/home/alberto/Dropbox/alberto/projects/frigate/frigate/data/dag_test_output",
        target_nodes=TARGET_NODES,
        eta=0.5,
        routing_step_period=10,
        sim_steps=1000,
        vehicles_to_route=SimulatorVehiclesToRoute.PERIODICAL_STEP,
        task_id="FrigateDeployOperator"
    ) 

    init_opr = FrigateInitializationOperator(
        name="FrigateInitializationOperator",
        task_id="FrigateInitializationOperator"
    )   

    sim_oprs = []
    for simulator_id, _ in enumerate(TARGET_NODES):
        sim_opr = FrigateSimulationOperator(
            name=f"FrigateSimulationOperator{simulator_id}",
            simulator_id=simulator_id,
            task_id=f"FrigateSimulationOperator{simulator_id}"
        )
        sim_oprs.append(sim_opr)
    
    remove_opr = FrigateRemoveOperator(
        name="FrigateRemoveOperator",
        task_id="FrigateRemoveOperator"
    )

    #####
    #####
    
    for setup_opr in setup_oprs:
        setup_opr >> deploy_opr
    deploy_opr >> init_opr
    for sim_opr in sim_oprs:
        init_opr >> sim_opr
        sim_opr >> remove_opr
        
    
    
