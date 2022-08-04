from gym_minigrid.actions import *

ALL_ACTIONS = ['pickup', 'drop', 'drop_in', 'toggle', 'open', 'close', 'slice', 'cook']
DEFAULT_ACTIONS = []

ACTION_FUNC_MAPPING = {
    'pickup': Pickup,
    'drop': Drop,
    'drop_in': DropIn,
    'toggle': Toggle,
    'open': Open,
    'close': Close,
    # 'unlock': Unlock,
    'slice': Slice,
    'cook': Cook
}

CONTROLS = ['left', 'right', 'forward']  # 'down'

