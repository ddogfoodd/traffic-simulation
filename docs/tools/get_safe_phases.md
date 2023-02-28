# get_safe_phases.py

## Requirement versions:
Note that the following are the versions that I developed this script with. It might work with different versions.

- Python version 3.9.1
- beautifulsoup4==4.11.1
- numpy==1.23.4

## What it does:
`get_safe_phases()` is a Python function that returns to find all combinations of connections in a junction that can share green signals without leading to collisions.  
To do so, it uses the XML file of a SUMO net and mainly reads and intersects the lists of foes. Foes of a connection are other connections that could lead to collisions if they share green phases.

## Why it does it:
The `get_safe_phases()` function returns the pool of possible safe green phase combinations. The next big goal would be to choose some combinations out of the pool so that the traffic can be optimized, i.e. calculate not only safe but also efficient phases.

## Usage:
**Parameters & Returns:**
| Parameters   | Position | Type | Description                                                                      | Example                         |
| ------------ | ------- | ---- | -------------------------------------------------------------------------------- | ------------------------------- |
| `net_xml_path` | 1       | `str`  | Path to the SUMO net XML file in which the junction can be found                 | `"/Users/jost/magdeburg_net.xml"` |
| `junction_id`  | 2       | `str`  | ID of the junction for which to calculate, usually found in net XML file or SUMO | `"junction001"`                  |
  

| Returns             | Position | Type   | Description                                                                                                                                                                                                                                                                              | Example |
| ------------------- | -------- | ------ | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | ------- |
| `n_tls`             | 1        | `int`  | Number of connections in the junction (by default this is also the number of tls in the junction in SUMO), these are the inward & outward pairs                                                                                                                                          | `14`    |
| `total_safe_phases` | 2        | `list` | All safe phase combinations of the given junction. Given as list of lists containing ints. The outer list contains all the safe combinations of phases whereas, the inner lists correspond to the combinations itself and contain the ints which resemble the indices of the connections. | `[[1], [2], [3], [4] [1, 3], [1, 4], [2, 4], [1, 3, 4]]`        |

**Usage for single junctions:**  
If you want to get all safe phases for just a single junction in a SUMO net, just import and call the function `get_safe_phases()` of the `get_safe_phases.py` file in the `tools` directory of the repo.  

The function call could look like this:  
```python
num_cons, safe_combs = get_safe_phases("/path/to/net.xml", "junction001")
```
  
**Usage for many junctions:**
If you want to get all safe phases for many junctions (e.g. all tls controlled junctions in a net) you probably want to modify the `get_safe_phases.py` script slightly.  
I haven't tested how much of a slowdown this actually is, but you probably don't want to read and parse the net XML file in each function call.  

Instead, I recommend doing the following:  
Modify the script as follows, move the read and parse part out of the function and store the net_xml in a variable that can be passed to or is accessible by the function.  
Then list all junction IDs for which you want to calculate the safe phases and iterate over the list and call the funtion for each junction ID. The function itself should be pretty fast, although it most likely can be further optimized.  
  
If you want to call the function for each tls controlled junction in a net I recommend you list all tls controlled junctions IDs using a regex on the XML file.  
The code could look like this:  
```python
import re
# read net xml
with open("/path/to/net.xml", "r") as f:
        net_data = f.read()

# find all junctions controlled by a tls
    junction_list = re.findall(pattern="junction id=.* type=\"traffic_light\"", string=net_data)
    # extract junction ID from regex matches
    junction_list = [regex_match.split("\"")[1] for regex_match in junction_list]
```
