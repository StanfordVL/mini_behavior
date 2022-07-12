# Mini-BEHAVIOR
###  MiniGrid Implementation of BEHAVIOR Tasks

### Environment Setup
* Follow setup instructions from: https://github.com/Farama-Foundation/gym-minigrid.
* Downgrade gym to version 0.21.0: pip install gym==0.21.0

### 
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
│   ├── bddl_utils.py (new)
│   ├── global_variables.py (new)
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
