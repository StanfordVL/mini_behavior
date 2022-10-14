from mini_behavior.objects import FurnitureObj
import random


# for all of these functions, assume obj2 is already on the grid

def put_ontop(env, obj1, obj2):
    """
    put obj1 ontop of obj2
    """

    # choose position to put obj1
    if isinstance(obj2, FurnitureObj):
        pos = random.choice(obj2.all_pos)
    else:
        pos = obj2.cur_pos

    # get dim (d) of furniture obj
    dim = env.get_obj_dim(obj2)

    # put_obj at (i,j) at dim (d+1)
    env.put_obj(obj1, *pos, dim + 1)


def put_inside(env, obj1, obj2):
    if isinstance(obj2, FurnitureObj):
        possible_pos = obj2.all_pos
        # get all possible positions
        # randomly choose a possible position (i, j)
        # get random dim (d) of furniture obj
        # put_obj at (i,j) at dim (d+1)
        # set state to inside = True


def put_contains(env, obj1, obj2):
    put_inside(env, obj2, obj1)


def put_under(env, obj1, obj2):
    put_ontop(env, obj2, obj1)


# what does connected mean?
def put_connected(env, obj1, obj2):
    if isinstance(obj2, FurnitureObj):
        possible_pos = obj2.all_pos