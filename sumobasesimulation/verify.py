import os, sys
import argparse
import traci
import numpy as np
from tf_agents.environments import py_environment
from tf_agents.specs import array_spec
from tf_agents.trajectories import time_step as ts
import tensorflow

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

class test():
    def __init__(self):
        print(1)


class SumoBaseSimulation(py_environment.PyEnvironment):

    def __init__(self):
        print('__init__')
        args = getArgs()
        print(args)
        self.sumo_config_path = args.sumo_config_path
        self.sumo_env = args.sumo_cmd_env
        self.all_lanes_density = 0
        self._action_spec = array_spec.BoundedArraySpec(shape = (), dtype = np.float32, minimum = 0, maximum = 1, name = 'action')
        self._observation_spec = array_spec.BoundedArraySpec(
            shape=(25, 20), dtype=np.int32, minimum=0, name='observation')
        self._state = np.zeros((25, 20))
        self._episode_ended = False
        self.maxSteps = 1000
        self.simulationSteps = self.maxSteps

    def action_spec(self):
        return self._action_spec

    def observation_spec(self):
        return self._observation_spec

    def _reset(self):
        if self.simulationSteps<self.maxSteps:
            traci.close()
        self._state = np.zeros((25, 20))
        self._episode_ended = False
        self.all_lanes_density = []
        self.simulationSteps = 1000
        return ts.restart(np.array([self._state], dtype=np.int32))

    def calc_lane_density(self, laneID):
        num = traci.lane.getLastStepVehicleNumber(laneID)
        density = num / traci.lane.getLength(laneID) / 100.
        return density

    def calc_density(self):
        lanes = traci.lane.getIDList()
        lane_density = []
        for laneID in lanes:
            density = self.calc_lane_density(laneID)
            lane_density.append(density)
        return lane_density

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
            if len(next_tls) >= 1 and not (traci.vehicle.getLaneID(vehicle)[0] == ':'):
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

    def _step(self, action):
        if self.simulationSteps == self.maxSteps:
            self.startSimulation()
        traci.simulationStep()
        if self._episode_ended:
            # The last action ended the episode. Ignore the current action and start
            # a new episode.
            return self.reset()

        tls = traci.trafficlight.getIDList()
        traci.trafficlight.setPhase(tls[5], action)

        self.simulationSteps -= 1
        self._episode_ended = self.simulationSteps == 0

        reward = self.all_lanes_density=np.mean(self.calc_density())
        if self._episode_ended:
            return ts.termination(np.array([self._state], dtype=np.int32), reward=reward)
        else:
            return ts.transition(
                np.array([self._state], dtype=np.int32), reward=reward, discount=1.0)

    def startSimulation(self):

        if 'SUMO_HOME' in os.environ:
            tools = os.path.join(os.environ['SUMO_HOME'], 'tools')
            print("SUMO_PATH : ", tools)
            sys.path.append(tools)
        else:
            sys.exit("please declare environment variable 'SUMO_HOME'")

        traci.start([self.sumo_env, "-c", self.sumo_config_path])


def getArgs():
    parser = argparse.ArgumentParser(
        description="For parsing values and IDs for network/edges/lanes/vehicles/trafficlights")
    parser.add_argument("--sumo_config_path", help="Path for SUMO config file", default="../xml/scenario1/grid.sumocfg")
    parser.add_argument("--sumo_cmd_env", help="Sumo execution environment", default="sumo")
    args, unknown = parser.parse_known_args()
    return args

if __name__ == '__main__':
    env = SumoBaseSimulation()
