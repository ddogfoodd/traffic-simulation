# SUMO Installation/Setup Document
### Basic installation, simple verification to test sample working code.


#### Installation instructions
Installation of SUMO is different for different platforms (Windows, macOS and Linux). It is pretty straight forward, click the SUMO logo below for detailed instructions.  _Note : Update your operating system before installing SUMO to ensure all dependencies are fulfilled._
[![](https://fileinfo.com/img/icons/files/128/sumocfg-11490.png)](https://sumo.dlr.de/docs/Installing/index.html)

#### File Structure

Folder : sumobasesimulation

| File | Purpose |
| ------ | ------ |
| createsimulation.py | To create a simple grid network simulation with vehicles |
| verify.py | Verification script to make sure SUMO is in  |

Folder : xml/scenarioxx

| File | Purpose |
| ------ | ------ |
| grid.net.xml | Network File |
| grid.rou.xml | Vehicle Route File  |
| grid.sumocfg | Main config file which SUMO will use to run the simulation  |
| route.xml | Route flow definitions  |
| grid.rou.xml | Vehicle Route File  |

#### Basic Setup

For creating a simple grid network run : 
```sh
python createsimulation.py
```

You can modify the size of the grid , number of vehicles and number of lanes before running the above script.
Once you run this script the configuration files , route files and network files are all created. 

#### Verification of Working Version

To check if the installed SUMO works along with the created simulation run : 
```sh
python verify.py
```
In the above script you can change the following parameter to run it either in GUI mode or command-line mode.
> --sumo_cmd_env  , values = [sumo,sumo-gui]
