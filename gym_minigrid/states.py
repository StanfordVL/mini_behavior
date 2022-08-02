from .states_base import *
import numpy as np


def get_obj_cell(self, env):
    obj = self.obj
    cell = env.grid.get(*obj.cur_pos)
    return obj, cell


###########################################################################################################
# ROBOT RELATED STATES

# TODO: CHANGE THIS
class InFOVOfRobot(AbsoluteObjectState):
    # return true if obj is in front of agent
    def _get_value(self, env):
        # agent_front = env.agent.front_pos
        # obj_pos = self.obj.cur_pos
        #
        # return np.all(agent_front == obj_pos)
        return env.agent.in_view(*self.obj.cur_pos)


class InHandOfRobot(AbsoluteObjectState):
    # return true if agent is carrying the object
    def _get_value(self, env):
        return np.all(self.obj.cur_pos == np.array([-1, -1]))


class InReachOfRobot(AbsoluteObjectState):
    # return true if obj is reachable by agent
    def _get_value(self, env):
        carrying = env.agent.is_carrying(self.obj)
        in_front = np.all(self.obj.cur_pos == env.agent.front_pos)
        return carrying or in_front


# TODO: check that this works
class InSameRoomAsRobot(AbsoluteObjectState):
    # return true if agent is in same room as the object
    def _get_value(self, env):
        if self.obj.check_abs_state(env, 'inhandofrobot'):
            return True

        obj_room = env.room_from_pos(*self.obj.cur_pos)
        agent_room = env.room_from_pos(*env.agent.cur_pos)
        return np.all(obj_room == agent_room)


###########################################################################################################
# ABSOLUTE OBJECT STATES


# # NOTE: not implementing for now
# class Burnt(AbsoluteObjectState):
#     def _get_value(self, env):


# TODO: check this works
class Cooked(AbsoluteObjectState):
    """
    Cooked(obj) only changes when Cook action is done on the obj
    """
    def __init__(self, obj):
        super(Cooked, self).__init__(obj)


# TODO: check this works
class Dusty(AbsoluteObjectState):
    def __init__(self, obj):
        """
        Always init True
        """
        super(Dusty, self).__init__(obj)
        self.value = True
        self.tools = ["broom", "rag", "scrub_brush", "towel"]

    def _update(self, env):
        """
        Always init True
        False if at any point, obj and cleaningTool are in the same location
        """
        # for tool_type in env.state_objs['cleaningTool']:
        for tool_type in self.tools:
            for tool in env.objs.get(tool_type, []):
                if self.obj.states['atsamelocation'].get_value(tool, env):
                    self.value = False


# TODO: check this works
class Frozen(AbsoluteObjectState):
    def __init__(self, obj):
        super(Frozen, self).__init__(obj)
        self.tools = ["electric_refrigerator"]

    def _get_value(self, env):
        """
        True: coldSource is toggled on AND obj, cold source are at same location
        False: coldsource is toggled off OR obj, cold source are not at same location

        NOTE: refrigerator isnt togglebale
        """
        self.value = False

        for tool_type in self.tools:
            for cold_source in env.objs.get(tool_type, []):
                # if cold_source.ToggledOn.get_value(env):
                if self.obj.states['atsamelocation'].get_value(cold_source, env):
                    self.value = True

        return self.value


# TODO: check this works
class Opened(AbsoluteObjectState):
    def __init__(self, obj):
        """
        Value changes only when Open action is done on obj
        """
        super(Opened, self).__init__(obj)


# TODO: check this works
class Sliced(AbsoluteObjectState):
    def _set_value(self, new_value=True):
        self.value = True


# TODO: check this works
class Soaked(AbsoluteObjectState):
    def __init__(self, obj):
        super(Soaked, self).__init__(obj)
        self.tools = ['sink']

    def _update(self, env):
        """
        not reversible
        True if at any point, the obj is at the same location as a water source that is toggled on
        """
        for tool_type in self.tools:
            for water_source in env.objs.get(tool_type, []):
                if water_source.ToggledOn.get_value(env):
                    if self.obj.states['atsamelocation'].get_value(water_source, env):
                        self.value = True


# TODO: check this works
class Stained(AbsoluteObjectState):
    def __init__(self, obj):
        """
        Always init True
        """
        super(Stained, self).__init__(obj)
        self.value = True
        self.tools = ['rag', 'scrub_brush', 'towel']

    def _update(self, env):
        """
        not reversible
        False if at any point, the obj is at the same location as a soaked cleaning tool
        """
        for tool_type in self.tools:
            for cleaning_tool in env.objs.get(tool_type, []):
                if cleaning_tool.Soaked.get_value(env):
                    if self.obj.states['atsamelocation'].get_value(cleaning_tool, env):
                        self.value = True


# TODO: check this works
class ToggledOn(AbsoluteObjectState):
    def __init__(self, obj): # env
        super(ToggledOn, self).__init__(obj)


###########################################################################################################
# RELATIVE OBJECT STATES


# TODO: check this works
class AtSameLocation(RelativeObjectState):
    # returns true if obj is at the same location as other
    def _update(self, other, env):
        self.value = np.all(self.obj.cur_pos == other.cur_pos)


class Inside(RelativeObjectState):
    def _update(self, other, env):
        same_location = np.all(self.obj.cur_pos == other.cur_pos)

        if same_location:
            if 'openable' not in other.state_keys:
                self.value = True
            elif other.Open.get_value(env):
                self.value = True
        else:
            self.value = False


class NextTo(RelativeObjectState):
    # return true if objs are next to each other
    def _get_value(self, other, env):
        pos_1 = self.obj.cur_pos
        pos_2 = other.cur_pos

        # above, below
        if pos_1[0] == pos_2[0] and abs(pos_1[1] - pos_2[1]) == 1:
            return True
        # left, right
        elif pos_1[1] == pos_2[1] and abs(pos_1[0] - pos_2[0]) == 1:
            return True
        else:
            return False


class OnFloor(AbsoluteObjectState):
    def _update(self, env):
        if 'pickup' in self.obj.actions and self.obj.states['inhandofrobot'].get_value(env):
            self.value = False
        else:
            self.value = True


class OnTop(AtSameLocation):
    def __init__(self, obj):
        super(OnTop, self).__init__(obj)


class Under(AtSameLocation):
    def __init__(self, obj):
        super(Under, self).__init__(obj)


###########################################################################################################
# OBJECT PROPERTIES

# TODO: CleaningTool
class CleaningTool(ObjectProperty):
    def __init__(self, obj):
        super(CleaningTool, self).__init__(obj)


# TODO: HeatSourceOrSink
class HeatSourceOrSink(ObjectProperty):
    def __init__(self, obj):
        super(HeatSourceOrSink, self).__init__(obj)


# TODO: ObjectsInFOVOfRobot
# class ObjectsInFOVOfRobot(AbsoluteObjectState):


# TODO: Slicer
class Slicer(ObjectProperty):
    def __init__(self, obj):
        super(Slicer, self).__init__(obj)


# TODO: WaterSource
class WaterSource(ObjectProperty):
    def __init__(self, obj):
        super(WaterSource, self).__init__(obj)
