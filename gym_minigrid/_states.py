import numpy as np


# return true if p1 is on top of p2
def on_top(env, p1, p2):
    if np.all(p1.cur_pos == p2.cur_pos):
        cell = env.grid.get(*p1.cur_pos)
        p1_index = cell.index(p1)
        p2_index = cell.index(p2)
        if p1_index > p2_index:
            return True
    return False


# return true if p1 is in the room
def in_room():
    return True


# return true if p1 is on the floor
def on_floor(env, p1):
    return p1.on_floor == True


# return true if p1 is inside p2
def inside(env, p1, p2):
    return p2.contains and on_top(env, p1, p2)