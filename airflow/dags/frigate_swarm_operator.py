# -*- coding: utf-8 -*-
"""
Frigate Docker Swarm operator for Airflow.
"""

import string
import sh
import os
import time
import jinja2
import requests
import logging
from airflow.models.baseoperator import BaseOperator
from airflow.utils.decorators import apply_defaults
from wait_for_tcp_port import wait_for_port
from frigate_simulator_client import FrigateSimulatorClient
from util import get_random_string

#logging.basicConfig(level=logging.DEBUG,
#                    format='%(asctime)s - %(levelname)s - %(name)s - %(message)s'
#                    )
logger = logging.getLogger("airflow.task")

class FrigateSwarmOperator(BaseOperator):

    @apply_defaults
    def __init__(
            self,
            name: str,
            scale: int,
            frigate_path: str,
            *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self.name = name
        self.scale = scale
        self.frigate_path = frigate_path
 
    def _render_template(self):
        stream_servers = [{
            "name": f"frigate-stream-{i}",
            "port": 6066 + i
        } for i in range(self.scale)]
        template = open(
            f"{self.frigate_path}/airflow/dags/docker-compose.yml.template", "r+").read()

        wait_for_it_cmds = [
            f"./wait-for-it.sh {stream_server['name']}:{stream_server['port']} --strict --" for stream_server in stream_servers]

        wait_for_it_cmd = " ".join(wait_for_it_cmds)

        render = jinja2.Template(template).render(
            stream_servers=stream_servers, wait_for_it_cmd=wait_for_it_cmd, scale=self.scale)
        fp = open(f"{self.frigate_path}/frigate/docker-compose.yml", "w+")
        fp.write(render)
        fp.close()

    def _wait_for_exit(self):
        wait_for_port(port=8010, host="127.0.0.1", timeout=60)
        logger.info("run!")
        sim_client = FrigateSimulatorClient(
            simulator_host="127.0.0.1", simulator_port=8010)
        sim_client.run()
        return

    def _wait_for_exit_stream(self):
        wait_for_port(port=8010, host="127.0.0.1", timeout=60)
        #logger.info("run (stream)!!")
        logger.info("run (stream)!!")
        sim_client = FrigateSimulatorClient(
            simulator_host="127.0.0.1", simulator_port=8010)        
        done = False
        for obj in sim_client.run_stream():
            # print(obj["message"])
            #print("/"*100, flush=True)
            #logger.info("/"*100)
            #print(line, flush=True)
            logger.info(obj["message"])
            if obj["message"] == "Simulation done.":
                done = True
                break
        return done

    def _deploy_stack(self, stack_name):
        try:
            cwd = os.getcwd()
            os.chdir(f"{self.frigate_path}/frigate")
            cmd = sh.docker.stack.deploy.bake(
                "--compose-file", "docker-compose.yml", stack_name)
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
        finally:
            os.chdir(cwd)

    def _remove_stack(self, stack_name):
        try:
            cmd = sh.docker.stack.rm.bake(stack_name)
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

        logger.info("rendering template ...")
        self._render_template()

        random_string = get_random_string(6)
        stack_name = f"frigate-{random_string}"

        logger.info(f"deploying stack {stack_name} ...")
        self._deploy_stack(stack_name=stack_name)
        logger.info("waiting 180 secs before running simulation ...")
        time.sleep(180)
        logger.info("run and waiting for exit ...")
        done = self._wait_for_exit_stream()
        
        logger.info(f"removing stack {stack_name} ...")
        self._remove_stack(stack_name=stack_name)
        
        if not done:
            raise Exception("ERROR: Simulation did not finish correctly.")

        logger.info(f"Done.")

        return f"Done {self.name}."
