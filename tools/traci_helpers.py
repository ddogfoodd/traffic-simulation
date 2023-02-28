"""
Helper functions building on TraCI
"""

# import traci
import os, sys
if sys.platform.startswith("darwin"):
    #! default MacOS path of sumo tools
    sys.path.append(os.path.join("/usr", "local", "opt", "sumo", "share", "sumo", "tools"))
import traci
import numpy as np
import inspect

"""
GET LANE INSIGHTS
---
Collection of functions that give insight about lanes.
"""
def get_lane_density(laneID):
    """Calculate the density of a given lane, 
    i.e. number of vehicles in relation to the lane length.

    Parameters
    ----------
    laneID : str
        ID of the SUMO lane for which to calculate the density.
        
    Returns
    -------
    float
        Lane density.
    """
    num = traci.lane.getLastStepVehicleNumber(laneID)
    density = num / traci.lane.getLength(laneID)
    return density

def get_state(tlsID):
    """For a given tls return the average lane density for each 
    controlled lane, 
    i.e. number of vehicles in relation to the lane length.

    Parameters
    ----------
    tlsID : str
        ID of the SUMO traffic light system for which lanes to calculate the densities.
        
    Returns
    -------
    list
        List of lane densities.
    """
    # copy of another function for simple use
    def get_lane_density(laneID):
        num = traci.lane.getLastStepVehicleNumber(laneID)
        density = num / traci.lane.getLength(laneID)
        return density
    
    controlled_lanes = traci.trafficlight.getControlledLanes(tlsID)
    all_lanes_density = dict()
    lane_state = []
    for lane in controlled_lanes:
        lane_key = lane.split('_')[0]
        lane_density = get_lane_density(lane)
        if lane not in all_lanes_density.keys():
            all_lanes_density[lane_key] = [lane_density]
        else:
            all_lanes_density[lane_key].append(lane_density)

    for key in all_lanes_density.keys():
        avg_lane_density = np.average(all_lanes_density[key])
        lane_state.append(avg_lane_density)
    return lane_state

# for each given lane, get number of vehicles in those lanes
def get_vehicle_numbers(lanes):
    """For each given lane return the number of vehicles in those lanes.

    Parameters
    ----------
    lanes : list
        IDs of the SUMO lanes for which to count the number of vehicles.
        
    Returns
    -------
    dict
        Dictionary where lanes are the keys and number of vehicles on those lanes are the values.
    """
    vehicle_per_lane = dict()
    for l in lanes:
        vehicle_per_lane[l] = 0
        for k in traci.lane.getLastStepVehicleIDs(l):
            if traci.vehicle.getLanePosition(k) > 10:
                vehicle_per_lane[l] += 1
    return vehicle_per_lane

# get the total waiting time for a list of lanes
def get_waiting_time(lanes):
    waiting_time = 0
    for lane in lanes:
        all_vehicles = traci.lane.getLastStepVehicleIDs(lane)
        for vehID in all_vehicles:
            waiting_time += traci.vehicle.getWaitingTime(vehID)
    return waiting_time

# sum the queue lengths of all lanes controlles by given tls
def getqueuelen(junction):
    qlen = 0
    controlledlanes = traci.trafficlight.getControlledLanes(junction)
    for lane in controlledlanes:
        qlen += traci.lane.getLastStepVehicleNumber(lane)
    return qlen


"""
GET Traffic Light Insights
---
Collection of functions that give insight about traffic lights.
"""
# for a given tls return all phase states
def get_state_definition(tlsID):
    phases = [phase.__dict__['state'] for phase in traci.trafficlight.getAllProgramLogics(tlsID)[0].__dict__['phases']]
    return (phases)

# apply get_state_definition to a list of tlsIDs
def get_all_state_definition(traffic_lights):
    # copy of another function for simple use
    def get_state_definition(tlsID):
        phases = [phase.__dict__['state'] for phase in traci.trafficlight.getAllProgramLogics(tlsID)[0].__dict__['phases']]
        return (phases)
    all_state_definition = []
    for tlsID in traffic_lights:
        all_state_definition.append(get_state_definition(tlsID))
    return all_state_definition


"""
MODIFY Traffic Lights
---
Collection of functions that modify traffic lights.
"""
# set the phase of a given tls to a given phase for a given duration
def phaseDuration(junction, phase_time, phase_state):
    traci.trafficlight.setRedYellowGreenState(junction, phase_state)
    traci.trafficlight.setPhaseDuration(junction, phase_time)


"""
GET Vehicle Insights
---
Collection of functions that give insight about vehicles.
"""
# return the mean emmision values for a list of vehicles
def get_emissions(vehicles):
    nox = []
    pmx = []
    co2 = []
    co = []
    hc = []
    for vehicle in vehicles:
        nox.append(traci.vehicle.getNOxEmission(vehicle))
        pmx.append(traci.vehicle.getPMxEmission(vehicle))
        co2.append(traci.vehicle.getCO2Emission(vehicle))
        co.append(traci.vehicle.getCOEmission(vehicle))
        hc.append(traci.vehicle.getHCEmission(vehicle))
    return np.mean(nox),np.mean(pmx),np.mean(co2),np.mean(co),np.mean(hc)
    
# sum the waiting times of all vehicles in a given list
def getnetworkwaitingtime(vehicles):
    waiting_time = 0
    for vehID in vehicles:
        waiting_time += traci.vehicle.getWaitingTime(vehID)
    return waiting_time/len(vehicles)

