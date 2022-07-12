from .rendering import *
from .bddl import *
import numpy as np
from .globals import COLOR_TO_IDX, IDX_TO_COLOR, OBJECT_TO_IDX, IDX_TO_OBJECT, COLORS

_DEFAULT_STATES = ['onfloor', 'ontop', 'inside']  # , 'inroom']

_STATE_FUNC_MAPPING = {
    'onfloor': Onfloor,
    'agentcarrying': Agentcarrying,
    'ontop': Ontop,
    'inside': Inside,
    # 'inroom': Inroom,
    'contains': Contains,
    'overlap': Overlap,
    'seebehind': Seebehind,
}
_ACTION_FUNC_MAPPING = {
    'pickup': Pickup,
    'drop': Drop
}

_DEFAULT_ACTIONS = []


class WorldObj:
    """
    Base class for grid world objects
    """

    def __init__(self, type, color, name=None, state_keys=[], action_keys=[]):
        assert type in OBJECT_TO_IDX, type
        assert color in COLOR_TO_IDX, color
        self.type = type
        self.color = color
        self.contains = None

        # Initial position of the object
        self.init_pos = None

        # Current position of the object
        self.cur_pos = None

        # Name of the object (type_number)
        self.name = name

        # is the agent carrying this
        self.agent_carry = False

        # TODO: define self.states and write a loop to initialize all states
        self.state_keys = _DEFAULT_STATES + state_keys
        self.states = {}

        for key in self.state_keys:
            self.states[key] = _STATE_FUNC_MAPPING[key](self)

        self.action_keys = _DEFAULT_ACTIONS + action_keys
        self.actions = {}
        for key in self.action_keys:
            self.actions[key] = _ACTION_FUNC_MAPPING[key](self)

    def possible_action(self, env, action):
        return action in self.action_keys and self.actions[action].can(env)

    def possible_state(self, state):
        return state in self.state_keys

    def check_abs_state(self, env, state):
        return state in self.state_keys and self.states[state].get_value(env)

    def check_static_state(self, env, state):
        return state in self.state_keys and self.states[state].get_value()

    def check_rel_state(self, env, other, state):
        return state in self.state_keys and self.states[state].get_value(other, env)

    def toggle(self, env, pos):
        """Method to trigger/toggle an action this object performs"""
        return False

    def encode(self):
        """Encode the a description of this object as a 3-tuple of integers"""
        return OBJECT_TO_IDX[self.type], COLOR_TO_IDX[self.color], 0

    @staticmethod
    def decode(type_idx, color_idx, state):
        """Create an object from a 3-tuple state description"""

        obj_type = IDX_TO_OBJECT[type_idx]
        color = IDX_TO_COLOR[color_idx]

        if obj_type == 'empty' or obj_type == 'unseen':
            return None

        if obj_type == 'door':
            # State, 0: open, 1: closed, 2: locked
            is_open = state == 0
            is_locked = state == 2
            v = Door(color, is_open, is_locked)
        else:
            OBJ_TYPE_DICT = {
                'wall': Wall,
                'floor': Floor,
                'ball': Ball,
                'key': Key,
                'box': Box,
                'goal': Goal,
                'counter': Counter,
                's_ball': S_ball,
                'ashcan': Ashcan
            }

            v = OBJ_TYPE_DICT[obj_type](color)

        return v

    def render(self, r):
        """Draw this object with the given renderer"""
        raise NotImplementedError


class Goal(WorldObj):
    def __init__(self):
        super().__init__('goal', 'green')

    def render(self, img):
        fill_coords(img, point_in_rect(0, 1, 0, 1), COLORS[self.color])


class Floor(WorldObj):
    """
    Colored floor tile the agent can walk over
    """

    def __init__(self, color='blue'):
        super().__init__('floor', color)

    def can_overlap(self):
        return True

    def render(self, img):
        # Give the floor a pale color
        color = COLORS[self.color] / 2
        fill_coords(img, point_in_rect(0.031, 1, 0.031, 1), color)


# NEW
# TODO: check cannot pickup counter
class Counter(WorldObj):
    """
    Colored floor tile the agent can walk over
    """

    def __init__(self, color='purple', name='counter'):
        super(Counter, self).__init__('counter', color, name)

    def render(self, img):
        fill_coords(img, point_in_rect(0, 1, 0, 1), COLORS[self.color])


class Lava(WorldObj):
    def __init__(self, state_keys=set('overlap')):
        super().__init__('lava', 'red')

    def render(self, img):
        c = (255, 128, 0)

        # Background color
        fill_coords(img, point_in_rect(0, 1, 0, 1), c)

        # Little waves
        for i in range(3):
            ylo = 0.3 + 0.2 * i
            yhi = 0.4 + 0.2 * i
            fill_coords(img, point_in_line(0.1, ylo, 0.3, yhi, r=0.03), (0,0,0))
            fill_coords(img, point_in_line(0.3, yhi, 0.5, ylo, r=0.03), (0,0,0))
            fill_coords(img, point_in_line(0.5, ylo, 0.7, yhi, r=0.03), (0,0,0))
            fill_coords(img, point_in_line(0.7, yhi, 0.9, ylo, r=0.03), (0,0,0))


class Wall(WorldObj):
    def __init__(self, color='grey'):
        super().__init__('wall', color=color, state_keys=['seebehind'])

    def render(self, img):
        fill_coords(img, point_in_rect(0, 1, 0, 1), COLORS[self.color])


class Door(WorldObj):
    def __init__(self, color, is_open=False, is_locked=False):
        super().__init__('door', color, state_keys=['seebehind', 'overlap'])
        self.is_open = is_open
        self.is_locked = is_locked

    def toggle(self, env, pos):
        # If the player has the right key to open the door
        if self.is_locked:
            if isinstance(env.carrying, Key) and env.carrying.color == self.color:
                self.is_locked = False
                self.is_open = True
                return True
            return False

        self.is_open = not self.is_open
        return True

    def encode(self):
        """Encode the a description of this object as a 3-tuple of integers"""

        # State, 0: open, 1: closed, 2: locked
        if self.is_open:
            state = 0
        elif self.is_locked:
            state = 2
        elif not self.is_open:
            state = 1

        return (OBJECT_TO_IDX[self.type], COLOR_TO_IDX[self.color], state)

    def render(self, img):
        c = COLORS[self.color]

        if self.is_open:
            fill_coords(img, point_in_rect(0.88, 1.00, 0.00, 1.00), c)
            fill_coords(img, point_in_rect(0.92, 0.96, 0.04, 0.96), (0,0,0))
            return

        # Door frame and door
        if self.is_locked:
            fill_coords(img, point_in_rect(0.00, 1.00, 0.00, 1.00), c)
            fill_coords(img, point_in_rect(0.06, 0.94, 0.06, 0.94), 0.45 * np.array(c))

            # Draw key slot
            fill_coords(img, point_in_rect(0.52, 0.75, 0.50, 0.56), c)
        else:
            fill_coords(img, point_in_rect(0.00, 1.00, 0.00, 1.00), c)
            fill_coords(img, point_in_rect(0.04, 0.96, 0.04, 0.96), (0,0,0))
            fill_coords(img, point_in_rect(0.08, 0.92, 0.08, 0.92), c)
            fill_coords(img, point_in_rect(0.12, 0.88, 0.12, 0.88), (0,0,0))

            # Draw door handle
            fill_coords(img, point_in_circle(cx=0.75, cy=0.50, r=0.08), c)


class Key(WorldObj):
    def __init__(self, color='blue', name='key'):
        super(Key, self).__init__('key', color, name, state_keys=['agentcarrying'], action_keys=['pickup', 'drop'])

    def can_pickup(self):
        return True

    def render(self, img):
        c = COLORS[self.color]

        # Vertical quad
        fill_coords(img, point_in_rect(0.50, 0.63, 0.31, 0.88), c)

        # Teeth
        fill_coords(img, point_in_rect(0.38, 0.50, 0.59, 0.66), c)
        fill_coords(img, point_in_rect(0.38, 0.50, 0.81, 0.88), c)

        # Ring
        fill_coords(img, point_in_circle(cx=0.56, cy=0.28, r=0.190), c)
        fill_coords(img, point_in_circle(cx=0.56, cy=0.28, r=0.064), (0,0,0))


class Ball(WorldObj):
    def __init__(self, color='blue', name='ball'):
        super(Ball, self).__init__('ball', color, name,
                                   state_keys=['agentcarrying'],
                                   action_keys=['pickup', 'drop'])

    def render(self, img):
        fill_coords(img, point_in_circle(0.5, 0.5, 0.4), COLORS[self.color])


# NEW
class S_ball(WorldObj):
    def __init__(self, color='blue', name='s_ball'):
        super(S_ball, self).__init__('s_ball', color, name,
                                     state_keys=['agentcarrying'],
                                     action_keys=['pickup', 'drop'])

    def render(self, img):
        fill_coords(img, point_in_circle(0.5, 0.5, 0.2), COLORS[self.color])


# NEW
class Ashcan(WorldObj):
    def __init__(self, color='green', name='ashcan'):
        super(Ashcan, self).__init__('ashcan', color, name, state_keys=['contains'])

    def render(self, img):
        c = COLORS[self.color]

        # Outline
        fill_coords(img, point_in_rect(0.12, 0.88, 0.12, 0.88), c)
        fill_coords(img, point_in_rect(0.18, 0.82, 0.18, 0.82), (0,0,0))


class Box(WorldObj):
    def __init__(self, color, name=None):
        super(Box, self).__init__('box', color, name,
                                  state_keys=['agentcarrying', 'contains'],
                                  action_keys=['pickup', 'drop'])

    def render(self, img):
        c = COLORS[self.color]

        # Outline
        fill_coords(img, point_in_rect(0.12, 0.88, 0.12, 0.88), c)
        fill_coords(img, point_in_rect(0.18, 0.82, 0.18, 0.82), (0,0,0))

        # Horizontal slit
        fill_coords(img, point_in_rect(0.16, 0.84, 0.47, 0.53), c)

    def toggle(self, env, pos):
        # Replace the box by its contents
        env.grid.set(*pos, self.contains)
        return True
