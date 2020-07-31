import sh
import logging
from airflow.models.baseoperator import BaseOperator
from airflow.utils.decorators import apply_defaults
from frigate_deploy_operator import FRIGATE_STACK_NAME

#logger = logging.getLogger(__name__)
logger = logging.getLogger("airflow.task")


class FrigateRemoveOperator(BaseOperator):

    @apply_defaults
    def __init__(
            self,
            name: str,
            *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self.name = name

    def _remove_stack(self):
        try:
            cmd = sh.docker.stack.rm.bake(FRIGATE_STACK_NAME)
            logger.info(cmd)
            out = cmd()
            if "Error" in out:
                raise Exception(
                    f"An error occurred when running the command: {cmd} Output: {out}")
        except sh.ErrorReturnCode as e:
            raise Exception(
                f"An error occurred when running the command: {cmd} Exception: {e} Stdout: {e.stdout} Stderr: {e.stderr}")
        except Exception as e:
            raise Exception(
                f"An error occurred when running the command: {cmd} Exception: {e}")

    def execute(self, context):

        logger.info(f"Hello from operator {self.name}")
        logger.info(f"removing stack {FRIGATE_STACK_NAME} ...")
        self._remove_stack()
        return f"Done {self.name}."
