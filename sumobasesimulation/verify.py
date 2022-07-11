import os, sys
import argparse
import traci
import traci.constants as tc
import numpy as np
import matplotlib.pyplot as plt



class SumoBaseSimulation:


     def __init__(self,args):

         self.sumo_config_path = args.sumo_config_path
         self.sumo_env = args.sumo_cmd_env
         self.all_lanes_density = []


     def calc_lane_density(self,laneID):
         num = traci.lane.getLastStepVehicleNumber(laneID)
         density = num / traci.lane.getLength(laneID) / 100.
         return density

     def main(self):

         if 'SUMO_HOME' in os.environ:
             tools = os.path.join(os.environ['SUMO_HOME'], 'tools')
             print ("SUMO_PATH : ",tools)
             sys.path.append(tools)
         else:
             sys.exit("please declare environment variable 'SUMO_HOME'")

         traci.start([self.sumo_env, "-c",self.sumo_config_path])


         for step in range(10000):
             traci.simulationStep()
             # print("Time Step : ",step)
             lanes = traci.lane.getIDList()
             lane_density = []
             for laneID in lanes:
                 density = self.calc_lane_density(laneID)
                 lane_density.append(density)


             # trafficlights = traci.trafficlight.getIDList()
             # red_state = 'rrrrrGGyyyrrrrrGGggy'
             # green_state = 'GGggyrrrrrggyyyrrrrr'
             # for tlsID in trafficlights:
             #     # print(tlsID, traci.trafficlight.getRedYellowGreenState(tlsID))
             #
             #     if(step % 50 ):
             #         traci.trafficlight.setRedYellowGreenState(tlsID,red_state)
             #     elif(step%90):
             #         traci.trafficlight.setRedYellowGreenState(tlsID,green_state)
             self.all_lanes_density.append(np.mean(lane_density))
             if (step%1000==0):
                 print("Average Network Density at time step "+str(step)+" : ",np.mean(self.all_lanes_density))
         traci.close()

         # x = np.arange(1,10001,1)
         # plt.plot(x,self.all_lanes_density)
         # plt.show()





if __name__ == "__main__":

    parser = argparse.ArgumentParser(description="For parsing values and IDs for network/edges/lanes/vehicles/trafficlights")

    parser.add_argument("--sumo_config_path",help="Path for SUMO config file", default="../xml/scenario1/grid.sumocfg")
    parser.add_argument("--sumo_cmd_env",help="Sumo execution environment", default="sumo-gui")

    args = parser.parse_args()

    simulator = SumoBaseSimulation(args)
    simulator.main()

