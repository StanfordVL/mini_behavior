# Mini-BEHAVIOR
###  MiniGrid Implementation of BEHAVIOR Tasks

### Environment Setup
* Follow setup instructions from: https://github.com/Farama-Foundation/gym-minigrid.
* Downgrade gym to version 0.21.0: pip install gym==0.21.0

### Run Code 
To run in interactive mode: ./manual_control.py

### Directory 
```angular2html
├── __init__.py 
├── benchmark.py
├── collect_demos.py (new)
├── convert_scenes.py (new)
├── evaluate.py
├── gym_minigrid
│   ├── __init__.py 
│   ├── actions.py (new)
│   ├── agent.py (new)
│   ├── bddl.py (new)
│   ├── envs
│   │   ├── __init__.py
│   │   ├── floorplan.py (new)
│   │   ├── navigation.py (new)
│   │   └── throwleftovers.py (new)
│   ├── globals.py (new)
│   ├── grids (new)
│   ├── minigrid.py (modified)
│   ├── objects.py (new)
│   ├── register.py
│   ├── rendering.py 
│   ├── roomgrid.py
│   ├── scene_to_grid.py (new)
│   ├── scenes (new)
│   ├── states.py (new)
│   ├── states_base.py (new)
│   ├── window.py
│   └── wrappers.py
├── manual_control.py
├── model.py
├── run_tests.py
├── setup.py
├── train.py
├── train_nav.py
├── utils
│   ├── __init__.py
│   ├── agent.py
│   ├── env.py
│   ├── format.py
│   ├── other.py
│   └── storage.py
└── visualize.py
``` 

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
