from .states_base import *

# ABSOLUTE
# broken
# burnt
# cooked
# dusty
# frozen
# open
# perished
# screwed
# stained
# sliced
# soaked
# timset
# toggledon

# RELATIVE
# inside -- done
# nextto -- done
# ontop -- done
# under -- done

# list of all objects at the current position: env.grid.get(*obj.cur_pos)
#   order of elements in list = order of vertical object placement


def get_obj_cell(self, env):
    obj = self.obj
    cell = env.grid.get(*obj.cur_pos)

    return obj, cell


# TODO: check that get_value is correct
class Onfloor(AbsoluteObjectState):
    def _get_value(self, env):
        # if self.obj.possible_state('agentcarrying') and self.obj.states['agentcarrying'].get_value(env):
        if env.agent.is_carrying(self.obj):
            return False

        obj, cell = get_obj_cell(self, env)

        if not isinstance(cell, list):
            return True
        else:
            return obj == cell[0]


class InFrontOfAgent(AbsoluteObjectState):
    # return true if obj is in front of agent
    def _get_value(self, env):

        agent_front = env.agent.front_pos
        obj_pos = self.obj.cur_pos

        return agent_front == obj_pos


class Ontop(RelativeObjectState):
    # returns true if obj is ontop other
    def _get_value(self, other, env):
        if env.agent.is_carrying(self.obj):
            return False

        obj, cell = get_obj_cell(self, env)

        # if obj and other are at the same pos
        if isinstance(cell, list):
            if other in cell:
                obj_index = cell.index(obj)
                other_index = cell.index(other)
                if obj_index > other_index:
                    return True
        return False


class Under(RelativeObjectState):
    # returns true if self.obj is under other
    def _get_value(self, other, env):
        if env.agent.is_carrying(self.obj):
            return False

        obj, cell = get_obj_cell(self, env)

        if isinstance(cell, list):
            # if obj and other are at the same pos
            if other in cell:
                obj_index = cell.index(obj)
                other_index = cell.index(other)
                if obj_index < other_index:
                    return True
        return False


# TODO: check that inside function works
class Inside(RelativeObjectState):
    # returns true if obj is inside other
    # define obj is inside other: obj is ontop other and other can contain
    def _get_value(self, other, env):
        # return self.obj.states['ontop'].get_value(other, env) and other.can_contain
        return self.obj in other.contains


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
