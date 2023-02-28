# Getting started with SUMO

## Basic installation of SUMO + simple verification to test sample working code
### Installation instructions:
Installation of SUMO is different for different platforms (Windows, macOS and Linux). It is pretty straightforward, click the SUMO logo below for detailed instructions.  _Note : Update your operating system before installing SUMO to ensure all dependencies are fulfilled._
[![](https://fileinfo.com/img/icons/files/128/sumocfg-11490.png)](https://sumo.dlr.de/docs/Installing/index.html)  

### Installation instructions for OVGU IKS cluster remote machines
If you want to use SUMO on a remote machine of the OVGU IKS cluster, you might not have the permissions to follow SUMO's [Linux installation instructions](https://sumo.dlr.de/docs/Installing/index.html#linux).  
Instead, you can install SUMO using the Python package manager `pip` without root permissions.  

```sh
python3 -m pip install sumo
```

If further SUMO libraries are required, they can also be installed via `pip`.
See examples for `traci` and `libsumo` below.
```sh
python3 -m pip install traci
```
```sh
python3 -m pip install libsumo
```

### (Optional) Test and verify SUMO
To test if installed SUMO is working as intended, you can run the scripts in the [`sumobasesimulation` directory](https://code.ovgu.de/ai-lab/projects/pascal/traffic-simulation/-/tree/main/sumobasesimulation).  
  
For creating a simple grid network, run : 
```sh
python createsimulation.py
```

You can modify the size of the grid, number of vehicles and number of lanes before running the above script.
Once you run this script the configuration files , route files and network files are all created. 

To check if the installed SUMO works along with the created simulation run : 
```sh
python verify.py
```
In the above script, you can change the following parameter to run it either in GUI mode or command-line mode.
> --sumo_cmd_env  , values = [sumo,sumo-gui]

## SUMO file structure
The most important files in a SUMO simulation are the following.
See [`xml` directory](https://code.ovgu.de/ai-lab/projects/pascal/traffic-simulation/-/tree/main/xml) for examples.

| File | Purpose |
| ------ | ------ |
| grid.net.xml | Network File |
| grid.rou.xml | Vehicle Route File  |
| grid.sumocfg | Main config file which SUMO will use to run the simulation  |
| route.xml | Route flow definitions  |
