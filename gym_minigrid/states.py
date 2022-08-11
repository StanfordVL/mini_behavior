from .utils.states_base import *
import numpy as np
from .bddl.objs import FURNITURE


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
        return env.agent.in_view(*self.obj.cur_pos)


class InHandOfRobot(AbsoluteObjectState):
    # return true if agent is carrying the object
    def _get_value(self, env=None):
        return np.all(self.obj.cur_pos == np.array([-1, -1]))


class InReachOfRobot(AbsoluteObjectState):
    # return true if obj is reachable by agent
    def _get_value(self, env=None):
        # obj not reachable if inside closed obj2
        inside = self.obj.inside_of
        if inside is not None and 'openable' in inside.states.keys() and not inside.check_abs_state(env, 'openable'):
            return False

        carrying = self.obj.check_abs_state(env, 'inhandofrobot')

        if self.obj.type in FURNITURE:
            in_front = False
            for pos in self.obj.all_pos:
                if np.all(pos == env.agent.front_pos):
                    in_front = True
                    break
        else:
            in_front = np.all(self.obj.cur_pos == env.agent.front_pos)

        return carrying or in_front


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

class Cooked(AbilityState):
    """
    Cooked(obj) only changes when Cook action is done on the obj
    """
    def __init__(self, obj, key):
        super(Cooked, self).__init__(obj, key)


class Dusty(AbilityState):
    def __init__(self, obj, key):
        """
        not reversible
        """
        super(Dusty, self).__init__(obj, key)
        self.tools = ["broom", "rag", "scrub_brush", "towel"]

    def _update(self, env):
        """
        Always init True
        False if at any point, obj and cleaningTool are in the same location
        """
        # for tool_type in env.state_objs['cleaningTool']:
        for tool_type in self.tools:
            for tool in env.objs.get(tool_type, []):
                if self.obj.check_rel_state(env, tool, 'atsamelocation'):
                    self.value = False


class Frozen(AbilityState):
    def __init__(self, obj, key):
        super(Frozen, self).__init__(obj, key)
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
                if self.obj.check_rel_state(env, cold_source, 'inside'):
                    self.value = True

        return self.value


class Opened(AbilityState):
    def __init__(self, obj, key):
        """
        Value changes only when Open action is done on obj
        """
        super(Opened, self).__init__(obj, key)


class Sliced(AbilityState):
    def _set_value(self, new_value=True):
        self.value = True


class Soaked(AbilityState):
    def __init__(self, obj, key):
        super(Soaked, self).__init__(obj, key)
        self.tools = ['sink']

    def _update(self, env):
        """
        not reversible
        True if at any point, the obj is at the same location as a water source that is toggled on
        """
        for tool_type in self.tools:
            for water_source in env.objs.get(tool_type, []):
                if water_source.check_abs_state(env, 'toggleable'):
                    if self.obj.check_rel_state(env, water_source, 'atsamelocation'):
                        self.value = True


class Stained(AbilityState):
    def __init__(self, obj, key):
        """
        Always init True
        """
        super(Stained, self).__init__(obj, key)
        self.tools = ['rag', 'scrub_brush', 'towel']

    def _update(self, env):
        """
        not reversible
        False if at any point, the obj is at the same location as a soaked cleaning tool
        """
        for tool_type in self.tools:
            for cleaning_tool in env.objs.get(tool_type, []):
                if cleaning_tool.check_abs_state(env, 'soakable'):
                    if self.obj.check_rel_state(env, cleaning_tool, 'atsamelocation'):
                        self.value = False


class ToggledOn(AbilityState):
    def __init__(self, obj, key): # env
        super(ToggledOn, self).__init__(obj, key)


###########################################################################################################
# RELATIVE OBJECT STATES

class AtSameLocation(RelativeObjectState):
    # returns true if obj is at the same location as other
    # def _update(self, other, env):
    def _get_value(self, other, env=None):
        if other is None:
            return False

        return np.all(self.obj.cur_pos == other.cur_pos)


class Inside(RelativeObjectState):
    """
    Inside(obj1, obj2) change ONLY IF Pickup(obj1) or Drop(obj1) is called
    """
    def __init__(self, obj, key): # env
        super(RelativeObjectState, self).__init__(obj, key)
        self.type = 'relative'

    def _get_value(self, other, env=None):
        # return other in self.inside_of
        if self.obj == other or other is None:
            return False

        return other == self.obj.inside_of

    def _set_value(self, other, new_value):
        if new_value:
            self.obj.inside_of = other
            other.contains = self.obj
        else:
            self.obj.inside_of = None
            other.contains = None


# TODO: fix for furniture
class NextTo(RelativeObjectState):
    # return true if objs are next to each other
    def _get_value(self, other, env=None):
        if other is None:
            return False

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


# TODO: fix for 3D
class OnFloor(AbsoluteObjectState):
    def _update(self, env=None):
        if self.obj.check_abs_state(env, 'inhandofrobot'):
            self.value = False
        else:
            self.value = True


class OnTop(RelativeObjectState):
    def __init__(self, obj, key):
        super(OnTop, self).__init__(obj, key)

    def _get_value(self, other, env=None):
        if other is None:
            return False

        obj, cell = get_obj_cell(self, env)

        obj_idx = cell.index(obj)
        other_idx = cell.index(other)

        if obj_idx > 0 and other_idx > 0:
            return obj_idx < other_idx

        return False


class Under(RelativeObjectState):
    def __init__(self, obj, key):
        super(Under, self).__init__(obj, key)

    def _get_value(self, other, env=None):
        if other is None:
            return False

        obj, cell = get_obj_cell(self, env)

        obj_idx = cell.index(obj)
        other_idx = cell.index(other)

        if obj_idx > 0 and other_idx > 0:
            return obj_idx > other_idx

        return False

###########################################################################################################
# OBJECT PROPERTIES


class CleaningTool(ObjectProperty):
    def __init__(self, obj, key):
        super(CleaningTool, self).__init__(obj, key)


class HeatSourceOrSink(ObjectProperty):
    def __init__(self, obj, key):
        super(HeatSourceOrSink, self).__init__(obj, key)


# class ObjectsInFOVOfRobot(AbsoluteObjectState):


class Slicer(ObjectProperty):
    def __init__(self, obj, key):
        super(Slicer, self).__init__(obj, key)


class WaterSource(ObjectProperty):
    def __init__(self, obj, key):
        super(WaterSource, self).__init__(obj, key)
