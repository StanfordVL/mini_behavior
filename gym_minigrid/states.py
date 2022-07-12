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
#
# RELATIVE
# inside
# nextto
# ontop x
# under

# list of all objects at the current position: env.grid.get(*obj.cur_pos)
#   order of elements in list = order of vertical object placement


def get_obj_cell(self, env):
    obj = self.obj
    cell = env.grid.get(*obj.cur_pos)

    return obj, cell


class Onfloor(AbsoluteObjectState):
    def _get_value(self, env):
        if self.obj.possible_state('agentcarrying') and self.obj.states['agentcarrying'].get_value(env):
            return False

        obj, cell = get_obj_cell(self, env)

        if not isinstance(cell, list):
            return True
        else:
            return obj == cell[0]


# class Inroom(AbsoluteObjectState):
#     def _get_value(self):
#         obj, env, cell = init(self)
#         agent_room = env.room_from_pos(*env.agent_pos)
#         obj_room = env.room_from_pos(*obj.cur_pos)
#
#         return agent_room == obj_room


class Agentcarrying(AbsoluteObjectState):
    def __init__(self, obj, value=False):
        super(Agentcarrying, self).__init__(obj)
        self.value = value

    def _get_value(self, env):
        return self.value

    def _set_value(self, new_value):
        self.value = new_value


class Contains(AbsoluteObjectState):
    def __init__(self, obj, value=False):
        super(Contains, self).__init__(obj)
        self.value = value
        self.contains_objs = []

    def _get_value(self, env):
        return self.value

    def _set_value(self, new_value):
        self.value = new_value

    def add_obj(self, obj):
        self.contains_objs.append(obj)
        self.value = True

    def remove_obj(self, obj):
        self.contains_objs.remove(obj)


class Overlap(StaticObjectState):
    def _get_value(self):
        return True


class Seebehind(StaticObjectState):
    def _get_value(self):
        return True


class Ontop(RelativeObjectState):
    # returns true if obj is ontop other
    def _get_value(self, other, env):
        if self.obj.states['agentcarrying'].get_value(env):
            return False

        obj, cell = get_obj_cell(self, env)

        # if obj and other are at the same pos
        # if np.all(obj.cur_pos == other.cur_pos):
        #     cell = env.grid.get(*obj.cur_pos)
        if isinstance(cell, list):
            if other in cell:
                obj_index = cell.index(obj)
                other_index = cell.index(other)
                if obj_index > other_index:
                    return True

        return False


class Inside(RelativeObjectState):
    # returns true if obj is inside other
    # define obj is inside other: obj is ontop other and other can contain
    def _get_value(self, other, env):
        return self.obj.states['ontop'].get_value(other, env) and other.possible_state("contains")

