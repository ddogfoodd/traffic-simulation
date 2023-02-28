from bs4 import BeautifulSoup
import numpy as np
import itertools
import warnings

def get_safe_phases(net_xml_path: str, junction_id: str):
    """For a given traffic-light-controlled junction return all connection combinations that can receive a green signal at the same time without leading to collisions.

    :param net_xml_path: Path to SUMO net xml file
    :type net_xml_path: str
    :param junction_id: SUMO junction ID
    :type junction_id: str
    :return: Two values: the number of connections in the junction & List of all safe phase combinations as list of lists where each inner list is a combination of connections that can share green signals without colliding
    :rtype: int, list
    """
    
    # read and parse SUMO net xml file
    with open(net_xml_path, "r") as f:
        net_data = f.read()
    net_xml = BeautifulSoup(net_data, "xml")

    # whole junction including lanes etc
    junction_data = net_xml.find('junction', {'id': junction_id})
    
    #! throw warning if junction type is not traffic_light i.e. it is not controlled by tls
    junction_type = junction_data.attrs['type']
    if junction_type != 'traffic_light':
        warnings.warn(f"Junction with ID: {junction_id} is not of type 'traffic_light'. Instead it is of type: '{junction_type}'. This means that the junction is not controlled by a tls.")
        
    # just request data including foes, cont, index, response
    request_data = junction_data.find_all('request')
    # just foes
    foes = [request.attrs['foes'] for request in request_data]
    # foes as np array
    foes = np.ma.array([list(map(int, foe)) for foe in foes], mask=False)
    
    # number of tls / tls controlled connections
    n_tls = foes.shape[0]
    
    #! flip foes to be more intuitive, without flipping columns would be reversed i.e. last value in each row would correspond to index 0
    foes = np.fliplr(foes)
    
    # mask values corresponding to whether a connection has itself as foe or not
    # we want to ignore those for further computations
    for i in range(n_tls):
        foes.mask[i][i] = True
    
    # non-foes as a non sparse non binary list of foe indices
    # practically list of connection indices that don't collide i.e. that can share a green phase
    non_foes_ind = [np.where(foes[i] == 0)[0] for i in range(n_tls)]
    
    # placeholder to collect all safe_phases (safe phase combinations) during computation
    total_safe_phases = [[i] for i in range(n_tls)]
    
    # for each tls / tls controlled connection list all others that are no foes of each other
    # this combines all safe connection combinations which are directly readable from the foe matrix and which don't need further computation
    safe_phases = []
    for i in range(n_tls):
        # pairs of 2: extract from foes
        for i2 in non_foes_ind[i]:
            #* condition to not take duplicates e.g. [0, 1] and [1, 0]
            if i2 > i:
                safe_phases.append([i, i2])
            else:
                continue
    
    # add safe phases to collection
    total_safe_phases += safe_phases
    
    # placeholder for computation of next level non-foes
    curr_non_foes = []
    
    # for each safe_phase that was combined in the first step -> get the safe connections of the given safe_phase and intersect those safe connections with the possible safe connections of an connection added to the safe phase
    # the resulting safe phases contain more connections that can go green in parallel but also leads to less further possibilities to add to that combination
    for safe_phase in safe_phases:
        # start with first connection of a safe phase
        wip_non_foes = non_foes_ind[safe_phase[0]]
        # for each other connection of a safe phase get the step-wise intersection
        for connection in safe_phase[1:]:
            wip_non_foes = np.intersect1d(wip_non_foes, non_foes_ind[connection])
        curr_non_foes.append(wip_non_foes)
        
    # check if non foes exist
    # this is used as end condition for the loop
    non_foes_exist = False
    for non_foe in curr_non_foes:
        if non_foe.any():
            non_foes_exist = True
            break
    
    # iteratively look for safe_phases and further non_foes
    # stop when there are no further connection combinations having no_foe options to add
    while non_foes_exist: 
        # get new safe_phases
        #! duplicates allowed, filter befor appending
        dupl_safe_phases = []
        for i in range(len(safe_phases)):
            for connection in curr_non_foes[i]:
                dupl_safe_phases.append(safe_phases[i].copy() + [connection])
        # filter duplicates
        for safe_phase in dupl_safe_phases:
            safe_phase.sort()
        dupl_safe_phases.sort()
        # these are the newly computed safe phase combinations
        new_safe_phases = list(k for k,_ in itertools.groupby(dupl_safe_phases))
    
        # get new indices of non_foes for the newly computed safe phase combinations
        # so to speak: for each safe combinations a list of connection indices that could further be added to a given combination
        new_non_foes = []
        for i in range(len(new_safe_phases)):
            wip_non_foes = non_foes_ind[new_safe_phases[i][0]]
            for connection in new_safe_phases[i][1:]:
                wip_non_foes = np.intersect1d(wip_non_foes, non_foes_ind[connection])
            new_non_foes.append(wip_non_foes)
        
        # add safe phases to collection
        total_safe_phases += new_safe_phases
        
        # overwrite old values for next iteration
        curr_non_foes = new_non_foes.copy()
        # check if further non foes exist and set ending condition accordingly
        non_foes_exist = False
        for non_foe in curr_non_foes:
            if non_foe.any():
                non_foes_exist = True
                break
                
        safe_phases = new_safe_phases.copy()
        
    # return number of connections or number of tls
    # return collection of all connection combinations that can share a green phase and would not lead to collisions
    # list of lists where each inner list contains indices of connections
    return n_tls, total_safe_phases
