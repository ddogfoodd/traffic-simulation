import os,sys
import numpy as np
import analysis
from matplotlib import pyplot as plt
import xml.etree.ElementTree as ET
import argparse
import traci
import traci.constants as tc


class CreateSimulation:

    def __init__(self,args):

        self.emission_output = "../xml/scenario1/emission_output.xml"
        self.sumo_config_path = args.sumo_config_path
        self.sumo_env = args.sumo_cmd_env
        self.sumo_home_path = ""
        self.network_path = "../xml/scenario1/grid.net.xml"
        self.route_path = "../xml/scenario1/route.xml"
        self.reroute_path = "../xml/scenario1/rerouter.add.xml"
        self.config_path = "../xml/scenario1/grid.sumocfg"
        self.grid_route = "../xml/scenario1/grid.rou.xml"


    def generate_network(self,grids,lanes,length):

        os.system("netgenerate --grid --grid.number="+str(grids)+" -L="+str(lanes)+" --default-junction-type \"traffic_light\" --grid.length="+str(length)+" --output-file="+self.network_path)

    def generate_vehicles(self,vehicles):
        os.system(self.sumo_home_path + "/randomTrips.py -n "+self.network_path+" -o "+self.route_path+" --begin 0 --end 1 --period 1 --flows " + str(vehicles))
        os.system("jtrrouter --route-files="+self.route_path+" --net-file="+self.network_path+" --output-file="+self.grid_route+" --begin 0 --end 10000 --accept-all-destinations")
        os.system(self.sumo_home_path + "/generateContinuousRerouters.py -n "+self.network_path+" --end 10000 -o "+self.reroute_path)
        print(self.config_path)
        tree = ET.parse(self.config_path)
        root = tree.getroot()
        for child in root:
            if (child.tag == 'output'):
                for child2 in child:
                    child2.attrib['value'] = 'grid.output' + str(vehicles) + '.xml'
        with open(self.config_path, 'wb') as f:
            tree.write(f)
        os.system("sumo-gui -c "+self.config_path+" --device.fcd.period 100")

    def build_network(self):

        if 'SUMO_HOME' in os.environ:
            self.sumo_home_path = os.path.join(os.environ['SUMO_HOME'], 'tools')
            print("SUMO_PATH : ", self.sumo_home_path)
            sys.path.append(self.sumo_home_path)
        else:
            sys.exit("please declare environment variable 'SUMO_HOME'")


        if not os.path.exists(self.network_path):
            self.generate_network(5,2,500)
        else:
            self.generate_network(5,2,500)

        self.generate_vehicles(500)




if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        description="For parsing values and IDs for network/edges/lanes/vehicles/trafficlights")

    parser.add_argument("--sumo_config_path", help="Path for SUMO config file", default="../xml/scenario1")
    parser.add_argument("--sumo_cmd_env", help="Sumo execution environment", default="sumo-gui")

    args = parser.parse_args()

    simulator = CreateSimulation(args)
    simulator.build_network()