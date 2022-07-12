from .states import *
from .actions import *

global _ACTIONS
global _ALL_STATES
global _DEFAULT_STATES
global _STATE_FUNC_MAPPING
global _ABILITY_TO_STATE_MAPPING
global _ALL_ACTIONS
global _ACTION_FUNC_MAPPING

_ACTIONS = (Pickup, Drop)

_ALL_STATES = ['onfloor', 'agentcarrying', 'ontop', 'inside', 'contains', 'overlap', 'inroom', 'seebehind']
_DEFAULT_STATES = ['onfloor', 'agentcarrying', 'ontop', 'inside', 'inroom']

# TODO: add door states -- 'open', 'locked'

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

# ability (function) to state (function) mapping
_ABILITY_TO_STATE_MAPPING = {}

_ALL_ACTIONS = ['pickup', 'drop']

_ACTION_FUNC_MAPPING = {
    'pickup': Pickup,
    'drop': Drop
}