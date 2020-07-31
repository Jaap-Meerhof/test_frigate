import logging
from airflow.models.baseoperator import BaseOperator
from airflow.utils.decorators import apply_defaults
from frigate_simulator_client import FrigateSimulatorClient

#logger = logging.getLogger(__name__)
logger = logging.getLogger("airflow.task")


class FrigateSimulationOperator(BaseOperator):

    @apply_defaults
    def __init__(
            self,
            name: str,
            simulator_id: int,
            *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self.name = name
        self.simulator_id = simulator_id

    def _run_simulation(self):

        logger.info(f"running simulation for simulator {self.simulator_id}!")
        sim_client = FrigateSimulatorClient(
            simulator_host="127.0.0.1", simulator_port=8010 + self.simulator_id)
        done = False
        for obj in sim_client.run_stream():
            logger.info(obj["message"])
            if obj["message"] == "Simulation done.":
                done = True
                break
        return done

    def execute(self, context):

        logger.info(f"Hello from operator {self.name}")
        logger.info("starting simulation ...")
        done = self._run_simulation()
        if not done:
            raise Exception("ERROR: Simulation did not finish correctly.")
        return f"Done {self.name}."
