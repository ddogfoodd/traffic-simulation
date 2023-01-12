import os, sys
import argparse
import traci
import numpy as np


def parseChar(char):
    """
    :param char: column index of the intersection (e.G. 'A', 'B', ...)
    :return: Returns the converted column index of the intersection to an int
    """

    if char == 'A':
        return 0
    elif char == 'B':
        return 1
    elif char == 'C':
        return 2
    elif char == 'D':
        return 3
    elif char == 'E':
        return 4
    else:
        return -1


class SumoLaneID:

    def __init__(self, lane_id):
        self.originFirstCoordinate = parseChar(str(lane_id)[0])
        self.originSecondCoordinate = int(str(lane_id)[1])
        self.destinationFirstCoordinate = parseChar(str(lane_id)[2])
        self.destinationSecondCoordinate = int(str(lane_id)[3])
        self.laneIndex = int(str(lane_id)[5])


    def upcommingWaiting(self):
        """
        :return: Returns the location at the next intersection
            north: 0
            east: 1
            south: 2
            west: 3
        """

        if self.originSecondCoordinate > self.destinationSecondCoordinate:
            return 0
        elif self.originFirstCoordinate > self.destinationFirstCoordinate:
            return 1
        elif self.originSecondCoordinate < self.destinationSecondCoordinate:
            return 2
        elif self.originFirstCoordinate < self.destinationFirstCoordinate:
            return 3
        else:
            return -1


class SumoBaseSimulation:

    def __init__(self, args):

        self.sumo_config_path = args.sumo_config_path
        self.sumo_env = args.sumo_cmd_env
        self.all_lanes_density = []

    def calc_lane_density(self, laneID):
        num = traci.lane.getLastStepVehicleNumber(laneID)
        density = num / traci.lane.getLength(laneID) / 100.
        return density

    def getBoardState(self):
        """
        getBoardState() -> int[25][20]
        :return: the board state. The lines represent the respective intersection. The columns represent the number of cars
        that are 100 meters before the intersection at the respective traffic light.
        """

        junctions = np.zeros((25, 20))
        for vehicle in traci.vehicle.getIDList():
            next_tls = traci.vehicle.getNextTLS(vehicle)
            signal = traci.vehicle.getSignals(vehicle)
            # traci.vehicle.getLaneID(vehicle)[0]==':' == Vehicle is located on the intersection
            if len(next_tls) >= 1 and not(traci.vehicle.getLaneID(vehicle)[0]==':'):
                sumoLaneId = SumoLaneID(traci.vehicle.getLaneID(vehicle))
                # from a distance of 100 the signal is switched on
                if float(next_tls[0][2]) < 100:
                    junctionIndex = self.junctionIDListToIndex(next_tls[0][0])
                    tLIndex = sumoLaneId.upcommingWaiting() * 5 + self.getTLSummand(signal, sumoLaneId)
                    junctions[junctionIndex][tLIndex] += 1
        return junctions

    def junctionIDListToIndex(self, junction):
        """
        :param junction: SUMO ID der junction
        :return: 1D Index of the SUMO ID
        """
        firstCoordinate = parseChar(junction[0])
        secondCoordinate = int(junction[1])
        return firstCoordinate + (secondCoordinate * 5)


    def getTLSummand(self, signal, sumoLaneId):
        """
        :param signal: signal of an vehicle

        signal == 0: no blinker Active & no brake lights active
        signal == 8: no blinker Active & brake lights active
        signal == 1: right blinker Active & no brake lights active
        signal == 9: right blinker Active & brake lights active
        signal == 2: left blinker Active & no brake lights active
        signal == 10: left blinker Active & brake lights active
        :param sumoLaneId: SumoLaneID() of an vehicle
        :return: the position at a traffic light

        position == 0: right turn
        position == 1: straight ahead, right lane
        position == 2: straight ahead, left lane
        position == 3: left/U turn
        """
        if (signal == 0 or signal == 8) and sumoLaneId.laneIndex == 0:
            return 1
        elif (signal == 0 or signal == 8) and sumoLaneId.laneIndex == 1:
            return 2
        elif signal == 1 or signal == 9:
            return 0
        elif signal == 2 or signal == 10:
            return 3
        else:
            print(f'error in getTLSummand for Signal: {signal} and sumoLaneIndex: {sumoLaneId.laneIndex}')
            return -1

    def main(self):

        if 'SUMO_HOME' in os.environ:
            tools = os.path.join(os.environ['SUMO_HOME'], 'tools')
            print("SUMO_PATH : ", tools)
            sys.path.append(tools)
        else:
            sys.exit("please declare environment variable 'SUMO_HOME'")

        traci.start([self.sumo_env, "-c", self.sumo_config_path])

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
            if (step % 10 == 0):
                print(self.getBoardState())
                print("Average Network Density at time step " + str(step) + " : ", np.mean(self.all_lanes_density))
        traci.close()

        # x = np.arange(1,10001,1)
        # plt.plot(x,self.all_lanes_density)
        # plt.show()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="For parsing values and IDs for network/edges/lanes/vehicles/trafficlights")

    parser.add_argument("--sumo_config_path", help="Path for SUMO config file", default="../xml/scenario1/grid.sumocfg")
    parser.add_argument("--sumo_cmd_env", help="Sumo execution environment", default="sumo-gui")

    args = parser.parse_args()

    simulator = SumoBaseSimulation(args)
    simulator.main()