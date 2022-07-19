import numpy as np
# functions to check if agent has the ability to perform an action on a given object


def get_cell(env, obj):
    cell = env.grid.get(*obj.cur_pos)
    return cell


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
        if not self.env.agent.reachable(obj):
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

        # can pickup if not carrying and if not inside somehting
        if self.env.agent.is_carrying(obj):
            return False

        cell = get_cell(self.env, obj)

        if isinstance(cell, list):
            for other_obj in cell:
                if obj.states['inside'].get_value(other_obj, self.env):
                    return False

        return True

    def do(self, obj):
        super().do(obj)

        self.env.grid.remove(*obj.cur_pos, obj)  # remove obj from the grid
        obj.cur_pos = np.array([-1, -1]) # update cur_pos of obj
        self.env.agent.carrying.append(obj) # update list of objects being carried by agent

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
        self.env.agent.carrying.remove(obj)

        if isinstance(cell, list):
            for other_obj in cell:
                if other_obj.can_contain:
                    other_obj.contains.append(obj)
        elif cell is not None:
            if cell.can_contain:
                cell.contains.append(obj)

        # check dependencies
        if cell == [] or cell is None:
            assert obj.states['onfloor'].get_value(self.env)
        else:
            assert not obj.states['onfloor'].get_value(self.env)

