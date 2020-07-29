# -*- coding: utf-8 -*-
"""
"""

import os
import random
import igraph as ig
import jinja2
import logging
from lxml import etree as etree
from airflow.models.baseoperator import BaseOperator
from airflow.utils.decorators import apply_defaults
from sumo_util import generate_traffic_rnd, generate_traffic_sp, get_plainxml_net

logger = logging.getLogger("airflow.task")

SUMO_CFG_TEMPLATE = """
<!-- Automatically generated by AGR -->
<configuration>

    <input>
        <net-file value="{{sumo_net_filen}}"/>
        <route-files value="{{routes_filen}}"/>
    </input>

    <time>
        <begin value="{{sim_begin}}"/>
        <end value="{{sim_end}}"/>
        <step-length value="{{sim_step_length}}"/>
    </time>

</configuration>
"""


class TRAFFIC_TYPE:
    random = 0
    shortest_path = 1


class FrigateSimulationSetupOperator(BaseOperator):

    @apply_defaults
    def __init__(
            self,
            name: str,
            graphml_roadnet_file: str,
            sim_folder: str,
            num_vehicles: int,
            source_nodes: list,
            target_nodes: list,
            traffic_type: int,
            depart_step: int,
            sim_begin: float,
            sim_end: float,
            sim_step_length: float,
            *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self.name = name
        self.graphml_roadnet_file = graphml_roadnet_file        
        self.sim_folder = sim_folder
        self.num_vehicles = num_vehicles
        self.source_nodes = source_nodes
        self.target_nodes = target_nodes
        self.traffic_type = traffic_type
        self.depart_step = depart_step
        self.sim_begin = sim_begin
        self.sim_end = sim_end
        self.sim_step_length = sim_step_length

    #    INPUT_DIRECTED_GRAPHML_FILEN = "irregular_grid_dag2.graphml" # generated with create_sumo_roadnet.pynb
    #    OUTPUT_ROUTES_XML_FILEN = "routes.rou.xml"
    #    NUM_VEHICLES = 1000
    #    SOURCES = [0, 1, 2]
    #    TARGETS = [33] # in DAGs the target should be the node with outdegree = 0

    def _generate_traffic(self, g) -> None:

        routes_xml_file = f"{self.sim_folder}/routes.rou.xml"

        if self.traffic_type == TRAFFIC_TYPE.random:
            generate_traffic_rnd(g=g,
                                 num_vehicles=self.num_vehicles,
                                 sources=self.source_nodes,
                                 targets=self.target_nodes,
                                 routes_xml_filen=routes_xml_file,
                                 depart_step=self.depart_step)
        elif self.traffic_type == TRAFFIC_TYPE.shortest_path:
            generate_traffic_sp(g=g,
                                num_vehicles=self.num_vehicles,
                                sources=self.source_nodes,
                                targets=self.target_nodes,
                                routes_xml_filen=routes_xml_file,
                                depart_step=self.depart_step)
        else:
            raise Exception(
                f"Unkown specified traffic type: {self.traffic_type}")
        return

    def _generate_sumo_roadnet(self, g) -> None:

        get_plainxml_net(g=g,
                         nod_xml_filen=f"{self.sim_folder}/nodes.nod.xml",
                         edg_xml_filen=f"{self.sim_folder}/edges.edg.xml",
                         net_xml_filen=f"{self.sim_folder}/roadnet.net.xml")
        return

    def _generate_sumo_cfg(self) -> None:

        render = jinja2.Template(SUMO_CFG_TEMPLATE).render(
            sumo_net_filen="roadnet.net.xml",
            routes_filen="routes.rou.xml",
            sim_begin=self.sim_begin,
            sim_end=self.sim_end,
            sim_step_length=self.sim_step_length
        )
        sumo_cfg_file = f"{self.sim_folder}/simulation.sumocfg"
        fp = open(sumo_cfg_file, "w+")
        fp.write(render)
        fp.close()

    def execute(self, context):

        logger.info(f"Hello from FrigateSumoSetupOperator")
        
        logger.info(f"loading graph {self.graphml_roadnet_file}")
        g = ig.Graph.Read_GraphML(self.graphml_roadnet_file)
        logger.info(f"loaded graph: {g.summary()}")

        logger.info(f"creating sim folder {self.sim_folder}")
        os.mkdir(self.sim_folder)

        logger.info(f"generating traffic of type {self.traffic_type}")
        self._generate_traffic(g=g)

        logger.info(f"generating SUMO NET XML file ...")
        self._generate_sumo_roadnet(g=g)

        logger.info(f"generating simulation cfg file ...")
        self._generate_sumo_cfg()
 
        logger.info(f"Done.")

        return f"Done {self.name}."
