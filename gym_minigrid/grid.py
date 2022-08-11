# MODIFIED FROM MINIGRID REPO
from .objects import *
from .bddl import FURNITURE

# Size in pixels of a tile in the full-scale human view
TILE_PIXELS = 32


def is_obj(obj):
    return obj is not None and type(obj) != bool


class Grid:
    """
    Represent a grid and operations on it
    """

    # Static cache of pre-renderer tiles
    tile_cache = {}

    def __init__(self, width, height):
        assert width >= 3
        assert height >= 3

        self.width = width
        self.height = height

        self.grid = [[None, None, False, None] for i in range(width * height)]
        self.walls = []

    def __contains__(self, key):
        if isinstance(key, WorldObj):
            for e in self.grid:
                if e is key:
                    return True
        elif isinstance(key, tuple):
            for e in self.grid:
                if e is None:
                    continue
                if (e.color, e.type) == key:
                    return True
                if key[0] is None and key[1] == e.type:
                    return True
        return False

    def __eq__(self, other):
        grid1 = self.encode()
        grid2 = other.encode()
        return np.array_equal(grid2, grid1)

    def __ne__(self, other):
        return not self == other

    def copy(self):
        from copy import deepcopy
        return deepcopy(self)

    def load(self, grid, env):
        for x in range(self.width):
            for y in range(self.height):
                cell = grid.get_all_dims(x, y)

                for i in range(4):
                    if cell[0] != 'wall' and cell[0] != 'door':
                        obj = cell[i]
                        new_obj = env.obj_instances[obj.name] if is_obj(obj) else obj
                        env.grid.set(x, y, new_obj, i)

    def add_wall(self, wall, x, y):
        wall.cur_pos = (x, y)
        self.set(x, y, wall)
        self.walls.append(wall)

    def get(self, i, j):
        assert 0 <= i < self.width
        assert 0 <= j < self.height
        return [obj for obj in self.grid[j * self.width + i] if is_obj(obj)]

    def get_all_dims(self, i, j):
        return self.grid[j * self.width + i]

    def get_dim(self, i, j, dim):
        return self.grid[j * self.width + i][dim]

    def remove(self, i, j, v):
        assert 0 <= i < self.width
        assert 0 <= j < self.height

        cell = self.get_all_dims(i, j)

        if v in cell:
            idx = cell.index(v)
            self.grid[j * self.width + i][idx] = None

            if idx == 0:
                for block_idx in v.block_idxs():
                    self.grid[j * self.width + i][block_idx] = None
                self.grid[j * self.width + i][2] = False

    def set(self, i, j, v, set_idx=0):
        assert 0 <= i < self.width, f'{i}'
        assert 0 <= j < self.height, f'{j}'

        self.grid[j * self.width + i][set_idx] = v

        if is_obj(v) and set_idx == 0:
            if v.can_contain:
                self.grid[j * self.width + i][2] = None
            for idx in v.block_idxs():
                self.grid[j * self.width + i][idx] = False

    def set_all_dims(self, i, j, objs):
        if len(objs) == 4:
            self.grid[j * self.width + i] = objs

    def horz_wall(self, x, y, length=None, obj_type=Wall):
        if length is None:
            length = self.width - x
        for i in range(0, length):
            self.add_wall(obj_type(), x + i, y)

    def vert_wall(self, x, y, length=None, obj_type=Wall):
        if length is None:
            length = self.height - y
        for j in range(0, length):
            self.add_wall(obj_type(), x, y + j)

    def wall_rect(self, x, y, w, h):
        self.horz_wall(x, y, w)
        self.horz_wall(x, y+h-1, w)
        self.vert_wall(x, y, h)
        self.vert_wall(x+w-1, y, h)

    def rotate_left(self):
        """
        Rotate the grid to the left (counter-clockwise)
        """

        grid = Grid(self.height, self.width)

        for i in range(self.width):
            for j in range(self.height):
                v = self.get_all_dims(i, j)
                grid.set_all_dims(j, grid.height - 1 - i, v)

        return grid

    def slice(self, topX, topY, width, height):
        """
        Get a subset of the grid
        """

        grid = Grid(width, height)

        for j in range(0, height):
            for i in range(0, width):
                x = topX + i
                y = topY + j

                if 0 <= x < self.width and 0 <= y < self.height:
                    v = self.get_all_dims(x, y)
                    grid.set_all_dims(i, j, v)
                else:
                    v = Wall()
                    grid.set(i, j, v)

        return grid

    def render_agent(self, img, agent_pos=None, agent_dir=None, tile_size=TILE_PIXELS):
        if agent_dir is not None:
            tri_fn = point_in_triangle(
                (0.12, 0.19),
                (0.87, 0.50),
                (0.12, 0.81),
            )

        i, j = agent_pos
        ymin = j * tile_size
        ymax = (j + 1) * tile_size
        xmin = i * tile_size
        xmax = (i + 1) * tile_size
        sub_img = img[ymin:ymax, xmin:xmax, :]

        # Rotate the agent based on its direction
        tri_fn = rotate_fn(tri_fn, cx=0.5, cy=0.5, theta=0.5 * math.pi * agent_dir)
        fill_coords(sub_img, tri_fn, (255, 0, 0))

        return img

    @classmethod
    def render_tile(
        cls,
        objs,
        agent_dir=None,
        highlight=False,
        tile_size=TILE_PIXELS,
        subdivs=3,
    ):
        """
        Render a tile and cache the result
        """

        # Hash map lookup key for the cache
        key = (agent_dir, highlight, tile_size)

        keys = [obj.encode() for obj in objs if is_obj(obj)]
        key = tuple(keys) + key

        if key in cls.tile_cache:
            return cls.tile_cache[key]

        img = np.zeros(shape=(tile_size * subdivs, tile_size * subdivs, 3), dtype=np.uint8)

        # Draw the grid lines (top and left edges)
        fill_coords(img, point_in_rect(0, 0.031, 0, 1), (100, 100, 100))
        fill_coords(img, point_in_rect(0, 1, 0, 0.031), (100, 100, 100))

        if is_obj(objs[0]) and objs[0].type == 'wall':
            objs[0].render(img)
        else:
            if is_obj(objs[0]) and objs[0].is_furniture():
                objs[0].render_background(img)
            objs = [obj for obj in objs if is_obj(obj) and not obj.is_furniture()]

            if len(objs) == 1:
                objs[0].render(img)
            else:
                # split up the cell for multiple objs
                full, half = np.shape(img)[0], int(np.shape(img)[0] / 2)
                y_coords = [(0, half), (0, half), (half, full), (half, full)]
                x_coords = [(0, half), (half, full), (0, half), (half, full)]

                for i in range(len(objs)):
                    obj = objs[i]
                    x_1, x_2 = x_coords[i]
                    y_1, y_2 = y_coords[i]
                    sub_img = img[y_1: y_2, x_1: x_2, :]
                    obj.render(sub_img)

        if agent_dir is not None:
            tri_fn = point_in_triangle(
                (0.12, 0.19),
                (0.87, 0.50),
                (0.12, 0.81),
            )

            # Rotate the agent based on its direction
            tri_fn = rotate_fn(tri_fn, cx=0.5, cy=0.5, theta=0.5*math.pi*agent_dir)
            fill_coords(img, tri_fn, (255, 0, 0))

        # Highlight the cell if needed
        if highlight:
            highlight_img(img)

        # Downsample the image to perform supersampling/anti-aliasing
        img = downsample(img, subdivs)

        # Cache the rendered tile
        cls.tile_cache[key] = img

        return img

    def render(
        self,
        tile_size,
        agent_pos=None,
        agent_dir=None,
        highlight_mask=None
    ):
        """
        Render this grid at a given scale
        :param r: target renderer object
        :param tile_size: tile size in pixels
        """

        if highlight_mask is None:
            highlight_mask = np.zeros(shape=(self.width, self.height), dtype=bool)

        # Compute the total grid size
        width_px = self.width * tile_size
        height_px = self.height * tile_size

        img = np.zeros(shape=(height_px, width_px, 3), dtype=np.uint8)

        # Render the grid
        for j in range(0, self.height):
            for i in range(0, self.width):
                cell = self.get_all_dims(i, j)

                agent_here = np.array_equal(agent_pos, (i, j))
                ymin = j * tile_size
                ymax = (j + 1) * tile_size
                xmin = i * tile_size
                xmax = (i + 1) * tile_size
                img[ymin:ymax, xmin:xmax, :] = Grid.render_tile(
                    cell,
                    agent_dir=agent_dir if agent_here else None,
                    highlight=highlight_mask[i, j],
                    tile_size=tile_size,
                )

        return img

    def render_furniture(
        self,
        tile_size,
        objs
    ):
        # Compute the total grid size
        width_px = self.width * tile_size
        height_px = self.height * tile_size

        img = np.zeros(shape=(height_px, width_px, 3), dtype=np.uint8)

        # Render the grid
        for j in range(0, self.height):
            for i in range(0, self.width):
                ymin = j * tile_size
                ymax = (j+1) * tile_size
                xmin = i * tile_size
                xmax = (i+1) * tile_size

                sub_img = img[ymin:ymax, xmin:xmax, :]

                # Draw the grid lines (top and left edges)
                fill_coords(sub_img, point_in_rect(0, 0.031, 0, 1), (100, 100, 100))
                fill_coords(sub_img, point_in_rect(0, 1, 0, 0.031), (100, 100, 100))

        layout = self.walls
        for obj_type in objs.keys():
            if obj_type in FURNITURE:
                layout += objs[obj_type]

        # render all furniture + walls
        for obj in layout:
            i, j = obj.cur_pos
            ymin = j * tile_size
            ymax = (j + obj.height) * tile_size
            xmin = i * tile_size
            xmax = (i + obj.width) * tile_size
            sub_img = img[ymin:ymax, xmin:xmax, :]

            obj.render(sub_img)

        return img

    def encode(self, vis_mask=None):
        """
        Produce a compact numpy encoding of the grid
        """

        if vis_mask is None:
            vis_mask = np.ones((self.width, self.height), dtype=bool)

        array = np.zeros((self.width, self.height, 3), dtype='uint8')

        for i in range(self.width):
            for j in range(self.height):
                if vis_mask[i, j]:
                    v = self.get_all_dims(i, j)

                    for obj in v:
                        if is_obj(obj):
                            encoding = obj.encode()
                        else:
                            encoding = np.array([OBJECT_TO_IDX['empty'], 0, 0])
                        array[i, j, :] = np.add(array[i, j, :], encoding)

        return array

    @staticmethod
    def decode(array):
        """
        Decode an array grid encoding back into a grid
        """

        width, height, channels = array.shape
        assert channels == 3

        vis_mask = np.ones(shape=(width, height), dtype=bool)

        grid = Grid(width, height)
        for i in range(width):
            for j in range(height):
                type_idx, color_idx, state = array[i, j]
                v = WorldObj.decode(type_idx, color_idx, state)
                grid.set(i, j, v)
                vis_mask[i, j] = (type_idx != OBJECT_TO_IDX['unseen'])

        return grid, vis_mask

    def process_vis(grid, agent_pos):
        # agent_pos=(self.agent.view_size // 2 , self.agent.view_size - 1)
        return np.ones(shape=(grid.width, grid.height), dtype=bool)

        # TODO: fix
        mask = np.zeros(shape=(grid.width, grid.height), dtype=bool)

        mask[agent_pos[0], agent_pos[1]] = True

        for j in reversed(range(0, grid.height)):
            for i in range(0, grid.width-1):
                if not mask[i, j]:
                    continue

                cell = grid.get(i, j)
                vis = True

                for obj in cell:
                    if not obj.can_seebehind:
                        vis = False
                        break

                if not vis:
                    continue

                mask[i+1, j] = True
                if j > 0:
                    mask[i+1, j-1] = True
                    mask[i, j-1] = True

            for i in reversed(range(1, grid.width)):
                if not mask[i, j]:
                    continue

                cell = grid.get(i, j)
                vis = True

                for obj in cell:
                    if not obj.can_seebehind:
                        vis = False
                        break

                if not vis:
                    continue

                mask[i-1, j] = True
                if j > 0:
                    mask[i-1, j-1] = True
                    mask[i, j-1] = True

        for j in range(0, grid.height):
            for i in range(0, grid.width):
                if not mask[i, j]:
                    grid.set_all_dims(i, j, [None, None, None, None])
        return mask
