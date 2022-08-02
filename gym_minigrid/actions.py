import numpy as np
# functions to check if agent has the ability to perform an action on a given object


def get_cell(env, obj):
    cell = env.grid.get(*obj.cur_pos)
    return cell


def find_tool(env, possible_tool_types):
    # returns whether agent is carrying a obj of possible_tool_types, and the obj_instance
    for tool_type in possible_tool_types:
        tools = env.objs.get(tool_type, []) # objs of type tool in the env
        for tool in tools:
            if env.agent.is_carrying(tool):
                return True, tool
    return False, None


class BaseAction:
    def __init__(self, env):
        """
        initialize action
        """
        super(BaseAction, self).__init__()
        self.env = env
        self.key = None

    def can(self, obj):
        """
        check if possible to do action
        """
        if not obj.possible_action(self.key):
            return False
        if not obj.states['inreachofrobot'].get_value(self.env):
            return False
        return True

    def do(self, obj):
        """
        do action
        """
        assert self.can(obj), 'Cannot perform action'
        self.env.agent.obj = obj


class Pickup(BaseAction):
    def __init__(self, env):
        super(Pickup, self).__init__(env)
        self.key = 'pickup'

    def can(self, obj):
        if not super().can(obj):
            return False

        # can pickup if not carrying and if not inside something that is closed
        if self.env.agent.is_carrying(obj):
            return False

        cell = get_cell(self.env, obj)

        if isinstance(cell, list):
            for other_obj in cell:
                if obj.states['inside'].get_value(other_obj, self.env):
                    if 'openable' in other_obj.state_keys and not other_obj.states['openable'].get_value(self.env):
                        return False

        return True

    def do(self, obj):
        super().do(obj)

        self.env.grid.remove(*obj.cur_pos, obj)  # remove obj from the grid
        obj.cur_pos = np.array([-1, -1]) # update cur_pos of obj
        # self.env.agent.carrying.append(obj) # update list of objects being carried by agent

        # check dependencies
        assert not obj.states['onfloor'].get_value(self.env)


class Drop(BaseAction):
    def __init__(self, env):
        super(Drop, self).__init__(env)
        self.key = 'drop'

    def can(self, obj):
        if not super().can(obj):
            return False

        return self.env.agent.is_carrying(obj)

    def do(self, obj):
        super().do(obj)

        fwd_pos = self.env.agent.front_pos
        cell = self.env.grid.get(*fwd_pos)

        # change object properties
        obj.cur_pos = fwd_pos

        # change agent / grid
        self.env.grid.set(*fwd_pos, obj)
        # self.env.agent.carrying.remove(obj)

        if isinstance(cell, list):
            for other_obj in cell:
                if other_obj.can_contain:
                    other_obj.contains.append(obj)
        elif cell is not None:
            if cell.can_contain:
                cell.contains.append(obj)
        # check dependencies
        # if cell == [] or cell is None:
        #     assert obj.states['onfloor'].get_value(self.env)
        # else:
        #     assert not obj.states['onfloor'].get_value(self.env)


# TODO: check this works
class Toggle(BaseAction):
    # "blender", "calculator", "printer", "sink", "stove"
    def __init__(self, env):
        super(Toggle, self).__init__(env)
        self.key = 'toggle'

    def do(self, obj):
        """
        toggle from on to off, or off to on
        """
        super().do(obj)
        cur = obj.states['toggleable'].get_value(self.env)
        obj.states['toggleable'].set_value(not cur)


# TODO: check this works
class Open(BaseAction):
    # "backpack", "cabinet", "car", "carton", "door", "electric_refrigerator", "folder", "jar", "package", "stove", "window"
    def __init__(self, env):
        super(Open, self).__init__(env)
        self.key = 'open'

    def do(self, obj):
        super().do(obj)
        obj.Open.set_value(True)


# TODO: check this works
class Close(BaseAction):
    # "backpack", "cabinet", "car", "carton", "door", "electric_refrigerator", "folder", "jar", "package", "stove", "window"
    def __init__(self, env):
        super(Close, self).__init__(env)
        self.key = 'close'

    def do(self, obj):
        super().do(obj)
        obj.Open.set_value(False)


# class Unlock(BaseAction):
#     # "door"
#     def __init__(self, env):
#         super(Unlock, self).__init__(env)
#         self.key = 'unlock'


# TODO: check this works
class Slice(BaseAction):
    # "apple", "lemon", "strawberry", "tomato"
    def __init__(self, env):
        super(Slice, self).__init__(env)
        self.key = 'slice'
        self.slicers = ['carving_knife', 'knife']

    def can(self, obj):
        if not super().can(obj):
            return False
        # has_slicer, _ = find_tool(self.env, self.env.state_objs['slicer'])
        has_slicer, _ = find_tool(self.env, self.slicers)
        return has_slicer

    def do(self, obj):
        super().do(obj)
        obj.Sliced.set_value()


# TODO: check this works
class Cook(BaseAction):
    def __init__(self, env):
        super(Cook, self).__init__(env)
        self.key = 'cook'
        self.tools = ['pan']
        self.heat_sources = ['stove']

    def can(self, obj):
        """
        agent is able to cook obj if:
            obj is cookable
            agent is carrying a cooking tool
            agent is infront of a heat source
            the heat source is toggled on
        """
        if not super().can(obj):
            return False

        has_a_tool, _ = find_tool(self.env, self.tools)

        if has_a_tool:
            front_cell = self.env.grid.get(self.env.agent.front_pos())
            if isinstance(front_cell, list):
                for obj in front_cell:
                    if obj.type in self.heat_sources:
                        return has_a_tool and obj.states['toggleable'].get_value(self.env)
            elif front_cell:
                if front_cell.type in self.heat_sources:
                    return has_a_tool and obj.states['toggleable'].get_value(self.env)

        return False

    def do(self, obj):
        super().do(obj)
        obj.states['cookable'].set_value()

        # if the agent was carrying the obj, drop it after cooking
        if self.env.agent.is_carrying(obj):
            self.env.agent.Drop.do(obj)
