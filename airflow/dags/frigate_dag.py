from datetime import timedelta

from airflow import DAG
from airflow.operators.bash_operator import BashOperator
from airflow.utils.dates import days_ago
from frigate_swarm_operator import FrigateSwarmOperator

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

dag = DAG(
    'frigate-dag-2',
    default_args=default_args,
    description='A simple tutorial DAG',
    schedule_interval=None,
)

t1 = FrigateSwarmOperator(
    name="FrigateSimulatorClientTest1",
    scale=8,
    frigate_path="/home/alberto/Dropbox/alberto/projects/frigate" ,
    task_id='FrigateSimulatorClientTest1',
    dag=dag
)

t1