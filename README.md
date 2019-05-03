# ASim : An Discrete Event Simulator of Algorand

## Installation
Run this command to install the dependencies and setup a virtual environment
```
./install.sh
```

This should create a virtual environment and add alias command in bashrc file to activate this environment. To activate the virtual environment run following command
```
algorand_env
```

## Running the simulation
Run following commands to run the simulation

```
python main.py --node 256 --blocks 64
```

### Arguments

 --node : Number of nodes
 
 --blocks : Number of blocks until simulation should run

## Creating hash of code files
This command was used to generate the sha256 hash of the code files. Note that only `.py` files are used to generate the hash.
```
sha256sum *.py | sha256sum
```