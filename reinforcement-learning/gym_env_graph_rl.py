import random
from typing import Tuple, List, Optional

from gym.core import ObsType

from src.Constants import EPS
from src.Training.Utils import getPhasesNotYellowForTls

try:
    import libsumo as traci
except:
    import traci
import gym

import numpy as np
import xml.etree.ElementTree as ET


class SumoGraphEnviroment(gym.Env):

    def __init__(
        self,
        simulation_steps: int,
        simulation_start_steps: int = 0,
        simulation_yellow_steps: int = 0,
        simulation_step_size: int = 1,
        sumo_path: str = "sumo",
        sumo_net_path: str = "../xml/scenario1/grid.net.xml",
        sumo_cfg_path: str = "../xml/scenario1/grid.sumocfg",
        sumo_warning: bool = False,
        sumo_verbose: bool = False,
        sumo_routing_thread: int = 4,
        sumo_time_to_teleport: int = -1
    ):
        super().__init__()
        self.simulation_steps = simulation_steps
        self.simulation_start_steps = simulation_start_steps
        self.simulation_step_size = simulation_step_size
        self.simulation_yellow_steps = simulation_yellow_steps
        self.sumo_path = sumo_path
        self.sumo_net_path = sumo_net_path
        self.sumo_cfg_path = sumo_cfg_path
        self.sumo_routing_threads = sumo_routing_thread
        self.sumo_ttt = sumo_time_to_teleport
        self.sumo_verbose = sumo_verbose
        self.sumo_warning = sumo_warning

        self.simulation_cur_step = 0
        self.tls_to_node = {}
        self.adj = np.array([])

        self.startTraci()

        self.fillNodeDict()
        self.create_adj()

        self.node_to_tls = {v: k for k, v in self.tls_to_node.items()}
        self.tls_to_lanes = {tls: list(set(traci.trafficlight.getControlledLanes(tls))) for tls in self.tls_to_node.keys()}
        lane_list = list(set(filter(lambda x: ":" not in str(x), traci.lane.getIDList())))
        self.lane_last_step_halting_number = {lane: 0 for lane in lane_list}
        self.lane_lengths = {lane: traci.lane.getLength(lane) for lane in lane_list}
        self.lane_idx = {}
        for tls in sorted(self.tls_to_lanes.keys(), key=str):
            tls_lanes = set(traci.trafficlight.getControlledLanes(tls))
            for idx, lane in enumerate(sorted(tls_lanes, key=str)):
                self.lane_idx[lane] = idx
        self.tls_to_phases = {
            tls: getPhasesNotYellowForTls(tls) for tls in self.tls_to_node.keys()
        }
        self.tls_to_action_cnt = {tls: len(phases) for tls, phases in self.tls_to_phases.items()}
        self.tls_last_action = {tls: -1 for tls in self.tls_to_node.keys()}
        self.tls_cur_action = {tls: -1 for tls in self.tls_to_node.keys()}
        self.relevant_vehicle_signals = {0, 1, 2, 8, 9, 10}

        self.ACTION_CNT = max(self.tls_to_action_cnt.values())
        self.NODE_FEATURES_CNT = self.getNodeFeatures().shape[1]
        self.NODE_CNT = len(traci.trafficlight.getIDList())
        self.isFirstReset = True

    def startTraci(self):
        # TODO: make SUMO parameters optional and add option for GUI usage
        traci.start(
            [
                self.sumo_path,
                "-c", self.sumo_cfg_path,
                "--time-to-teleport", str(self.sumo_ttt),
                "--seed", str(random.randint(1, 999999)),
                "--verbose", str(self.sumo_verbose),
                "--routing-threads", str(self.sumo_routing_threads),
                "--max-depart-delay", str(self.simulation_start_steps),
                "--no-warnings", str(self.sumo_warning),
            ]
        )
        for _ in range(self.simulation_start_steps):
            traci.simulationStep()

    def create_adj(self):
        root = ET.parse(self.sumo_net_path).getroot()
        adj = np.eye(len(self.tls_to_node))
        for edge in root.findall('edge'):
            if 'from' in edge.keys():
                from_tls = self.tls_to_node[edge.attrib['from']]
                to_tls = self.tls_to_node[edge.attrib['to']]
                adj[from_tls, to_tls] = 1
        self.adj = adj

    def fillNodeDict(self):
        for node_id, tls_id in enumerate(traci.trafficlight.getIDList()):
            self.tls_to_node[tls_id] = node_id

    def getNodeFeatures(self) -> np.ndarray:
        LANES = max(self.lane_idx.values()) + 1
        FEATURES = 2
        TLS_CNT = len(self.node_to_tls)
        features = np.zeros((TLS_CNT, LANES, FEATURES))
        phases = np.zeros((TLS_CNT, 2))
        for idx, (tls, node) in enumerate(self.tls_to_node.items()):
            phases[idx, 0] = traci.trafficlight.getPhase(tls)
            phases[idx, 1] = self.tls_to_action_cnt[tls] / self.ACTION_CNT
            for lane in self.tls_to_lanes[tls]:
                lane_idx = self.lane_idx[lane]
                vehicles = traci.lane.getLastStepVehicleIDs(lane)
                features[idx, lane_idx, 0] = len(vehicles)
                features[idx, lane_idx, 1] = self.lane_last_step_halting_number[lane]
        maxima = np.max(features, axis=-2)
        maxima = maxima[:, None, :]
        features /= maxima + EPS
        features = np.reshape(features, (TLS_CNT, LANES * FEATURES))
        features = np.append(features, phases, axis=-1)

        return features

    def _get_obs(self):
        return {
            "nodes": self.getNodeFeatures(),
            "adj": self.adj
        }

    def _get_info(self):
        return {'info': "There is currently no info"}

    def reset(self, seed=None, options=None, sim_steps=None):
        super().reset(seed=seed)
        self.simulation_cur_step = 0
        if sim_steps is not None:
            self.simulation_steps = sim_steps
        if not self.isFirstReset:
            traci.close()
            self.startTraci()
        else:
            self.isFirstReset = False
        observation = self._get_obs()
        info = None

        return observation, info

    def skip_steps(self, steps):
        for _ in range(steps):
            traci.simulationStep()

    def step(self, actions: Optional[np.ndarray]) -> Tuple[ObsType, List[float], bool, bool, dict]:
        self.simulation_cur_step += 1
        actions_is_not_none = actions is not None

        tls_action_penalty = []
        if actions_is_not_none:
            for idx, action in enumerate(actions):
                tls = self.node_to_tls[idx]
                if action >= self.tls_to_action_cnt[tls]:
                    tls_action_penalty.append(tls)
                    continue
                cur_phase = traci.trafficlight.getRedYellowGreenState(tls)
                next_phase = self.tls_to_phases[tls][action].state
                if cur_phase == next_phase:
                    continue
                cur_phase = cur_phase.replace('G', 'y').replace('g', 'y')
                traci.trafficlight.setRedYellowGreenState(
                    tls,
                    cur_phase
                )
        self.skip_steps(self.simulation_yellow_steps)
        if actions_is_not_none:
            for idx, action in enumerate(actions):
                tls = self.node_to_tls[idx]
                if action >= self.tls_to_action_cnt[tls]:
                    tls_action_penalty.append(tls)
                    continue
                next_phase = self.tls_to_phases[tls][action].state
                traci.trafficlight.setRedYellowGreenState(
                    tls,
                    next_phase
                )
        self.skip_steps(self.simulation_step_size)

        terminated = self.simulation_cur_step >= self.simulation_steps

        # required for reward and Obs
        self.fillLastStepHaltingNumber()
        reward = self.reward(tls_action_penalty)
        observation = self._get_obs()

        truncated = False
        info = None

        return observation, reward, terminated, truncated, info

    def reward(self, tls_action_penalty):
        queue_length = [0.] * len(self.tls_to_lanes.keys())
        for idx, (tls, lanes) in enumerate(self.tls_to_lanes.items()):
            for lane in lanes:
                queue_length[idx] -= self.lane_last_step_halting_number[lane]
            if tls in tls_action_penalty:
                queue_length[idx] *= 2
        return queue_length

    def fillLastStepHaltingNumber(self):
        for tls, lanes in self.tls_to_lanes.items():
            for lane in lanes:
                self.lane_last_step_halting_number[lane] = traci.lane.getLastStepHaltingNumber(lane)
