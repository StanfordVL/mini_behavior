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
#     Burnt: 3,
#     Cooked: 2,
#     Soaked: 1,
#     ToggledOn: 0,
# }