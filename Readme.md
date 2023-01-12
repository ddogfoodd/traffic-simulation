# Traffic Simulation Repository of AILab
This is the traffic-simulation repository of the OvGU AILab.  
It contains a collection of tools and documentation regarding traffic simulation using the [Eclipse SUMO (Simulation of Urban MObility) framework](https://github.com/eclipse/sumo).

### Purpose:
This repo collects tools/scripts/documentation used in our research. It mainly contains Python ↔︎ SUMO interactions on a higher level than regular SUMO interfaces like [TraCI](https://sumo.dlr.de/docs/TraCI.html).
  
### Install and setup SUMO:
To install and test SUMO refer to our [installation/setup doc](https://code.ovgu.de/ai-lab/projects/pascal/traffic-simulation/-/blob/main/docs/sumo/installation_setup.md).

### Tools:
- `createsimulation.py` - create SUMO files for a grid world ([Link to file](https://code.ovgu.de/ai-lab/projects/pascal/traffic-simulation/-/blob/main/sumobasesimulation/createsimulation.py))
- `verify.py` - verify that SUMO installation works ([Link to file](https://code.ovgu.de/ai-lab/projects/pascal/traffic-simulation/-/blob/main/sumobasesimulation/verify.py))
- `get_safe_phases.py` - calculate set of connections that can share the same green phase without leading to collisions ([More Info](https://code.ovgu.de/ai-lab/projects/pascal/traffic-simulation/-/blob/main/docs/tools/get_safe_phases.md), [Link to file](https://code.ovgu.de/ai-lab/projects/pascal/traffic-simulation/-/blob/main/tools/get_safe_phases.py))

### Docs:
- [OSM Web Wizard for SUMO tutorial](https://code.ovgu.de/ai-lab/projects/pascal/traffic-simulation/-/blob/main/docs/sumo/osmWebWizard.md) - Tutorial on how to use OSMWebWizard to convert OpenStreetMaps into SUMO files

### Contributing:
Feel free to contribute to this repo by adding more tools or docs or even fix bugs or expand functionality in existing tools.  
Please create a new branch and work on there. When finished, create a merge request.  
If you don't want to code, we also appreciate contributions in the form of ideas or feature requests. Just create an issue.
