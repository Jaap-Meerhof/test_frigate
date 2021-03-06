from datetime import timedelta
from airflow import DAG
from airflow.operators.bash_operator import BashOperator
from airflow.operators.dagrun_operator import TriggerDagRunOperator
from airflow.utils.dates import days_ago
from airflow.operators import DagSensor
from frigate_setup_operator import FrigateSetupOperator, TRAFFIC_TYPE
from frigate_deploy_operator import FrigateDeployOperator, SimulatorVehiclesToRoute
from frigate_simulation_operator import FrigateSimulationOperator
from frigate_remove_operator import FrigateRemoveOperator
from frigate_initialization_operator import FrigateInitializationOperator
from frigate_monitor_operator import FrigateMonitorOperator


SOURCE_NODES = [0, 1, 2]
GRAPHML_ROADNET_FILE = "/home/alberto/Dropbox/alberto/projects/frigate/frigate/data/irregular_grid_dag2/irregular_grid_dag2.graphml"
SIM_FOLDER = "/home/alberto/Dropbox/alberto/projects/frigate/frigate/data/input"
FRIGATE_PATH = "/home/alberto/Dropbox/alberto/projects/frigate"
FRIGATE_DATA_FOLDER = "/home/alberto/Dropbox/alberto/projects/frigate/frigate/data"
OUTPUT_SIM_FOLDER = "/home/alberto/Dropbox/alberto/projects/frigate/frigate/data/output"
OUTPUT_MONITOR_FOLDER = "/home/alberto/Dropbox/alberto/projects/frigate/frigate/data/monitor"
SIM_STEPS = 1000
NUM_VEHICLES = 5000
SIM_END = 5000
VEHICLES_TO_ROUTE = SimulatorVehiclesToRoute.CHANGED_EDGE
ETA = 0.5
ROUTING_STEP_PERIOD = 10

CONFIGURATIONS = {
    "frigate-dag-scale1": {
        "scale": 1,
        "target_nodes": [33, 33, 33, 33]
    },

    "frigate-dag-scale2": {
        "scale": 2,
        "target_nodes": [33, 33, 33, 33]
    },

    "frigate-dag-scale4": {
        "scale": 4,
        "target_nodes": [33, 33, 33, 33]
    },

    "frigate-dag-scale8": {
        "scale": 8,
        "target_nodes": [33, 33, 33, 33]
    }
}

DEFAULT_ARGS = {
    'owner': 'airflow',
    'start_date': days_ago(2),    
    'email_on_failure': False,
    'email_on_success': False,
    'retries': 0
}


def generate_frigate_dag(dag_name, scale, target_nodes):
    """
    Generate a DAG with a given DAG name, scale and target nodes.
    """
    
    dag = DAG(
        dag_name,
        default_args=DEFAULT_ARGS,
        description=f'Frigate DAG of scale {scale} and {len(target_nodes)} target nodes.',
        schedule_interval=None
    )

    with dag:
        
        setup_oprs = []
        for simulator_id, target_node in enumerate(target_nodes):
            setup_opr = FrigateSetupOperator(
                name=f"FrigateSetupOperator{simulator_id}",
                graphml_roadnet_file=GRAPHML_ROADNET_FILE,
                sim_folder=SIM_FOLDER,
                num_vehicles=NUM_VEHICLES,
                source_nodes=SOURCE_NODES,
                target_node=target_node,
                traffic_type=TRAFFIC_TYPE.shortest_path,
                depart_step=1,
                sim_begin=0,
                sim_end=SIM_END,
                sim_step_length=0.2,
                task_id=f"FrigateSetupOperator{simulator_id}",
                vehicle_id_suffix=simulator_id,
                simulator_id=simulator_id
            )
            setup_oprs.append(setup_opr)

        deploy_opr = FrigateDeployOperator(
            name="FrigateDeployOperator",
            scale=scale,
            frigate_path=FRIGATE_PATH,
            input_sim_folder=SIM_FOLDER,
            output_sim_folder=OUTPUT_SIM_FOLDER,
            output_monitor_folder=OUTPUT_MONITOR_FOLDER,
            target_nodes=target_nodes,
            eta=ETA,
            routing_step_period=ROUTING_STEP_PERIOD,
            sim_steps=SIM_STEPS,
            vehicles_to_route=VEHICLES_TO_ROUTE,
            task_id="FrigateDeployOperator"
        )

        init_opr = FrigateInitializationOperator(
            name="FrigateInitializationOperator",
            task_id="FrigateInitializationOperator"
        )

        sim_oprs = []
        for simulator_id, _ in enumerate(target_nodes):
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

        mon_opr = FrigateMonitorOperator(
            name="FrigateMonitorOperator",
            task_id="FrigateMonitorOperator"
        )

        templated_command = """
        mkdir {{params.frigate_data_folder}}/{{params.dag_name}}
        mv {{params.frigate_data_folder}}/input {{params.frigate_data_folder}}/{{params.dag_name}}/input 
        mv {{params.frigate_data_folder}}/output {{params.frigate_data_folder}}/{{params.dag_name}}/output 
        mv {{params.frigate_data_folder}}/monitor {{params.frigate_data_folder}}/{{params.dag_name}}/monitor
        """
        move_data_opr = BashOperator(
            task_id='BashOperator-MoveData',
            bash_command=templated_command,
            params={'frigate_data_folder': FRIGATE_DATA_FOLDER,
                    'dag_name': dag_name}
        )

        #####
        #####

        for setup_opr in setup_oprs:
            setup_opr >> deploy_opr
        deploy_opr >> init_opr
        init_opr >> mon_opr
        for sim_opr in sim_oprs:
            mon_opr >> sim_opr
            sim_opr >> remove_opr
        remove_opr >> move_data_opr

    return dag

# generate a DAG for each configuration in CONFIGURATIONS
for dag_name, dag_conf in CONFIGURATIONS.items():
    frigate_dag = generate_frigate_dag(dag_name = dag_name, scale=dag_conf["scale"], target_nodes=dag_conf["target_nodes"])
    globals()[dag_name] = frigate_dag

# create the DAG that will trigger all the previously created DAGs
trigger_dag = DAG(
        "frigate-dag-all",
        default_args=DEFAULT_ARGS,
        description=f'DAG to trigger all Frigate DAGs.',
        schedule_interval=None
    )
with trigger_dag:
    prev_wait_sensor = None
    for dag_name in CONFIGURATIONS.keys():     

        trigger_opr = TriggerDagRunOperator(
            task_id=f"TriggerDagOperator-{dag_name}",
            trigger_dag_id=dag_name                        
        )
        
        #NOTE: Airflow sensors fail after they timeout. Default timeout is 1 week. See: https://airflow.apache.org/docs/stable/_api/airflow/sensors/base_sensor_operator/index.html
        wait_sensor = DagSensor(            
            task_id=f'DagSensor-{dag_name}',
            external_dag_id=dag_name,
            poke_interval=30            
        )
        

        if prev_wait_sensor:
            prev_wait_sensor >> trigger_opr >> wait_sensor
            prev_wait_sensor = wait_sensor
        else:
            trigger_opr >> wait_sensor
            prev_wait_sensor = wait_sensor
            continue

