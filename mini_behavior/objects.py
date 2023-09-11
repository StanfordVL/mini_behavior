from .rendering import *
from mini_bddl import OBJECT_TO_IDX
from .utils.globals import COLOR_TO_IDX, COLORS
from .utils.objects_base import WorldObj, FurnitureObj


class Goal(WorldObj):
    def __init__(self, color='green', name='goal'):
        super().__init__('goal', color=color, name=name, can_overlap=True)

    def render(self, img):
        fill_coords(img, point_in_rect(0, 1, 0, 1), COLORS[self.color])


class Ashcan(FurnitureObj):
    def __init__(self, width=1, height=1, color='blue', name='ashcan'):
        super(Ashcan, self).__init__('ashcan', width, height, {0, 1, 2}, color, name, can_contain={0, 1, 2})


class Bed(FurnitureObj):
    def __init__(self, width=3, height=2, color='purple', name='bed'):
        super(Bed, self).__init__('bed', width, height, {0}, color, name, can_overlap=True)


class Bin(FurnitureObj):
    def __init__(self, width=1, height=1, color='purple', name='bin'):
        super(Bin, self).__init__('bin', width, height, {0, 1, 2}, color, name, can_contain={0, 1, 2})


class Box(FurnitureObj):
    def __init__(self, width=2, height=2, color='tan', name='box'):
        super(Box, self).__init__('box', width, height, {0}, color, name, can_contain={0})


class Bucket(FurnitureObj):
    def __init__(self, width=1, height=2, color='l_blue', name='bucket'):
        super(Bucket, self).__init__('bucket', width, height, {0}, color, name, can_contain={0})


class Cabinet(FurnitureObj):
    def __init__(self, width=2, height=3, color='brown', name='cabinet'):
        super(Cabinet, self).__init__('cabinet', width, height, {0, 1, 2}, color, name, can_contain={0, 1, 2}, can_seebehind=False)


class Car(FurnitureObj):
    def __init__(self, width=3, height=2, color='blue', name='car'):
        super(Car, self).__init__('car', width, height, {0, 1}, color, name, can_contain={0})


class Chair(FurnitureObj):
    def __init__(self, width=1, height=1, color='brown', name='chair'):
        super(Chair, self).__init__('chair', width, height, {0, 1}, color, name)


class Countertop(FurnitureObj):
    def __init__(self, width=3, height=2, color='tan', name='countertop'):
        super(Countertop, self).__init__('countertop', width, height, {0}, color, name, can_seebehind=True)


class Door(FurnitureObj):
    def __init__(self, dir=None, width=1, height=1, color='yellow', is_open=False, name='door'):
        self.is_open = is_open
        self.dir = dir
        super().__init__('door', width, height, {
            0, 1, 2}, color, name, can_overlap=is_open, can_seebehind=is_open)

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

    def get_state(self):
        if self.is_open:
            return True
        else:
            return False

    def render(self, img):
        c = COLORS[self.color]

        if self.is_open:
            fill_coords(img, point_in_rect(0.88, 1.00, 0.00, 1.00), c)
            fill_coords(img, point_in_rect(0.92, 0.96, 0.04, 0.96), (0, 0, 0))
            return

        # Door frame and door
        fill_coords(img, point_in_rect(0.00, 1.00, 0.00, 1.00), c)
        fill_coords(img, point_in_rect(0.04, 0.96, 0.04, 0.96), (0, 0, 0))
        fill_coords(img, point_in_rect(0.08, 0.92, 0.08, 0.92), c)
        fill_coords(img, point_in_rect(0.12, 0.88, 0.12, 0.88), (0, 0, 0))

        # Draw door handle
        fill_coords(img, point_in_circle(cx=0.75, cy=0.50, r=0.08), c)


class ElectricRefrigerator(FurnitureObj):
    def __init__(self, width=2, height=3, color='l_blue', name='electric_refrigerator'):
        super(ElectricRefrigerator, self).__init__('electric_refrigerator', width, height, {0, 1, 2}, color, name, can_contain={0, 1, 2}, can_seebehind=False)


# TODO: add wall to object properties
class Wall(FurnitureObj):
    def __init__(self, color='grey'):
        super().__init__('wall', 1, 1, {0, 1, 2}, color, 'wall', can_seebehind=False)

    def render(self, img):
        fill_coords(img, point_in_rect(0, 1, 0, 1), COLORS['grey'])


class Shelf(FurnitureObj):
    def __init__(self, width=2, height=3, color='brown', name='shelf'):
        super(Shelf, self).__init__('shelf', width, height, {0, 1}, color, name, can_contain={0, 1}, can_seebehind=False)


class Shower(FurnitureObj):
    def __init__(self, width=3, height=2, color='l_blue', name='shower'):
        super(Shower, self).__init__('shower', width, height, {0, 1, 2}, color, name)


class Sink(FurnitureObj):
    def __init__(self, width=2, height=2, color='blue', name='sink'):
        super(Sink, self).__init__('sink', width, height, {0}, color, name, can_contain={0}, can_overlap=False, can_seebehind=True)


class Sofa(FurnitureObj):
    def __init__(self, width=3, height=2, color='red', name='sofa'):
        super(Sofa, self).__init__('sofa', width, height, {0}, color, name)


class Stove(FurnitureObj):
    def __init__(self, width=3, height=2, color='grey', name='stove'):
        super(Stove, self).__init__('stove', width, height, {0, 1}, color, name, can_contain={0})


class Table(FurnitureObj):
    def __init__(self, width=3, height=2, color='tan', name='table'):
        super(Table, self).__init__('table', width, height, {1}, color, name)


OBJECT_CLASS = {
    'ashcan': Ashcan,
    'bed': Bed,
    'bin': Bin,
    'box': Box,
    'bucket': Bucket,
    'cabinet': Cabinet,
    'chair': Chair,
    'car': Car,
    'countertop': Countertop,
    'door': Door,
    'electric_refrigerator': ElectricRefrigerator,
    'wall': Wall,
    'shelf': Shelf,
    'shower': Shower,
    'sink': Sink,
    'sofa': Sofa,
    'stove': Stove,
    'table': Table
}
