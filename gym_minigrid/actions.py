import numpy as np


def find_tool(env, possible_tool_types):
    # returns whether agent is carrying a obj of possible_tool_types, and the obj_instance
    for tool_type in possible_tool_types:
        tools = env.objs.get(tool_type, []) # objs of type tool in the env
        for tool in tools:
            if tool.check_abs_state(env, 'inhandofrobot'):
                return True
    return False


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

        # check if possible to do the action on the object
        if not obj.possible_action(self.key):
            return False

        # check if the object is in reach of the agent
        if not obj.check_abs_state(self.env, 'inreachofrobot'):
            return False

        return True

    def do(self, obj):
        """
        do action
        """
        assert self.can(obj), 'Cannot perform action'
        self.env.agent.obj = obj


class Close(BaseAction):
    def __init__(self, env):
        super(Close, self).__init__(env)
        self.key = 'close'

    def do(self, obj):
        super().do(obj)
        obj.states['openable'].set_value(False)
        obj.update(self.env)

        if self.env.grid.get_dim(*obj.cur_pos, 2) is None:
            self.env.grid.set(*obj.cur_pos, False, 2)

        if obj.is_furniture():
            for pos in obj.all_pos:
                if self.env.grid.get_dim(*pos, 2) is None:
                    self.env.grid.set(*pos, False, 2)


class Cook(BaseAction):
    def __init__(self, env):
        super(Cook, self).__init__(env)
        self.key = 'cook'
        self.tools = ['pan']
        self.heat_sources = ['stove']

    def can(self, obj):
        """
        can perform action if:
        - obj is cookable
        - agent is carrying a cooking tool
        - agent is infront of a heat source
        - the heat source is toggled on
        """
        if not super().can(obj):
            return False

        if find_tool(self.env, self.tools):
            front_cell = self.env.grid.get(*self.env.agent.front_pos)
            # if isinstance(front_cell, list):
            for obj2 in front_cell:
                if obj2.type in self.heat_sources:
                    return obj2.check_abs_state(self.env, 'toggleable')
        return False

    def do(self, obj):
        super().do(obj)
        obj.states['cookable'].set_value(True)


class Drop(BaseAction):
    def __init__(self, env):
        super(Drop, self).__init__(env)
        self.key = 'drop'

    def can(self, obj):
        """
        can drop obj if:
        - agent is carrying obj
        - there is no obj in base of forward cell
        """
        if not super().can(obj):
            return False

        fwd_pos = self.env.agent.front_pos
        base = self.env.grid.get_dim(*fwd_pos, 0)

        return obj.check_abs_state(self.env, 'inhandofrobot') and base is None

    def do(self, obj):
        super().do(obj)

        fwd_pos = self.env.agent.front_pos

        # change object properties
        obj.cur_pos = fwd_pos
        # change agent / grid
        self.env.grid.set(*fwd_pos, obj, 0)

        # if obj2 in obj, also drop obj2
        if obj.contains:
            obj.contains.cur_pos = fwd_pos
            self.env.grid.set(*fwd_pos, obj.contains, 2)

        # if inside obj2, obj no longer inside
        if obj.inside_of:
            obj.states['inside'].set_value(obj.inside_of, False)


class DropIn(BaseAction):
    def __init__(self, env):
        super(DropIn, self).__init__(env)
        self.key = 'drop_in'

    def can(self, obj):
        """
        can drop obj under if:
        - agent is carrying obj
        - middle of forward cell is open
        - obj does not contain another obj
        """
        if not super().can(obj):
            return False

        fwd_pos = self.env.agent.front_pos
        middle = self.env.grid.get_dim(*fwd_pos, 2)

        return obj.check_abs_state(self.env, 'inhandofrobot') and middle is None and obj.contains is None

    def do(self, obj):
        # drop
        super().do(obj)
        fwd_pos = self.env.agent.front_pos
        obj.cur_pos = fwd_pos
        self.env.grid.set(*fwd_pos, obj, 2)

        if obj.inside_of:
            obj.states['inside'].set_value(obj.inside_of, False)

        # drop in and update
        base = self.env.grid.get_dim(*fwd_pos, 0)
        obj.states['inside'].set_value(base, True)


class DropOn(BaseAction):
    def __init__(self, env):
        super(DropOn, self).__init__(env)
        self.key = 'drop_on'

    def can(self, obj):
        """
        can drop obj on top if:
        - agent is carrying obj
        - there is no obj in top of forward cell
        - obj does not contain another obj
        """
        if not super().can(obj):
            return False

        fwd_pos = self.env.agent.front_pos
        top = self.env.grid.get_dim(*fwd_pos, 1)

        return obj.check_abs_state(self.env, 'inhandofrobot') and top is None and obj.contains is None

    def do(self, obj):
        # drop
        super().do(obj)
        fwd_pos = self.env.agent.front_pos
        obj.cur_pos = fwd_pos
        self.env.grid.set(*fwd_pos, obj, 1)

        if obj.inside_of:
            obj.states['inside'].set_value(obj.inside_of, False)


class DropUnder(BaseAction):
    def __init__(self, env):
        super(DropUnder, self).__init__(env)
        self.key = 'drop_under'

    def can(self, obj):
        """
        can drop obj under if:
        - agent is carrying obj
        - bottom of forward cell is open
        - obj does not contain another obj
        """
        if not super().can(obj):
            return False

        fwd_pos = self.env.agent.front_pos
        bottom = self.env.grid.get_dim(*fwd_pos, 3)

        return obj.check_abs_state(self.env, 'inhandofrobot') and bottom is None and obj.contains is None

    def do(self, obj):
        # drop
        super().do(obj)
        fwd_pos = self.env.agent.front_pos
        obj.cur_pos = fwd_pos
        self.env.grid.set(*fwd_pos, obj, 3)

        if obj.inside_of:
            obj.states['inside'].set_value(obj.inside_of, False)


class Open(BaseAction):
    def __init__(self, env):
        super(Open, self).__init__(env)
        self.key = 'open'

    def do(self, obj):
        super().do(obj)
        obj.states['openable'].set_value(True)
        obj.update(self.env)

        if obj.check_abs_state(self.env, 'onfloor'):
            middle = self.env.grid.get_dim(*obj.cur_pos, 2)
            if not middle:
                self.env.grid.set(*obj.cur_pos, None, 2)
            if obj.is_furniture():
                for pos in obj.all_pos:
                    middle = self.env.grid.get_dim(*pos, 2)
                    if not middle:
                        self.env.grid.set(*pos, None, 2)


class Pickup(BaseAction):
    def __init__(self, env):
        super(Pickup, self).__init__(env)
        self.key = 'pickup'

    def can(self, obj):
        if not super().can(obj):
            return False

        # cannot pickup if carrying
        if obj.check_abs_state(self.env, 'inhandofrobot'):
            return False

        # cannot pickup if inside closed obj
        base = self.env.grid.get_dim(*obj.cur_pos, 0)
        if obj.check_rel_state(self.env, base, 'inside') and not base.check_abs_state(self.env, 'openable'):
            return False

        return True

    def do(self, obj):
        def pick(obj1):
            self.env.grid.remove(*obj1.cur_pos, obj1)  # remove obj from the grid and unblock slots
            obj1.update_pos(np.array([-1, -1])) # update cur_pos of obj

            # check dependencies
            assert obj.check_abs_state(self.env, 'inhandofrobot')
            assert not obj.check_abs_state(self.env, 'onfloor')

            # pickup object inside
            if obj1.contains:
                pick(obj1.contains)

        super().do(obj)
        pick(obj)

        # if obj was inside, then no longer inside
        if obj.inside_of:
            obj.states['inside'].set_value(obj.inside_of, False)


class Slice(BaseAction):
    def __init__(self, env):
        super(Slice, self).__init__(env)
        self.key = 'slice'
        self.slicers = ['carving_knife', 'knife']

    def can(self, obj):
        """
        can perform action if:
        - action is sliceable
        - agent is holding a slicer
        """
        if not super().can(obj):
            return False
        return find_tool(self.env, self.slicers)

    def do(self, obj):
        super().do(obj)
        obj.states['sliceable'].set_value()


class Toggle(BaseAction):
    def __init__(self, env):
        super(Toggle, self).__init__(env)
        self.key = 'toggle'

    def do(self, obj):
        """
        toggle from on to off, or off to on
        """
        super().do(obj)
        cur = obj.check_abs_state(self.env, 'toggleable')
        obj.states['toggleable'].set_value(not cur)

