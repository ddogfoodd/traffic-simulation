# Traffic Simulation Repository of AILab
This is the traffic-simulation repository of the OvGU AILab.  
It contains a collection of tools and documentation regarding traffic simulation using the [Eclipse SUMO (Simulation of Urban MObility) framework](https://github.com/eclipse/sumo).

### Purpose:
This repo collects tools/scripts/documentation used in our research. It mainly contains Python ↔︎ SUMO interactions on a higher level than regular SUMO interfaces like [TraCI](https://sumo.dlr.de/docs/TraCI.html).
  
### Install and setup SUMO:
To install and test SUMO refer to our [installation/setup doc](https://code.ovgu.de/ai-lab/projects/pascal/traffic-simulation/-/blob/main/docs/sumo/installation_setup.md).

### Tools:
- `createsimulation.py` - create SUMO files for a grid world
- `verify.py` - verify that SUMO installation works
- `get_safe_phases.py` - calculate set of connections that can share the same green phase without leading to collisions ([More Info](https://code.ovgu.de/ai-lab/projects/pascal/traffic-simulation/-/blob/main/docs/tools/get_safe_phases.md))

### Docs:
- [OSM Web Wizard for SUMO tutorial](https://code.ovgu.de/ai-lab/projects/pascal/traffic-simulation/-/blob/main/docs/sumo/osmWebWizard.md) - Tutorial on how to use OSMWebWizard to convert OpenStreetMaps into SUMO files
