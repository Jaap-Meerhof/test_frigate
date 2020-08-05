import logging
import time
from airflow.models.baseoperator import BaseOperator
from airflow.utils.decorators import apply_defaults
from frigate_simulator_client import FrigateSimulatorClient

#logger = logging.getLogger(__name__)
logger = logging.getLogger("airflow.task")


class FrigateInitializationOperator(BaseOperator):

    @apply_defaults
    def __init__(
            self,
            name: str,            
            *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self.name = name
        
    def _initialize_qtable(self):        
        sim_client = FrigateSimulatorClient(
            simulator_host="127.0.0.1", simulator_port=8010)        
        sim_client.initialize_qtable()      
        logger.info(f"Waiting 180 secs ...")
        time.sleep(180)  
        return

    def execute(self, context):

        logger.info(f"Hello from operator {self.name}")
        logger.info(f"requesting initialization of Q-table to frigate-simulator-0 ...")
        self._initialize_qtable()
        logger.info("Done.")
        return f"Done {self.name}."
