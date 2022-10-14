## FROM MINIGRID REPO
import mini_behavior

# Import the envs module so that envs register themselves
import mini_behavior.mini_behavior.envs

# Import wrappers so it's accessible when installing with pip
import gym_minigrid.wrappers
