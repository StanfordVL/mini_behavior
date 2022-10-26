from mini_behavior.mini_behavior.objects import FurnitureObj
import random


# for all of these functions, assume obj2 is already on the grid

def put_ontop(env, obj1, obj2):
    """
    put obj1 ontop of obj2
    """

    # choose position to put obj1
    if isinstance(obj2, FurnitureObj):
        # TODO: clean up loop logic
        pos = None
        while pos is None:
            all_pos = obj2.all_pos
            random.shuffle(all_pos)
            # pos = random.shuffle(obj2.all_pos)
            for try_pos in all_pos:
                if len(env.grid.get_all_objs(*try_pos)) < 4:
                    pos = try_pos
                    break
    else:
        pos = obj2.cur_pos

    # get max dim of furniture obj
    cell = env.grid.get(*pos)
    n = len(cell.objs)
    cell_objs = [cell.objs[n - i] for i in range(1, n + 1)]
    dim = len(cell_objs) - cell_objs.index(obj2) - 1

    # put_obj at (i,j) at dim+1
    env.put_obj(obj1, *pos, dim + 1)


def put_inside(env, obj1, obj2):
    # choose position to put obj2
    if isinstance(obj2, FurnitureObj):
        # pos = random.choice(obj2.all_pos)
        pos = None
        while pos is None:
            all_pos = obj2.all_pos
            random.shuffle(all_pos)
            # pos = random.shuffle(obj2.all_pos)
            for try_pos in all_pos:
                if len(env.grid.get_all_objs(*try_pos)) < 4:
                    pos = try_pos
                    break
    else:
        pos = obj2.cur_pos

    # put_obj at (i,j) at dim
    dim = random.choice(list(obj2.dims))
    env.put_obj(obj1, *pos, dim)

    # set state inside(obj1, obj2) = True
    obj1.states['inside'].set_value(obj2, True)


def put_contains(env, obj1, obj2):
    put_inside(env, obj2, obj1)


def put_under(env, obj1, obj2):
    if isinstance(obj2, FurnitureObj):
        pos = None
        while pos is None:
            all_pos = obj2.all_pos
            random.shuffle(all_pos)
            # pos = random.shuffle(obj2.all_pos)
            for try_pos in all_pos:
                if len(env.grid.get_all_objs(*try_pos)) < 4:
                    pos = try_pos
                    break
    else:
        pos = obj2.cur_pos

    # get max dim of furniture obj
    cell = env.grid.get(*pos)
    dim = cell.objs.index(obj2)

    # put_obj at (i,j) at dim+1
    env.put_obj(obj1, *pos, dim)
