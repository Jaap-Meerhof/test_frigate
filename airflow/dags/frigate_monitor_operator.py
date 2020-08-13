import logging
from airflow.models.baseoperator import BaseOperator
from airflow.utils.decorators import apply_defaults
from frigate_monitor_client import FrigateMonitorClient
from wait_for_tcp_port import wait_for_port

#logger = logging.getLogger(__name__)
logger = logging.getLogger("airflow.task")


class FrigateMonitorOperator(BaseOperator):

    @apply_defaults
    def __init__(
            self,
            name: str,            
            *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self.name = name
        
    def _start_monitor(self):        
        mon_client = FrigateMonitorClient(
            monitor_host="127.0.0.1", monitor_port=83)        
        done = mon_client.start_monitor()        
        return done

    def execute(self, context):

        logger.info(f"Hello from operator {self.name}")

        logger.info(f"Waiting for Monitor server")
        wait_for_port(port=83, host="127.0.0.1", timeout=60)
        logger.info(f"Monitor server operational!")

        logger.info("starting monitor ...")
        done = self._start_monitor()
        if not done:
            raise Exception("ERROR: Frigate Monitor Server did not start correctly!")
        return f"Done {self.name}."
