import numpy as np
from .bddl import ALL_ACTIONS, ACTION_FUNC_MAPPING
from .globals import DIR_TO_VEC


class Agent:
    """
    Base class for agent
    """

    def __init__(self, env, agent_view_size):
        # Initial position of agent
        self.init_pos = None
        self.env = env
        self.view_size = agent_view_size

        # Current position of agent
        self.cur_pos = None
        self.dir = None
        # self.obj = None
        # self.carrying = []

        self.actions = {} # NOTE: dict with key = action_key, value = action class

        for action in ALL_ACTIONS:
            self.actions[action] = ACTION_FUNC_MAPPING[action](env)

    def reset(self):
        self.dir = None
        self.cur_pos = None
        # self.carrying = []

    def copy(self):
        from copy import deepcopy
        agent = {'dir': self.dir,
                 'cur_pos': self.cur_pos}
        return deepcopy(agent)

    def load(self, agent, obj_instances):
        self.dir = agent['dir']
        self.cur_pos = agent['cur_pos']

        # for obj in obj_instances.values():
            # if self.is_carrying(obj):
                # self.carrying.append(obj)

    @property
    def dir_vec(self):
        """
        Get the direction vector for the agent, pointing in the direction
        of forward movement.
        """

        assert 0 <= self.dir < 4
        return DIR_TO_VEC[self.dir]

    @property
    def right_vec(self):
        """
        Get the vector pointing to the right of the agent.
        """

        dx, dy = self.dir_vec
        return np.array((-dy, dx))

    @property
    def front_pos(self):
        """
        Get the position of the cell that is right in front of the agent
        """

        return self.cur_pos + self.dir_vec

    def get_view_coords(self, i, j):
        """
        Translate and rotate absolute grid coordinates (i, j) into the
        agent's partially observable view (sub-grid). Note that the resulting
        coordinates may be negative or outside of the agent's view size.
        """

        ax, ay = self.cur_pos
        dx, dy = self.dir_vec
        rx, ry = self.right_vec

        # Compute the absolute coordinates of the top-left view corner
        sz = self.view_size
        hs = self.view_size // 2
        tx = ax + (dx * (sz-1)) - (rx * hs)
        ty = ay + (dy * (sz-1)) - (ry * hs)

        lx = i - tx
        ly = j - ty

        # Project the coordinates of the object relative to the top-left
        # corner onto the agent's own coordinate system
        vx = (rx*lx + ry*ly)
        vy = -(dx*lx + dy*ly)

        return vx, vy

    def relative_coords(self, x, y):
        """
        Check if a grid position belongs to the agent's field of view, and returns the corresponding coordinates
        """

        vx, vy = self.get_view_coords(x, y)

        if vx < 0 or vy < 0 or vx >= self.view_size or vy >= self.view_size:
            return None

        return vx, vy


    def get_view_exts(self):
        """
        Get the extents of the square set of tiles visible to the agent
        Note: the bottom extent indices are not included in the set
        """

        # Facing right
        if self.dir == 0:
            topX = self.cur_pos[0]
            topY = self.cur_pos[1] - self.view_size // 2
        # Facing down
        elif self.dir == 1:
            topX = self.cur_pos[0] - self.view_size // 2
            topY = self.cur_pos[1]
        # Facing left
        elif self.dir == 2:
            topX = self.cur_pos[0] - self.view_size + 1
            topY = self.cur_pos[1] - self.view_size // 2
        # Facing up
        elif self.dir == 3:
            topX = self.cur_pos[0] - self.view_size // 2
            topY = self.cur_pos[1] - self.view_size + 1
        else:
            assert False, "invalid agent direction"

        botX = topX + self.view_size
        botY = topY + self.view_size

        return topX, topY, botX, botY

    def in_view(self, x, y):
        """
        check if a grid position is visible to the agent
        """
        return self.relative_coords(x, y) is not None

    # NEW
    # def reachable(self, obj):
    #     # true if the agent can reach the object
    #     carrying = self.is_carrying(obj)
    #     in_front = np.all(obj.cur_pos == self.front_pos)
    #     return carrying or in_front

    def all_reachable(self):
        return [obj for obj in self.env.obj_instances.values() if obj.states['inreachofrobot'].get_value(self.env)]

    # NEW
    def is_carrying(self, obj):
        return np.all(obj.cur_pos == [-1, -1])
