import numpy as np
from mini_behavior.utils.globals import DIR_TO_VEC

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

        # check if possibe to do the action on the object
        if not obj.possible_action(self.key):
            return False

        # check if the object is in reach of the agent
        # if not obj.check_abs_state(self.env, 'inreachofrobot'):
            # return False

        return True

    def do(self, obj):
        """
        do action
        """
        assert self.can(obj), 'Cannot perform action'


class Close(BaseAction):
    def __init__(self, env):
        super(Close, self).__init__(env)
        self.key = 'close'

    def do(self, obj):
        super().do(obj)
        obj.states['openable'].set_value(False)
        obj.update(self.env)


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
            front_cell = self.env.grid.get_all_items(*self.env.agent_pos)
            for obj2 in front_cell:
                if obj2 is not None and obj2.type in self.heat_sources:
                    return obj2.check_abs_state(self.env, 'toggleable')
        return False

    def do(self, obj):
        super().do(obj)
        obj.states['cookable'].set_value(True)


class Drop(BaseAction):
    def __init__(self, env):
        super(Drop, self).__init__(env)
        self.key = 'drop'

    def drop_dims(self, obj):
        dims = []
        pos = self.env.agent_pos + DIR_TO_VEC[self.env.agent_dir]

        all_items = self.env.grid.get_all_items(*pos)
        last_furniture, last_obj = 'floor', 'floor'
        breakpoint()
        for i in range(3):
            furniture = all_items[2*i]
            obj = all_items[2*i + 1]

            if furniture is None and obj is None:
                if last_furniture is not None or last_obj is not None:
                    dims.append(i)

            last_furniture = furniture
            last_obj = obj

        return dims

    def can(self, obj):
        """
        can drop obj if:
        - agent is carrying obj
        - there is no obj in base of forward cell
        """
        if not super().can(obj):
            return False

        if not obj.check_abs_state(self.env, 'inhandofrobot'):
            return False

        fwd_pos = self.env.front_pos
        dims = self.drop_dims(fwd_pos)

        return dims != []

    def do(self, obj, dim=2):
        super().do(obj)

        self.env.carrying.discard(obj)

        fwd_pos = self.env.front_pos

        # change object properties
        obj.cur_pos = fwd_pos
        # change agent / grid
        self.env.grid.set(*fwd_pos, obj, dim)


class DropIn(BaseAction):
    def __init__(self, env):
        super(DropIn, self).__init__(env)
        self.key = 'drop_in'

    def drop_dims(self, pos):
        dims = []

        all_items = self.env.grid.get_all_items(*pos)
        last_obj = 'floor'
        for i in range(3):
            furniture = all_items[2*i]
            obj = all_items[2*i + 1]

            if obj is None and furniture is not None and furniture.can_contain and i in furniture.can_contain:
                if 'openable' not in furniture.states or furniture.check_abs_state(self.env, 'openable'):
                    if last_obj is not None:
                        dims.append(i)

            last_obj = obj
        return dims

    def can(self, obj):
        """
        can drop obj under if:
        - agent is carrying obj
        - middle of forward cell is open
        - obj does not contain another obj
        """
        print("=" * 20)
        print(self, obj.name)
        if not super().can(obj):
            return False

        if not obj.check_abs_state(self.env, 'inhandofrobot'):
            return False

        # Check if there is any furniture item we can drop the object in
        fwd_pos = self.env.front_pos
        furniture = None

        for i in range(3):
            furniture = self.env.grid.get_furniture(*fwd_pos, dim=i)
            if furniture is not None:
                break 

        # If none, we can't drop the furniture object
        if furniture is None:
            return False

        print(self, obj.name, furniture)
        # Check if there is available room on the furniture object
        # We test all valid positions
        print('test')
        print(furniture.all_pos)
        for pos in furniture.all_pos:
            dims = self.drop_dims(pos)
            print(dims, pos)
            if len(dims) > 0:
                print(dims)
                return True

        print("=" * 20)
        return False


    def do(self, obj, dim=2):
        super().do(obj)
        self.env.carrying.discard(obj)

        fwd_pos = self.env.front_pos
        furniture = None
        for i in range(3):
            furniture = self.env.grid.get_furniture(*fwd_pos, dim=i)
            if furniture is not None:
                break 

        assert furniture is not None

        for pos in furniture.all_pos:
            dims = self.drop_dims(pos)
            if len(dims) > 0:
                # TODO (mjlbach): Should we change this?
                dim = dims[0]
                obj.cur_pos = pos
                self.env.grid.set(*pos, obj, dim)
                # drop in and update
                obj.states['inside'].set_value(furniture, True)
                break



class Open(BaseAction):
    def __init__(self, env):
        super(Open, self).__init__(env)
        self.key = 'open'

    def do(self, obj):
        super().do(obj)
        obj.states['openable'].set_value(True)
        obj.update(self.env)


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

        # Can only pickup adjacent objects
        if np.linalg.norm(self.env.agent_pos - np.array(obj.cur_pos)) >= 3:
            return False

        return True

    def do(self, obj):
        super().do(obj)
        self.env.carrying.add(obj)

        objs = self.env.grid.get_all_objs(*obj.cur_pos)
        dim = objs.index(obj)

        # remove obj from the grid and shift remaining objs
        self.env.grid.remove(*obj.cur_pos, obj)

        if dim < 2:
            new_objs = objs[: dim] + objs[dim + 1:] + [None]
            assert len(new_objs) == 3
            self.env.grid.set_all_objs(*obj.cur_pos, new_objs)

        # update cur_pos of obj
        obj.update_pos(np.array([-1, -1]))

        # check dependencies
        assert obj.check_abs_state(self.env, 'inhandofrobot')
        assert not obj.check_abs_state(self.env, 'onfloor')


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

class GoTo(BaseAction):
    def __init__(self, env):
        super(GoTo, self).__init__(env)
        self.key = 'goto'
        self.max_search_size = 10

    def can(self, obj):
        if obj.check_abs_state(self.env, 'inhandofrobot'):
            return False
        return True

    def do(self, obj):
        """
        find the closest reachable position to obj and update the agent's position and direction to face the object
        """
        super().do(obj)
        obj_pos = obj.cur_pos
        for search_size in range(self.max_search_size):
            for candidate_dir, candidate_vec in enumerate(DIR_TO_VEC):
                candidate_pos = obj_pos - search_size * candidate_vec
                if candidate_pos[0] < 0 or candidate_pos[0] >= self.env.grid.width or candidate_pos[1] < 0 or candidate_pos[1] >= self.env.grid.height:
                    continue
                if self.env.grid.is_empty(candidate_pos[0], candidate_pos[1]):
                    self.env.agent_pos = candidate_pos
                    self.env.agent_dir = candidate_dir
                    return

ACTION_FUNC_MAPPING = {
    'pickup': Pickup,
    'drop': Drop,
    'drop_in': DropIn,
    'toggle': Toggle,
    'open': Open,
    'close': Close,
    'slice': Slice,
    'cook': Cook,
    'goto': GoTo,
}

def get_allowable_actions(env):
    action_strs = []
    actions = []
    for action_str, action in ACTION_FUNC_MAPPING.items():
        print(action_str, action)
        for obj in env.obj_instances.values(): #type: ignore
            if action(env).can(obj):
                actions.append((action, obj))
                action_strs.append(f"{action_str} + {obj.name}")
    return action_strs, actions

