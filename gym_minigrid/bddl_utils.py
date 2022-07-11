from .states import *
from .actions import *

_STATE_FUNC_MAPPING = {
    'onfloor': Onfloor,
    'agentcarrying': Agentcarrying,
    'ontop': Ontop,
    'inside': Inside,
    # 'inroom': Inroom,
    'contains': Contains,
    'overlap': Overlap,
    'seebehind': Seebehind,
}

# _ACTION_FUNC_MAPPING = {
#     'pickup': Pickup,
#     'drop': Drop
# }


def check_abs_state(env, obj, state):
    return state in obj.state_keys and obj.states[state].get_value(env)


def check_static_state(env, obj, state):
    return state in obj.state_keys and obj.states[state].get_value()


def check_rel_state(env, obj1, obj2, state):
    return state in obj1.state_keys and obj1.states[state].get_value(obj2, env)


def check_action(obj, action):
    return action in obj.action_keys and obj._ACTION_FUNC_MAPPING[action].can()

# obj._ACTION_FUNC_MAPPING[action].do() # perform action