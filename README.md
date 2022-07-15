# Mini-BEHAVIOR
###  MiniGrid Implementation of BEHAVIOR Tasks

### Environment Setup
* Follow setup instructions from: https://github.com/Farama-Foundation/gym-minigrid.
* Downgrade gym to version 0.21.0: pip install gym==0.21.0

### Run Code 
To run in interactive mode: ./manual_control.py --env MiniGrid-ThrowLeftoversMulti-16x16-N2-v

### Directory 
```.
├── gym_minigrid
│   ├── envs
│   │   ├── __init__.py
│   │   ├── throwleftovers.py (new)
│   │   └── throwleftovers_multiroom.py (new)
│   ├── __init__.py
│   ├── actions.py (new)
│   ├── bddl.py (new)
│   ├── globals.py (new)
│   ├── mappings.py (new)
│   ├── minigrid.py (modified)
│   ├── objects.py (new)
│   ├── register.py 
│   ├── rendering.py
│   ├── roomgrid.py
│   ├── states.py (new)
│   ├── states_base.py (new)
│   ├── utils.py (new)
│   ├── window.py
│   └── wrappers.py
├── __init__.py
├── benchmark.py
├── gen_behavior.py (new)
├── manual_control.py
├── run_tests.py
├── setup.py
├── test_interactive_mode.py
└── test_throwingleftovers.py (new)
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
