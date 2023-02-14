Module traci_helpers
====================
Helper functions building on TraCI

Functions
---------

    
`get_all_state_definition(traffic_lights)`
:   

    
`get_emissions(vehicles)`
:   

    
`get_lane_density(laneID)`
:   Calculate the density of a given lane, 
    i.e. number of vehicles in relation to the lane length.
    
    Parameters
    ----------
    laneID : str
        ID of the SUMO lane for which to calculate the density.
        
    Returns
    -------
    float
        Lane density.

    
`get_state(tlsID)`
:   For a given tls return the average lane density for each 
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

    
`get_state_definition(tlsID)`
:   

    
`get_vehicle_numbers(lanes)`
:   For each given lane return the number of vehicles in those lanes.
    
    Parameters
    ----------
    lanes : list
        IDs of the SUMO lanes for which to count the number of vehicles.
        
    Returns
    -------
    dict
        Dictionary where lanes are the keys and number of vehicles on those lanes are the values.

    
`get_waiting_time(lanes)`
:   

    
`getnetworkwaitingtime(vehicles)`
:   

    
`getqueuelen(junction)`
:   

    
`phaseDuration(junction, phase_time, phase_state)`
: