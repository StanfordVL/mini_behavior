from mini_behavior.actions import *

ALL_ACTIONS = ['pickup', 'drop', 'drop_in', 'drop_on', 'drop_under', 'toggle', 'open', 'close', 'slice', 'cook']
DEFAULT_ACTIONS = []

ACTION_FUNC_MAPPING = {
    'pickup': Pickup,
    'drop': Drop,
    'drop_in': DropIn,
    'toggle': Toggle,
    'open': Open,
    'close': Close,
    'slice': Slice,
    'cook': Cook
}

CONTROLS = ['left', 'right', 'forward']  # 'down'

