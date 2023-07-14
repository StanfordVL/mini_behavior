# Mini-BEHAVIOR
###  MiniGrid Implementation of BEHAVIOR Tasks

### Environment Setup
* Follow setup instructions from: https://github.com/Farama-Foundation/gym-minigrid.
   pip install gym-minigrid==1.0.3
* Install gym: pip install gym==0.21.0

### Run Code 
* To run in interactive mode: ./manual_control.py
* To train a sample RL agent, install stable-baseline3:
```commandline
pip install stable-baselines3==1.6.2
python train_rl_agent.py
```

### Action Space Type
Mini-BH supports two types of action spaces: cartesian and primitive. Environment names that ends with v0 correspond to 
primitive actions, while v1 corresponds to cartesian actions.

### File Descriptions 
* **gym_minigrid/actions.py**
    * Contains base class for actions 
    * All action classes defined here

* **gym_minigrid/bddl.py**
    * Contains all implemented states, actions, and mappings based on original BEHAVIOR BDDL Code

* **gym_minigrid/globals.py**
    *  Defines colors, mappings, etc, used for rendering the grid environment

* **gym_minigrid/minigrid.py**
    * Contains base class for mini grid environment
    * Modified to support multiple objects in a tile, generalizability to any actions / states / objects
    * Significant changes made to: grid.set, grid.remove, grid.render_tile, grid.render, minigrid.ste

* **gym_minigrid/objects.py**
    * Contains base class for GridWorld objects
    * All object classes defined here

* **gym_minigrid/states.py**
    * All states defined here, inherited from base classes in states_base.py

* **gym_minigrid/states_base.py**
    * Contains base classes for states (different classes for absolute and relative states)

### Floor plan to Mini-Behavior Environment
* add image file of floor plan to gym_minigrid/scenes directory
* run script to process floor plan and save grid to gym_minigrid/grids directory: `python convert_scenes.py --imgs IMG_FILENAMES`
* `floorplan.py` will register the floor plan of each `IMG_FILENAME` as an environment with:
    * `id='MiniGrid-IMG_FILENAME-0x0-N1-v0'`
    * `entry_point='gym_minigrid.envs:FloorPlanEnv'`
