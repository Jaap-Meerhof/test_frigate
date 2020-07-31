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
from util import get_random_string
from distutils.dir_util import copy_tree

#logger = logging.getLogger(__name__)
logger = logging.getLogger("airflow.task")

class SimulatorVehiclesToRoute:
    CHANGED_EDGE = "CHANGED_EDGE"
    ONLY_DEPARTED = "ONLY_DEPARTED"
    PERIODICAL_STEP = "PERIODICAL_STEP"

FRIGATE_STACK_NAME = "frigate"

class FrigateDeployOperator(BaseOperator):

    @apply_defaults
    def __init__(
            self,
            name: str,
            scale: int,
            frigate_path: str,

            input_sim_folder: str,  # path should NOT include trail '/'
            output_sim_folder: str, # path should NOT include trail '/'
            target_nodes: list,
            
            eta: float,  # for stream
            # for simulator. Only works for vehicles_to_route = SimulatorVehiclesToRoute.PERIODICAL_STEP
            routing_step_period: str,
            sim_steps: int,  # for simulator
            # a constant for the simulator. Use the SimulatorVehiclesToRoute enum.
            vehicles_to_route: str,
            
            *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self.name = name
        self.scale = scale
        self.frigate_path = frigate_path

        self.input_sim_folder = input_sim_folder
        self.output_sim_folder = output_sim_folder
        self.target_nodes = target_nodes

        self.eta = eta
        self.routing_step_period = routing_step_period
        self.sim_steps = sim_steps
        self.vehicles_to_route = vehicles_to_route
        
    def _render_template(self):

        # as many stream servers as the scale value
        stream_servers = [{
            "name": f"frigate-stream-{i}",
            "port": 6066 + i
        } for i in range(self.scale)]
        template = open(
            f"{self.frigate_path}/airflow/dags/docker-compose.yml.template", "r+").read()

        wait_for_it_cmds = [
            f"./wait-for-it.sh {stream_server['name']}:{stream_server['port']} --strict --" for stream_server in stream_servers]

        wait_for_it_cmd = " ".join(wait_for_it_cmds)

        sim_foldern = os.path.basename(self.output_sim_folder)

        # one simulator server per target node, each running a simulation 
        # for a different target node
        simulator_servers = [{
            "name": f"frigate-simulator-{i}",
            "sim_folder": f"/var/data/{sim_foldern}/{target_node}",
            "port": 8010 + i
        } for i, target_node in enumerate(self.target_nodes)]

        render = jinja2.Template(template).render(
            stream_servers=stream_servers,
            wait_for_it_cmd=wait_for_it_cmd,
            scale=self.scale,
            sim_foldern=sim_foldern,
            eta=self.eta,
            routing_step_period=self.routing_step_period,
            sim_steps=self.sim_steps,
            vehicles_to_route=self.vehicles_to_route,
            simulator_servers=simulator_servers
        )
        fp = open(f"{self.frigate_path}/frigate/docker-compose.yml", "w+")
        fp.write(render)
        fp.close()

    def _wait_for_simulators(self):
        """
        Wait for all deployed simulator servers.
        """
        for i in range(len(self.target_nodes)):
            wait_for_port(port=8010 + i, host="127.0.0.1", timeout=60)
            logger.info(f"Simulator at port {8010 + i} operational!")
        return
        
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
    
    def execute(self, context):

        logger.info(f"Hello from operator {self.name}")

        logger.info("rendering template ...")
        self._render_template()

        #random_string = get_random_string(6)
        stack_name = FRIGATE_STACK_NAME

        logger.info("preparing sim folder ...")
        os.mkdir(path=self.output_sim_folder)
        copy_tree(src=self.input_sim_folder, dst=self.output_sim_folder)
        
        logger.info(f"deploying stack {stack_name} ...")
        self._deploy_stack(stack_name=stack_name)
                
        logger.info("waiting 180 secs ...")
        time.sleep(180)
        logger.info("waiting for simulator servers to start ...")
        self._wait_for_simulators()
        
        logger.info(f"Done.")

        return f"Done {self.name}."
