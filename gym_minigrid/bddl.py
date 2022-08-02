from .actions import *
from .states import *

_ALL_STATES = ['atsamelocation',
               'cleaningTool',
               'coldSource',
               'cookable',
               'dustyable',
               'freezable',
               'heatSource',
               'infovofrobot',
               'inhandofrobot',
               'inreachofrobot',
               'insameroomasrobot',
               'inside',
               'nextto',
               'onfloor',
               'ontop',
               'openable',
               'sliceable',
               'slicer',
               'soakable',
               'stainable',
               'toggleable',
               'under'
               'waterSource'
               # 'touching', TODO: uncomment once implemented
               ]

# Touching
# ObjectsInFOVOfRobot,

_DEFAULT_STATES = ['atsamelocation',
                   'infovofrobot',
                   'inhandofrobot',
                   'inreachofrobot',
                   'insameroomasrobot',
                   'inside',
                   'nextto',
                   'onfloor',
                   'ontop',
                   'under'
                   # 'touching', TODO: uncomment once implemented
                   ]
#                ]

# state (str) to state (function) mapping
_STATE_FUNC_MAPPING = {
    'atsamelocation': AtSameLocation,
    'cleaningTool': CleaningTool,
    'coldSource': HeatSourceOrSink,
    'cookable': Cooked,
    'dustyable': Dusty,
    'freezable': Frozen,
    'heatSource': HeatSourceOrSink,
    'infovofrobot': InFOVOfRobot,
    'inhandofrobot': InHandOfRobot,
    'inreachofrobot': InReachOfRobot,
    'insameroomasrobot': InSameRoomAsRobot,
    'inside': Inside,
    'nextto': NextTo,
    'onfloor': OnFloor,
    'ontop': OnTop,
    'openable': Opened,
    'sliceable': Sliced,
    'slicer': Slicer,
    'soakable': Soaked,
    'stainable': Stained,
    'toggleable': ToggledOn,
    'under': Under,
    'waterSource': WaterSource
    # 'touching', TODO: uncomment once implemented
}

_ALL_ACTIONS = ['pickup', 'drop', 'toggle', 'open', 'close', 'slice', 'cook']
_DEFAULT_ACTIONS = []

_ACTION_FUNC_MAPPING = {
    'pickup': Pickup,
    'drop': Drop,
    'toggle': Toggle,
    'open': Open,
    'close': Close,
    # 'unlock': Unlock,
    'slice': Slice,
    'cook': Cook
}

_CONTROLS = ['left', 'right', 'forward']  # 'down'

########################################################################################################################

# FROM BDDL

# TEXTURE_CHANGE_PRIORITY = {
#     Frozen: 4,
#     Burnt: seed 10_3,
#     Cooked: seed 0_2,
#     Soaked: seed 0_2,
#     ToggledOn: 0,
# }
