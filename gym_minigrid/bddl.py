_ACTIONS = set('pickup', 'drop')
_STATES = set('on_top', 'onfloor')

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