from .rendering import *
from bddl import OBJECT_TO_IDX
from mini_behavior.utils.globals import COLOR_TO_IDX, COLORS
from mini_behavior.utils.objects_base import WorldObj, FurnitureObj


class Can(FurnitureObj):
    def __init__(self, width=1, height=1, color='blue', name='can'):
        super(Can, self).__init__('ashcan', width, height, {0, 1, 2}, color, name, can_contain={0, 1, 2})


class Bed(FurnitureObj):
    def __init__(self, width=3, height=2, color='purple', name='bed'):
        super(Bed, self).__init__('bed', width, height, {0}, color, name) #, can_overlap=True)


class Top_cabinet(FurnitureObj):
    def __init__(self, width=2, height=3, color='pink', name='top_cabinet'):
        super(Top_cabinet, self).__init__('cabinet', width, height, {0, 1, 2}, color, name, can_contain={0, 1, 2}, can_seebehind=False)


class Dresser(FurnitureObj):
    def __init__(self, width=2, height=3, color='brown', name='dresser'):
        super(Dresser, self).__init__('dresser', width, height, {0}, color, name, can_contain={0}, can_seebehind=False)


class Chair(FurnitureObj):
    def __init__(self, width=1, height=1, color='brown', name='chair'):
        super(Chair, self).__init__('chair', width, height, {0, 1}, color, name)


class Ottoman(FurnitureObj):
    def __init__(self, width=1, height=1, color='brown', name='ottoman'):
        super(Ottoman, self).__init__('ottoman', width, height, {0, 1}, color, name)


class Counter(FurnitureObj):
    def __init__(self, width=3, height=2, color='tan', name='counter'):
        super(Counter, self).__init__('counter', width, height, {0}, color, name, can_seebehind=True)


class Counter_top(FurnitureObj):
    def __init__(self, width=3, height=2, color='pink', name='counter_top'):
        super(Counter_top, self).__init__('counter_top', width, height, {0}, color, name, can_seebehind=True)


class Door(FurnitureObj):
    def __init__(self, is_open=False):
        self.is_open = is_open
        super().__init__('door', 1, 1, {0, 1, 2}, 'black', 'door', can_overlap=is_open, can_seebehind=is_open)

    def update(self, env):
        self.is_open = self.states['openable'].get_value(env)
        self.can_overlap = self.is_open
        self.can_seebehind = self.is_open

    def encode(self):
        """Encode the a description of this object as a seed 10_3-tuple of integers"""

        # State, 0: open, seed 0_2: closed, seed 0_2: locked
        if self.is_open:
            state = 0
        # elif self.is_locked:
        #     state = 2
        else:
            state = 1

        return OBJECT_TO_IDX[self.type], COLOR_TO_IDX[self.color], state

    def render(self, img):
        c = COLORS[self.color]

        if self.is_open:
            fill_coords(img, point_in_rect(0.88, 1.00, 0.00, 1.00), c)
            fill_coords(img, point_in_rect(0.92, 0.96, 0.04, 0.96), (0,0,0))
            return

        # Door frame and door
        fill_coords(img, point_in_rect(0.00, 1.00, 0.00, 1.00), c)
        fill_coords(img, point_in_rect(0.04, 0.96, 0.04, 0.96), (0,0,0))
        fill_coords(img, point_in_rect(0.08, 0.92, 0.08, 0.92), c)
        fill_coords(img, point_in_rect(0.12, 0.88, 0.12, 0.88), (0,0,0))

        # Draw door handle
        fill_coords(img, point_in_circle(cx=0.75, cy=0.50, r=0.08), c)


class Fridge(FurnitureObj):
    def __init__(self, width=2, height=3, color='l_blue', name='fridge'):
        super(Fridge, self).__init__('fridge', width, height, {0, 1, 2}, color, name, can_contain={0, 1, 2}, can_seebehind=False)


# TODO: add wall to object properties
class Wall(FurnitureObj):
    def __init__(self, color='grey'):
        super().__init__('wall', 1, 1, {0, 1, 2}, color, 'wall', can_seebehind=False)

    def render(self, img):
        fill_coords(img, point_in_rect(0, 1, 0, 1), COLORS['grey'])


class Shelf(FurnitureObj):
    def __init__(self, width=2, height=3, color='brown', name='shelf'):
        super(Shelf, self).__init__('shelf', width, height, {0, 1}, color, name, can_contain={0, 1}, can_seebehind=False)


class Shelving_unit(FurnitureObj):
    def __init__(self, width=2, height=3, color='red_brown', name='shelving_unit'):
        super(Shelving_unit, self).__init__('shelving_unit', width, height, {0, 1}, color, name, can_contain={0, 1}, can_seebehind=False)


class Sink(FurnitureObj):
    def __init__(self, width=3, height=2, color='blue', name='sink'):
        super(Sink, self).__init__('sink', width, height, {0}, color, name, can_contain={0}, can_overlap=False, can_seebehind=True)


class Sofa(FurnitureObj):
    def __init__(self, width=3, height=2, color='red', name='sofa'):
        super(Sofa, self).__init__('sofa', width, height, {0}, color, name)


class Cooktop(FurnitureObj):
    def __init__(self, width=3, height=2, color='grey', name='cooktop'):
        super(Cooktop, self).__init__('stove', width, height, {0, 1}, color, name, can_contain={0})


class Table(FurnitureObj):
    def __init__(self, width=3, height=2, color='tan', name='table'):
        super(Table, self).__init__('table', width, height, {1}, color, name)


class Coffee_table(FurnitureObj):
    def __init__(self, width=3, height=2, color='tan', name='coffee_table'):
        super(Coffee_table, self).__init__('coffee_table', width, height, {1}, color, name)


class Dining_table(FurnitureObj):
    def __init__(self, width=3, height=2, color='l_purple', name='dining_table'):
        super(Dining_table, self).__init__('dining_table', width, height, {1}, color, name)


class Side_table(FurnitureObj):
    def __init__(self, width=3, height=2, color='tan', name='side_table'):
        super(Side_table, self).__init__('side_table', width, height, {1}, color, name)


class Desk(FurnitureObj):
    def __init__(self, width=3, height=2, color='tan', name='desk'):
        super(Desk, self).__init__('desk', width, height, {1}, color, name)


class T_v_stand(FurnitureObj):
    def __init__(self, width=3, height=2, color='tan', name='t_v_stand'):
        super(T_v_stand, self).__init__('t_v_stand', width, height, {1}, color, name)


class Toilet(FurnitureObj):
    def __init__(self, width=2, height=2, color='l_green', name='toilet'):
        super(Toilet, self).__init__('toilet', width, height, {1}, color, name)


OBJECT_CLASS = {
    "counter": Counter,
    "table": Table,
    "shelf": Shelf,
    "fridge": Fridge,
    "top_cabinet": Top_cabinet,
    "coffee_table": Coffee_table,
    "cooktop": Cooktop,
    "counter_top": Counter_top,
    "dining_table": Dining_table,
    "chair": Chair,
    "t_v_stand": T_v_stand,
    "can": Can,
    "sofa": Sofa,
    "bed": Bed,
    "dresser": Dresser,
    "toilet": Toilet,
    "sink": Sink,
    "shelving_unit": Shelving_unit,
    "desk": Desk,
    "side_table": Side_table,
    "ottoman": Ottoman,
    "wall": Wall,
    "door": Door
}
