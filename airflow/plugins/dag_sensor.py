# taken from https://stackoverflow.com/a/61991942

import logging

from airflow.plugins_manager import AirflowPlugin
from airflow.models import DagRun
from airflow.sensors.base_sensor_operator import BaseSensorOperator
from airflow.utils.db import provide_session
from airflow.utils.decorators import apply_defaults
from airflow.utils.state import State

logger = logging.getLogger('airflow.dag_sensor')


class DagSensor(BaseSensorOperator):
    """
    Sensor that check if a Dag is currently running.
    It proceeds only if the Dag is in not running.
    """

    template_fields = ['external_dag_id']
    ui_color = '#FFFFCC'

    @apply_defaults
    def __init__(self,
                 external_dag_id,
                 *args,
                 **kwargs):
        super(DagSensor, self).__init__(*args, **kwargs)
        self.external_dag_id = external_dag_id

    @provide_session
    def poke(self, context, session=None):
        dag_run = DagRun

        count = session.query(dag_run).filter(
            dag_run.dag_id == self.external_dag_id,
            dag_run._state.in_([State.RUNNING])
        ).count()
        session.commit()
        session.close()

        logger.info(f'Dag {self.external_dag_id} in running status: {count}')

        if count > 0:
            return False
        else:
            return True


class DagSensorPlugin(AirflowPlugin):
    name = 'dag_sensor_plugin'
    operators = [DagSensor]