import os
from mini_behavior.rendering import *
from bddl import DEFAULT_STATES, STATE_FUNC_MAPPING, DEFAULT_ACTIONS, OBJECT_TO_IDX, IDX_TO_OBJECT, OBJECTS, ABILITIES
from .globals import COLOR_TO_IDX, IDX_TO_COLOR, COLORS
from .load import load_json


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
            object_actions = load_json(os.path.join(os.path.dirname(__file__), 'object_actions.json'))
            if obj_type in object_actions.keys():
                action_keys = object_actions[obj_type]
            else:
                action_keys = []
        if state_keys is None:
            object_properties = load_json(os.path.join(os.path.dirname(__file__), 'object_properties.json'))
            if obj_type in object_properties.keys():
                state_keys = object_properties[obj_type]
            else:
                state_keys = []

        assert obj_type in OBJECT_TO_IDX, obj_type
        self.type = obj_type

        self.width = 1
        self.height = 1

        # TODO: change this
        if obj_type in OBJECTS:
            icon_path = os.path.join(os.path.dirname(__file__), f'../utils/object_icons/{self.type}.jpg')
            self.icon = img_to_array(icon_path)
        else:
            self.icon = None

        self.color = 'white' if color is None else color
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

    def check_abs_state(self, env=None, state=None):
        if state is not None:
            return state in self.states.keys() and self.states[state].get_value(env)

    def check_rel_state(self, env, other, state):
        return other is not None and state in self.states.keys() and self.states[state].get_value(other, env)

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
            v = OBJECT_CLASS[obj_type](color)

        return v

    def encode(self):
        """Encode the a description of this object as a seed 10_3-tuple of integers"""
        return OBJECT_TO_IDX[self.type], COLOR_TO_IDX[self.color], 0

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
        return states2

    def get_ability_values(self, env):
        states = {}
        for state, instance in self.states.items():
            if state in ABILITIES:
                val = instance.get_value(env)
                states[state] = val
        return states

    def is_furniture(self):
        return isinstance(self, FurnitureObj)

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
        fill_coords(img, point_in_icon(img, self.icon), [255, 255, 255])

    def reset(self):
        self.contains = None
        self.cur_pos = None

    def update(self, env):
        """Method to trigger/toggle an action this object performs"""
        pass

    def update_pos(self, cur_pos):
        self.cur_pos = cur_pos


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
        fill_coords(img, point_in_rect(0.031, 1, 0.031, 1), COLORS[self.color])

    def reset(self):
        super().reset()
        self.all_pos = []

    def update_pos(self, pos):
        self.cur_pos = pos
        self.all_pos = []
        for dx in range(self.width):
            for dy in range(self.height):
                self.all_pos.append((pos[0] + dx, pos[1] + dy))
