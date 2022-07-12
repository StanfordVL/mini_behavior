import numpy as np
from .bddl_utils import *
from .utils import *
from .states import *
# functions to check if agent has the ability to perform an action on a given object
# pickup object


class BaseAction:
    def __init__(self, obj):
        super(BaseAction, self).__init__()
        self.obj = obj
        # self.env = env

    def can(self, env):
        """
        check if possible to do action
        """
        raise NotImplementedError()

    def do(self, env):
        """
        do action
        """
        raise NotImplementedError()


class Pickup(BaseAction):
    def can(self, env):
        # can pickup if not carrying and if not inside somehting
        if self.obj.states['agentcarrying'].get_value(env):
            return False

        obj, cell = get_obj_cell(self, env)

        if isinstance(cell, list):
            for other_obj in cell:
                if obj.states['inside'].get_value(other_obj, env):
                    return False

        return True

    def do(self, env):
        assert self.can(env), 'Cannot perform action'
        obj, _ = get_obj_cell(self, env)

        # env.grid.remove(*env.front_pos, obj)  # remove obj from the grid
        env.grid.remove(*obj.cur_pos, obj)  # remove obj from the grid
        obj.cur_pos = np.array([-1, -1]) # update cur_pos of obj
        obj.states['agentcarrying'].set_value(True)
        env.carrying.append(obj) # update list of objects being carried by agent

        # check dependencies
        assert not obj.states['onfloor'].get_value(env)


class Drop(BaseAction):
    def can(self, env):
        return self.obj.states['agentcarrying'].get_value(env)

    def do(self, env):
        assert self.can(env), 'Cannot perform action'

        obj = self.obj
        fwd_pos = env.front_pos
        cell = env.grid.get(*fwd_pos)

        # change object properties
        obj.cur_pos = fwd_pos
        obj.states['agentcarrying'].set_value(False)

        # change agent / grid
        env.grid.set(*fwd_pos, obj)
        env.carrying.remove(obj)

        if isinstance(cell, list):
            for other_obj in cell:
                if 'contains' in other_obj.state_keys:
                    other_obj.states['contains'].set_value(True)
                    other_obj.states['contains'].add_obj(obj)
        elif cell is not None:
            if 'contains' in cell.state_keys:
                cell.states['contains'].set_value(True)
                cell.states['contains'].add_obj(obj)

        # check dependencies
        if cell == [] or cell is None:
            assert obj.states['onfloor'].get_value(env)
        else:
            assert not obj.states['onfloor'].get_value(env)

