from .actions import *
from .states import *

global _ALL_ACTIONS
global _DEFAULT_ACTIONS
global _ALL_STATES
global _DEFAULT_STATES
global _STATE_FUNC_MAPPING
global _ABILITY_TO_STATE_MAPPING
global _ACTION_FUNC_MAPPING


_ALL_STATES = ['onfloor', 'ontop', 'under', 'inside', 'nextto', 'infrontofagent', 'agentcarrying'], #  'inroom'
_DEFAULT_STATES = ['onfloor', 'ontop', 'under', 'nextto', 'inside', 'infrontofagent']  # , 'inroom']

# TODO: add door states -- 'open', 'locked'

_STATE_FUNC_MAPPING = {
    'onfloor': Onfloor,
    'ontop': Ontop,
    'under': Under,
    'inside': Inside,
    'nextto': NextTo,
    'infrontofagent': InFrontOfAgent,
    'agentcarrying': AgentCarrying
    # 'inroom': Inroom,
}

# ability (function) to state (function) mapping
_ABILITY_TO_STATE_MAPPING = {}

_ALL_ACTIONS = ['pickup', 'drop']
_DEFAULT_ACTIONS = []

_ACTION_FUNC_MAPPING = {
    'pickup': Pickup,
    'drop': Drop,
}

_CONTROLS = ['left', 'right', 'up'] # 'down'

########################################################################################################################

# FROM BDDL

# _ALL_STATES = frozenset(
#     [
#         # AABB,
#         Burnt,
#         CleaningTool,
#         ContactBodies,
#         Cooked,
#         Dusty,
#         # Frozen,
#         HeatSourceOrSink,
#         HorizontalAdjacency,
#         InFOVOfRobot,
#         InHandOfRobot,
#         InReachOfRobot,
#         InSameRoomAsRobot,
#         Inside,
#         InsideRoomTypes,
#         MaxTemperature,
#         NextTo,
#         ObjectsInFOVOfRobot,
#         OnFloor,
#         OnTop,
#         Open,
#         Pose,
#         Sliced,
#         Slicer,
#         Soaked,
#         Stained,
#         Temperature,
#         ToggledOn,
#         Touching,
#         Under,
#         VerticalAdjacency,
#         WaterSource,
#     ]
# )
#
#
# _ABILITY_TO_STATE_MAPPING = {
#     "burnable": [Burnt],
#     "cleaningTool": [CleaningTool],
#     "coldSource": [HeatSourceOrSink],
#     "cookable": [Cooked],
#     "dustyable": [Dusty],
#     "freezable": [Frozen],
#     "heatSource": [HeatSourceOrSink],
#     "openable": [Open],
#     "robot": [ObjectsInFOVOfRobot],
#     "sliceable": [Sliced],
#     "slicer": [Slicer],
#     "soakable": [Soaked],
#     "stainable": [Stained],
#     "toggleable": [ToggledOn],
#     "waterSource": [WaterSource],
# }
#
# _DEFAULT_STATE_SET = frozenset(
#     [
#         InFOVOfRobot,
#         InHandOfRobot,
#         InReachOfRobot,
#         InSameRoomAsRobot,
#         Inside,
#         NextTo,
#         OnFloor,
#         OnTop,
#         Touching,
#         Under,
#     ]
# )

# TEXTURE_CHANGE_PRIORITY = {
#     Frozen: 4,
#     Burnt: seed 10_3,
#     Cooked: seed 0_2,
#     Soaked: seed 0_2,
#     ToggledOn: 0,
# }