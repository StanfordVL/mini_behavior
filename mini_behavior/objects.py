import os
import random
from .rendering import *
from mini_behavior.bddl import ABILITIES, DEFAULT_STATES, STATE_FUNC_MAPPING, DEFAULT_ACTIONS, OBJECT_TO_IDX, IDX_TO_OBJECT
from mini_behavior.utils.globals import COLOR_TO_IDX, COLORS, IDX_TO_COLOR, COLOR_NAMES
from mini_behavior.utils.load import load_json

class WorldObj:
    """
    Base class for grid world objects
    """

    def __init__(self,
                 obj_type,
                 color=None,
                 name=None,
                 state_keys=None,
                 action_keys=None,
                 can_contain=False,
                 can_overlap=False,
                 can_seebehind=True,
                 ):

        if action_keys is None:
            object_actions = load_json(os.path.join(os.path.dirname(__file__), 'utils', 'object_actions.json'))
            if obj_type in object_actions.keys():
                action_keys = object_actions[obj_type]
            else:
                action_keys = []
        if state_keys is None:
            object_properties = load_json(os.path.join(os.path.dirname(__file__), 'utils', 'object_properties.json'))
            if obj_type in object_properties.keys():
                state_keys = object_properties[obj_type]
            else:
                state_keys = []

        assert obj_type in OBJECT_TO_IDX, obj_type
        self.type = obj_type

        self.width = 1
        self.height = 1

        # TODO: change this
        icon_path = os.path.join(os.path.dirname(__file__), 'utils', f'object_icons/{self.type}.jpg')
        if os.path.isfile(icon_path):
            self.icon = img_to_array(icon_path)
            self.icon_color = 'white'
        else:
            self.icon = None
            self.icon_color = None

        self.color = random.choice(COLOR_NAMES) if color is None else color
        if color is not None:
            assert self.color in COLOR_TO_IDX, self.color

        # Initial and current position of the object
        self.init_pos = None
        self.cur_pos = None

        # Name of the object: {type}_{number}
        self.name = name

        # Dict of possible states for the object: key=state_name, value=state_class
        self.states = {key: STATE_FUNC_MAPPING[key](self, key) for key in (DEFAULT_STATES + state_keys)}

        # List of actions agent can perform on the object
        self.actions = DEFAULT_ACTIONS + action_keys

        # OBJECT PROPERTIES
        # ALWAYS STATIC
        self.can_contain = can_contain
        # NOT ALWAYS STATIC
        self.can_overlap = can_overlap
        self.can_seebehind = can_seebehind
        self.contains = None
        self.inside_of = None

    def is_furniture(self):
        return isinstance(self, FurnitureObj)
    
    def check_abs_state(self, env=None, state=None):
        if state is not None:
            return state in self.states.keys() and self.states[state].get_value(env)

    def check_rel_state(self, env, other, state):
        return other is not None and state in self.states.keys() and self.states[state].get_value(other, env)

    def get_all_state_values(self, env):
        states = {}
        for state, instance in self.states.items():
            if instance.type == 'absolute':
                name = '{}/{}'.format(self.name, state)
                val = instance.get_value(env)
                states[name] = val
            elif instance.type == 'relative':
                for obj_name, obj_instance in env.obj_instances.items():
                    if state in obj_instance.states:
                        name = '{}/{}/{}'.format(self.name, obj_name, state)
                        val = instance.get_value(obj_instance, env)
                        states[name] = val
        return states

    def get_ability_values(self, env):
        states = {}
        for state, instance in self.states.items():
            if state in ABILITIES:
                val = instance.get_value(env)
                states[state] = val
        return states

    # TODO: test function and clean up
    def load(self, obj, grid, env):
        self.reset()
        self.update_pos(obj.cur_pos)
        self.can_overlap = obj.can_overlap
        self.can_seebehind = obj.can_seebehind

        # TODO: may not need this if statement anymore
        if obj.can_contain:
            cell = grid.get(*obj.cur_pos)
            if isinstance(cell, list):
                cell_names = [obj.name for obj in cell]
                obj_idx = cell_names.index(obj.name)
                for i in range(obj_idx+1, len(cell)):
                    self.contains.add(env.obj_instances[cell_names[i]])

        inside = obj.states['inside'].inside_of
        if inside:
            name = inside.name
            new_inside = env.obj_instances[name]
            self.states['inside'].set_value(new_inside, True)

    def possible_action(self, action):
        # whether the obj is able to have the action performed on it
        return action in self.actions

    def render(self, img):
        """
        render object from icon
        """
        if self.icon is not None:
            fill_coords(img, point_in_icon(img, self.icon), COLORS[self.icon_color])
        else:
            fill_coords(img, point_in_circle(.5, .5, .6), COLORS[self.color])

    def reset(self):
        self.contains = None
        self.cur_pos = None

        # CHANGE
        for state in self.states.values():
            if state.type == 'absolute':
                state.set_value(False)

    def update(self, env):
        """Method to trigger/toggle an action this object performs"""
        pass

    def update_pos(self, cur_pos):
        self.cur_pos = cur_pos
        
    @staticmethod
    def decode(type_idx, color_idx, state):
        """Create an object from a seed 10_3-tuple state description"""

        obj_type = IDX_TO_OBJECT[type_idx]
        color = IDX_TO_COLOR[color_idx]

        if obj_type == 'empty' or obj_type == 'unseen':
            return None

        if obj_type == 'door':
            # State, 0: open, seed 0_2: closed, seed 0_2: locked
            is_open = state == 0
            is_locked = state == 2
            v = Door(color, is_open, is_locked)
        else:
            try:
                v = OBJECT_CLASS[obj_type](color)
            except KeyError:
                v = WorldObj(obj_type, color)

        return v

    def encode(self):
        """Encode the a description of this object as a seed 10_3-tuple of integers"""
        return OBJECT_TO_IDX[self.type], COLOR_TO_IDX[self.color], 0
        
class FurnitureObj(WorldObj):
    def __init__(self,
                 type,
                 width, # in cells
                 height,
                 dims,
                 color,
                 name=None,
                 can_contain=False,
                 can_overlap=False,
                 can_seebehind=True):

        super().__init__(type, color=color, name=name, can_contain=can_contain, can_overlap=can_overlap, can_seebehind=can_seebehind)
        self.width = width
        self.height = height
        self.dims = dims
        self.all_pos = []

    def render_background(self, img):
        fill_coords(img, point_in_rect(0, 1, 0, 1), COLORS[self.color])

    def reset(self):
        super().reset()
        self.all_pos = []

    def update_pos(self, pos):
        self.cur_pos = pos
        self.all_pos = []
        for dx in range(self.width):
            for dy in range(self.height):
                self.all_pos.append((pos[0] + dx, pos[1] + dy))

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
