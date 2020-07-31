from datetime import timedelta
from airflow import DAG
from airflow.operators.bash_operator import BashOperator
from airflow.utils.dates import days_ago
from frigate_setup_operator import FrigateSetupOperator, TRAFFIC_TYPE
from frigate_deploy_operator import FrigateDeployOperator, SimulatorVehiclesToRoute
from frigate_simulation_operator import FrigateSimulationOperator
from frigate_remove_operator import FrigateRemoveOperator

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

TARGET_NODES = [31, 32, 33]
SOURCE_NODES = [0, 1, 2]


with DAG(
    'frigate-full-dag3',
    default_args=default_args,
    description='Frigate full DAG',
    schedule_interval=None,
) as dag:
    
    setup_oprs = []
    for i, target_node in enumerate(TARGET_NODES):
        setup_opr = FrigateSetupOperator(
            name=f"FrigateSetupOperator{i}",
            graphml_roadnet_file="/home/alberto/Dropbox/alberto/projects/frigate/frigate/data/irregular_grid_dag2/irregular_grid_dag2.graphml",
            sim_folder="/home/alberto/Dropbox/alberto/projects/frigate/frigate/data/input_test",
            num_vehicles=1000,
            source_nodes=SOURCE_NODES,
            target_node=target_node,
            traffic_type=TRAFFIC_TYPE.shortest_path,
            depart_step=1,
            sim_begin=0,
            sim_end=5000,
            sim_step_length=0.2,
            task_id=f"FrigateSetupOperator{i}"
        )
        setup_oprs.append(setup_opr)
             
    deploy_opr = FrigateDeployOperator(
        name="FrigateDeployOperator",
        scale=2,
        frigate_path="/home/alberto/Dropbox/alberto/projects/frigate",
        input_sim_folder="/home/alberto/Dropbox/alberto/projects/frigate/frigate/data/input_test",
        output_sim_folder="/home/alberto/Dropbox/alberto/projects/frigate/frigate/data/output_test",
        target_nodes=TARGET_NODES,
        eta=0.5,
        routing_step_period=10,
        sim_steps=10,
        vehicles_to_route=SimulatorVehiclesToRoute.PERIODICAL_STEP,
        task_id="FrigateDeployOperator"
    )    

    sim_oprs = []
    for i, _ in enumerate(TARGET_NODES):
        sim_opr = FrigateSimulationOperator(
            name=f"FrigateSimulationOperator{i}",
            simulator_id=i,
            task_id=f"FrigateSimulationOperator{i}"
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
    for sim_opr in sim_oprs:
        deploy_opr >> sim_opr
        sim_opr >> remove_opr
    
    
