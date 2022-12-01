from mini_behavior.actions import *

DEFAULT_ACTIONS = []

ACTION_FUNC_MAPPING = {
    'pickup': Pickup,
    'drop': Drop,
    'drop_in': DropIn,
    'toggle': Toggle,
    'open': Open,
    'close': Close,
    'slice': Slice,
    'cook': Cook,
    'goto': GoTo,
}

CONTROLS = ['left', 'right', 'forward']  # 'down'
