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
        def pick(obj1):
            # if obj1 was in obj2, then no longer inside (unless obj2 is also being picked up)
            # for obj2 in obj1.states['inside'].inside_of:
            #     if not obj2.states['inhandofrobot'].get_value(self.env):
            #         obj1.states['inside'].set_value(obj2, False)

            self.env.grid.remove(*obj1.cur_pos, obj1)  # remove obj from the grid
            obj1.cur_pos = np.array([-1, -1])  # update cur_pos of obj
            # self.env.agent.carrying.append(obj) # update list of objects being carried by agent

            # check dependencies
            assert obj.states['inhandofrobot'].get_value(self.env)
            assert not obj.states['onfloor'].get_value(self.env)

        super().do(obj)
        pick(obj)

        # if obj1 was in obj2, then no longer inside (unless obj2 is also being picked up)
        if obj.states['inside'].inside_of:
            obj2 = obj.states['inside'].inside_of
            obj.states['inside'].set_value(obj2, False)

        if obj.can_contain:
            for other in obj.contains:
                pick(other)


class Drop(BaseAction):
    def __init__(self, env):
        super(Drop, self).__init__(env)
        self.key = 'drop'

    def can(self, obj):
        if not super().can(obj):
            return False

        return obj.states['inhandofrobot'].get_value(self.env)

    def do(self, obj):
        fwd_pos = self.env.agent.front_pos

        def drop(obj1):
            # change object properties
            obj1.cur_pos = fwd_pos
            # change agent / grid
            self.env.grid.set(*fwd_pos, obj1)

        super().do(obj)
        drop(obj)

        inside = obj.states['inside'].inside_of
        if inside:
            obj.states['inside'].set_value(inside, False) # could have been in an obj when agent was carrying

        # all objs inside obj get dropped too. they stay inside obj
        if obj.can_contain:
            for other in obj.contains:
                drop(other)


class DropIn(Drop):
    def __init__(self, env):
        super(DropIn, self).__init__(env)
        self.key = 'drop_in'
        self.drop_in_obj = None

    def can(self, obj):
        """
        possible if agent can drop obj
        and if there is an object in the front cell that can_contain
        """
        if not super().can(obj):
            return False

        fwd_pos = self.env.agent.front_pos
        cell = self.env.grid.get(*fwd_pos)

        if cell is None:
            return False

        front_can_contain = False
        cell = cell if isinstance(cell, list) else [cell]
        for obj2 in cell:
            if obj2.can_contain:
                if 'openable' not in obj2.state_keys or obj2.states['openable'].get_value(self.env):
                    front_can_contain = True
                    self.drop_in_obj = obj2

        return front_can_contain

    def do(self, obj):
        # drop
        super().do(obj)

        # drop in
        obj.states['inside'].set_value(self.drop_in_obj, True)


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
        obj.states['openable'].set_value(True)
        obj.update(self.env)


# TODO: check this works
class Close(BaseAction):
    # "backpack", "cabinet", "car", "carton", "door", "electric_refrigerator", "folder", "jar", "package", "stove", "window"
    def __init__(self, env):
        super(Close, self).__init__(env)
        self.key = 'close'

    def do(self, obj):
        super().do(obj)
        obj.states['openable'].set_value(False)
        obj.update(self.env)

# class Unlock(BaseAction):
#     # "door"
#     def __init__(self, env):
#         super(Unlock, self).__init__(env)
#         self.key = 'unlock'


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
        obj.states['sliceable'].set_value()


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
            front_cell = self.env.grid.get(*self.env.agent.front_pos)
            if isinstance(front_cell, list):
                for obj2 in front_cell:
                    if obj2.type in self.heat_sources:
                        return has_a_tool and obj2.states['toggleable'].get_value(self.env)
            elif front_cell:
                if front_cell.type in self.heat_sources:
                    return has_a_tool and front_cell.states['toggleable'].get_value(self.env)

        return False

    def do(self, obj):
        super().do(obj)
        obj.states['cookable'].set_value(True)

        # # if the agent was carrying the obj, drop it after cooking
        # if self.env.agent.is_carrying(obj):
        #     self.env.agent.actions['drop'].do(obj)
