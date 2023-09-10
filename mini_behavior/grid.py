# MODIFIED FROM MINIGRID REPO
import numpy as np

from .objects import *
from mini_bddl import ABILITIES, FURNATURE_STATES
from gym_minigrid.minigrid import Grid

# Size in pixels of a tile in the full-scale human view
TILE_PIXELS = 32


def is_obj(obj):
    return isinstance(obj, WorldObj)


class BehaviorGrid(Grid):
    """
    Represent a grid and operations on it
    """

    # Static cache of pre-renderer tiles
    tile_cache = {}

    def __init__(self, width, height):
        super().__init__(width, height)

        # 3 Grid Dimension classes
        self.grid = [GridDimension(width, height) for i in range(3)]

        # Parameters related to observation encoding
        self.null_encoding_value = 0
        self.furniture_encoding_length = 4
        self.obj_encoding_length = 8
        self.pixel_dim = 3 * self.obj_encoding_length + self.furniture_encoding_length + 4

        self.walls = []

        self.render_dim = None
        self.state_values = None

    # TODO: fix this
    def load(self, grid, env):
        for x in range(self.width):
            for y in range(self.height):
                cell = grid.get_all_objs(x, y)

                for i in range(3):
                    if cell[0] != 'wall' and cell[0] != 'door':
                        obj = cell[i]
                        new_obj = env.obj_instances[obj.name] if is_obj(obj) else obj
                        env.grid.set(x, y, new_obj, i)

    # TODO: fix
    def add_wall(self, wall, x, y):
        wall.cur_pos = (x, y)
        self.walls.append(wall)
        self.set(x, y, wall)

    def get(self, i, j):
        assert 0 <= i < self.width
        assert 0 <= j < self.height
        return [dim.get(i, j) for dim in self.grid]

    def get_furniture(self, i, j, dim=None):
        if dim is not None:
            return self.grid[dim].get_furniture(i, j)

        for grid in self.grid:
            if grid.get_furniture(i, j) is not None:
                return grid.get_furniture(i, j)

        return None

    def get_obj_dim(self, obj):
        cell = self.get_all_objs(*obj.cur_pos)
        if obj in cell:
            return cell.index(obj)

    def get_obj(self, i, j, dim):
        return self.grid[dim].get_obj(i, j)

    def get_all_objs(self, i, j):
        return [grid.get_obj(i, j) for grid in self.grid]

    def get_dim(self, i, j, dim):
        return self.grid[dim].get(i, j)

    def get_all_items(self, i, j):
        items = []
        for grid in self.grid:
            items += grid.get(i, j)
        return items

    def is_empty(self, i, j):
        return self.get(i, j) == [[None, None] for i in range(3)]

    def remove(self, i, j, v):
        assert 0 <= i < self.width
        assert 0 <= j < self.height
        assert isinstance(v, WorldObj) and not isinstance(v, FurnitureObj)

        cell = self.get_all_objs(i, j)

        assert v in cell, f'trying to remove obj {v} not in cell'

        dim = cell.index(v)
        self.grid[dim].remove(i, j)

    def set(self, i, j, v, dim=0):
        assert 0 <= i < self.width, f'{i}'
        assert 0 <= j < self.height, f'{j}'

        if isinstance(v, FurnitureObj):
            for idx in v.dims:
                self.grid[idx].set(i, j, v)
        elif isinstance(v, set):
            # This means the object is carried by the agent
            # Not sure how we should handle more than three
            for idx, obj in enumerate(v):
                if idx <= 2:
                    self.grid[idx].set(i, j, obj)
        else:
            self.grid[dim].set(i, j, v)

    def set_all_objs(self, i, j, objs):
        assert len(objs) == 3
        for dim in range(3):
            self.grid[dim].set(i, j, objs[dim])

    def set_all_items(self, i, j, objs):
        assert len(objs) == 3
        for dim in range(3):
            for obj in objs[dim]:
                self.grid[dim].set(i, j, obj)

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

    def rotate_left(self):
        """
        Rotate the grid to the left (counter-clockwise)
        """

        grid = BehaviorGrid(self.height, self.width)

        for i in range(self.width):
            for j in range(self.height):
                v = self.get(i, j)
                grid.set_all_items(j, grid.height - 1 - i, v)

        grid.state_values = self.state_values

        return grid

    def slice(self, topX, topY, width, height):
        """
        Get a subset of the grid
        """
        grid = BehaviorGrid(width, height)

        for j in range(0, height):
            for i in range(0, width):
                x = topX + i
                y = topY + j

                if 0 <= x < self.width and 0 <= y < self.height:
                    v = self.get(x, y)
                    grid.set_all_items(i, j, v)
                else:
                    grid.set_all_objs(i, j, [Wall()] * 3)
        grid.state_values = self.state_values

        return grid

    @classmethod
    def render_tile(
        cls,
        furniture,
        objs,
        agent_dir=None,
        highlight=False,
        tile_size=TILE_PIXELS,
        subdivs=3,
    ):
        """
        Render a tile and cache the result
        """

        # if obj is inside closed obj, don't render it
        render_objs = []

        for obj in objs:
            if is_obj(obj):
                if not obj.inside_of or 'openable' not in obj.inside_of.states.keys() or obj.inside_of.check_abs_state(state='openable'):
                    render_objs.append(obj)
                else:
                    render_objs.append(None)
            else:
                render_objs.append(obj)

        # Hash map lookup key for the cache
        key = (agent_dir, highlight, tile_size)
        objs_encoding = [obj.encode() if is_obj(obj) else None for obj in render_objs]
        furniture_encoding = [furniture.encode() if is_obj(furniture) else None]

        key = tuple(furniture_encoding + objs_encoding) + key

        if key in cls.tile_cache:
            return cls.tile_cache[key]

        img = np.zeros(shape=(tile_size * subdivs, tile_size * subdivs, 3), dtype=np.uint8)

        # Draw the grid lines (top and left edges)
        fill_coords(img, point_in_rect(0, 0.031, 0, 1), (100, 100, 100))
        fill_coords(img, point_in_rect(0, 1, 0, 0.031), (100, 100, 100))

        if furniture:
            furniture.render_background(img)

        full, half = np.shape(img)[0], int(np.shape(img)[0] / 2)
        y_coords = [(0, half), (0, half), (half, full)] #, (half, full)]
        x_coords = [(0, half), (half, full), (0, half)] #, (half, full)]

        for i in range(len(render_objs)):
            obj = render_objs[i]

            if is_obj(obj):
                x_1, x_2 = x_coords[i]
                y_1, y_2 = y_coords[i]
                sub_img = img[y_1: y_2, x_1: x_2, :]
                obj.render(sub_img)

        if agent_dir is not None:
            GridDimension.render_agent(img, agent_dir)

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
        highlight_mask=None,
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
                agent_here = np.array_equal(agent_pos, (i, j))
                ymin = j * tile_size
                ymax = (j + 1) * tile_size
                xmin = i * tile_size
                xmax = (i + 1) * tile_size

                if self.render_dim is None:
                    furniture = self.get_furniture(i, j)
                    objs = self.get_all_objs(i, j)

                    img[ymin:ymax, xmin:xmax, :] = BehaviorGrid.render_tile(
                        furniture,
                        objs,
                        agent_dir=agent_dir if agent_here else None,
                        highlight=highlight_mask[i, j],
                        tile_size=tile_size,
                    )
                else:
                    furniture, obj = self.grid[self.render_dim].get(i, j)
                    state_values = self.state_values.get(obj, None)

                    img[ymin:ymax, xmin:xmax, :] = GridDimension.render_tile(
                        furniture,
                        obj,
                        state_values,
                        agent_dir=agent_dir if agent_here else None,
                        highlight=highlight_mask[i, j],
                        tile_size=tile_size,
                        draw_grid_lines=True
                    )

        return img

    def render_furniture(
        self,
        tile_size,
        obj_instances
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

        # render all furniture
        for obj in list(obj_instances.values()) + self.walls:
            if obj.is_furniture():
                i, j = obj.cur_pos
                ymin = j * tile_size
                ymax = (j + obj.height) * tile_size
                xmin = i * tile_size
                xmax = (i + obj.width) * tile_size
                sub_img = img[ymin:ymax, xmin:xmax, :]

                obj.render(sub_img)

        return img

    def state_dict_encoding(self, state_dict, state_list):
        if state_dict is None:
            return [self.null_encoding_value] * len(state_list)
        else:
            states = []
            for state in state_list:
                if state in state_dict:
                    val = state_dict[state]
                    states.append(val)
                else:
                    states.append(self.null_encoding_value)
            return states

    def encode(self, vis_mask=None):
        """
        Produce a compact numpy encoding of the grid
        """

        if vis_mask is None:
            vis_mask = np.ones((self.width, self.height), dtype=bool)

        array = np.zeros((self.width, self.height, self.pixel_dim), dtype='uint8')

        for i in range(self.width):
            for j in range(self.height):
                if vis_mask[i, j]:
                    item_list = []

                    # Process furniture first
                    furniture = self.get_furniture(i, j)
                    if not is_obj(furniture):
                        fur_n = 'empty'
                        state_dict = None
                    else:
                        fur_n = furniture.type
                        if fur_n == "wall" or fur_n == "door":
                            state_dict = None
                        else:
                            state_dict = self.state_values[furniture]
                    item_list.append(np.array([OBJECT_TO_IDX[fur_n]] +
                                              self.state_dict_encoding(state_dict,
                                                                       FURNATURE_STATES)))

                    # A bit hacky, handle door state
                    if fur_n == "door":
                        if not furniture.is_open:
                            item_list[-1][1] = 1

                    objects = self.get_all_objs(i, j)
                    # Next, handle objects
                    for obj in objects:
                        if not is_obj(obj):
                            obj_n = 'empty'
                            state_dict = None
                        else:
                            obj_n = obj.type
                            state_dict = self.state_values[obj]
                        item_list.append(np.array([OBJECT_TO_IDX[obj_n]] +
                                                   self.state_dict_encoding(state_dict,
                                                                            ABILITIES)))

                    array[i, j] = np.concatenate(item_list)

        return array

    @staticmethod
    def decode(array):
        """
        Decode an array grid encoding back into a grid
        """

        width, height, channels = array.shape
        assert channels == 3

        vis_mask = np.ones(shape=(width, height), dtype=bool)

        grid = BehaviorGrid(width, height)
        for i in range(width):
            for j in range(height):
                type_idx, color_idx, state = array[i, j]
                v = WorldObj.decode(type_idx, color_idx, state)
                grid.set(i, j, v)
                vis_mask[i, j] = (type_idx != OBJECT_TO_IDX['unseen'])

        return grid, vis_mask

    # # TODO: fix
    def process_vis(grid, agent_pos):
        return np.ones(shape=(grid.width, grid.height), dtype=bool)


class GridDimension(Grid):
    """
    Represent a grid and operations on it
    """

    # Static cache of pre-renderer tiles
    tile_cache = {}

    def __init__(self, width, height):
        super().__init__(width, height)
        self.grid = [[None, None] for i in range(width * height)]

    # TODO: check this works
    def load(self, grid, env):
        for x in range(self.width):
            for y in range(self.height):
                furniture, obj = grid.get(x, y)

                if obj != 'wall' and obj != 'door':
                    new_obj = env.obj_instances[obj.name] if is_obj(obj) else obj
                    env.grid.set(x, y, new_obj)

    def get_furniture(self, i, j):
        assert 0 <= i < self.width
        assert 0 <= j < self.height
        return self.grid[j * self.width + i][0]

    def get_obj(self, i, j):
        assert 0 <= i < self.width
        assert 0 <= j < self.height
        return self.grid[j * self.width + i][1]

    def remove(self, i, j):
        assert 0 <= i < self.width
        assert 0 <= j < self.height
        self.grid[j * self.width + i][1] = None

    def set(self, i, j, v):
        assert 0 <= i < self.width, f'{i}'
        assert 0 <= j < self.height, f'{j}'

        if isinstance(v, FurnitureObj):
            self.grid[j * self.width + i][0] = v
        else:
            self.grid[j * self.width + i][1] = v

    def rotate_left(self):
        """
        Rotate the grid to the left (counter-clockwise)
        """

        grid = GridDimension(self.height, self.width)

        for i in range(self.width):
            for j in range(self.height):
                v = self.get(i, j)
                grid.set(j, grid.height - 1 - i, v)

        return grid

    def slice(self, topX, topY, width, height):
        """
        Get a subset of the grid
        """

        grid = GridDimension(width, height)

        for j in range(0, height):
            for i in range(0, width):
                x = topX + i
                y = topY + j

                if 0 <= x < self.width and 0 <= y < self.height:
                    furniture, obj = self.get(x, y)
                    grid.set(i, j, furniture)
                    grid.set(i, j, obj)
                else:
                    grid.set(i, j, Wall())

        return grid

    # TODO: maybe delete
    @classmethod
    def render_agent(cls, img, agent_dir):
        tri_fn = point_in_triangle(
            (0.12, 0.19),
            (0.87, 0.50),
            (0.12, 0.81),
        )

        # Rotate the agent based on its direction
        tri_fn = rotate_fn(tri_fn, cx=0.5, cy=0.5, theta=0.5 * math.pi * agent_dir)
        fill_coords(img, tri_fn, (255, 0, 0))

        return img

    @classmethod
    def render_tile(
        cls,
        furniture,
        obj,
        state_values=None,
        agent_dir=None,
        highlight=False,
        tile_size=TILE_PIXELS,
        subdivs=3,
        draw_grid_lines=True
    ):
        """
        Render a tile and cache the result
        """
        # assert not is_obj(obj) or state_values is not None, 'no states passed in for obj'
        obj_size = int(tile_size * 7 / 8)

        # if obj is inside closed obj, don't render it
        if is_obj(obj) and obj.inside_of and 'openable' in obj.inside_of.states.keys() and not obj.inside_of.check_abs_state(state='openable'):
            obj = None

        # Hash map lookup key for the cache
        obj_encoding = obj.encode() if is_obj(obj) else None
        furniture_encoding = furniture.encode() if is_obj(furniture) else None

        key = (furniture_encoding, obj_encoding, agent_dir, highlight, tile_size, draw_grid_lines)

        if key in cls.tile_cache:
            img = cls.tile_cache[key]
        else:
            img = np.zeros(shape=(tile_size * subdivs, tile_size * subdivs, 3), dtype=np.uint8)

            # Draw the grid lines (top and left edges)
            if draw_grid_lines:
                fill_coords(img, point_in_rect(0, 0.031, 0, 1), (100, 100, 100))
                fill_coords(img, point_in_rect(0, 1, 0, 0.031), (100, 100, 100))

            if furniture:
                furniture.render_background(img)

            # render obj and all false states
            if is_obj(obj):
                obj_img = img[: obj_size * 3, : obj_size * 3, :]
                obj.render(obj_img)

            if agent_dir is not None:
                GridDimension.render_agent(img, agent_dir)

            # Highlight the cell if needed
            if highlight:
                highlight_img(img)

            # Downsample the image to perform supersampling/anti-aliasing
            img = downsample(img, subdivs)

            # Cache the rendered tile
            cls.tile_cache[key] = img.astype(np.uint8)

        if is_obj(obj):
            img[:, obj_size:, :] = cls.render_obj_states(state_values, highlight, tile_size)

        return img.astype(np.uint8)

    @classmethod
    def render_obj_states(cls, state_values, highlight=False, tile_size=TILE_PIXELS):
        num = len(ABILITIES)
        img = np.zeros(shape=(tile_size, int(tile_size / num), 3), dtype=np.uint8)

        for i in range(len(ABILITIES)):
            state = ABILITIES[i]

            y_min = int(i * tile_size / len(ABILITIES))
            y_max = int((i + 1) * tile_size / len(ABILITIES))
            sub_img = img[y_min: y_max, :, :]

            if state_values and state_values.get(state, False):
                fill_coords(sub_img, point_in_rect(0.15, 1, 0.15, 1), COLORS['green'])
            else:
                fill_coords(sub_img, point_in_rect(0.15, 1, 0.15, 1), (255, 204, 203))

        # Highlight the cell if needed
        if highlight:
            highlight_img(img)

        return img

    @classmethod
    def render_furniture_states(cls, img, state_values):
        if state_values.get('dustyable', False):
            fill_coords(img, point_in_rect(0, 0.05, 0, 1), [0, 255, 0])
        if state_values.get('openable', False):
            fill_coords(img, point_in_rect(0, 1, 0, 0.05), [0, 255, 0])
        if state_values.get('stainable', False):
            fill_coords(img, point_in_rect(0.95, 1, 0, 1), [0, 255, 0])
        if state_values.get('toggleable', False):
            fill_coords(img, point_in_rect(0, 1, 0.95, 1), [0, 255, 0])

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
                    v = self.get(i, j)

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

        grid = GridDimension(width, height)
        for i in range(width):
            for j in range(height):
                type_idx, color_idx, state = array[i, j]
                v = WorldObj.decode(type_idx, color_idx, state)
                grid.set(i, j, v)
                vis_mask[i, j] = (type_idx != OBJECT_TO_IDX['unseen'])

        return grid, vis_mask
