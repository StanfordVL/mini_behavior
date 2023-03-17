# MODIFIED FROM MINIGRID REPO
from .objects import *
from mini_behavior.bddl import ABILITIES
from gym_minigrid.minigrid import Grid
import cv2
# Size in pixels of a tile in the full-scale human view
TILE_PIXELS = 32


def is_obj(obj):
    return isinstance(obj, WorldObj)


class Cell:
    def __init__(self, furniture=None, objs=None):
        self.wall = None
        self.furniture = furniture
        self.objs = [] if objs is None else objs

    def add_at_dim(self, obj, d):
        if d < len(self.objs):
            if self.objs[d] is None:
                self.objs[d] = obj
            else:
                self.objs.insert(d, obj)
        else:
            for _ in range(len(self.objs) - d):
                self.objs.append(None)
            self.objs.append(obj)

    def add_wall(self, wall):
        if self.wall is None:
            assert self.furniture is None and self.objs == []
        self.wall = wall
        self.furniture = wall
        self.objs = None

    def add_furniture(self, obj):
        assert self.wall is None
        self.furniture = obj

        for dim in obj.dims:
            self.add_at_dim(obj, dim)
            # TODO: block out

    def add_obj(self, obj, dim=0):
        assert self.wall is None
        self.add_at_dim(obj, dim)

    def reset(self):
        self.wall = None
        self.furniture = None
        self.objs = []


class BehaviorGrid(Grid):
    """
    Represent a grid and operations on it
    """
    # Static cache of pre-renderer tiles
    tile_cache = {}

    def __init__(self, width, height):
        super().__init__(width, height)
        self.grid = [Cell() for _ in range(width * height)]

        self.walls = []

        self.render_dim = None
        self.state_values = None

    # TODO: check this works
    def load(self, grid, env):
        for x in range(self.width):
            for y in range(self.height):
                furniture, objs = grid.get(x, y)

                # if obj != 'wall' and obj != 'door':
                #     new_obj = env.obj_instances[obj.name] if is_obj(obj) else obj
                #     env.grid.set(x, y, new_obj)

    # TODO: fix
    def add_wall(self, wall, x, y):
        cell = self.get(x, y)
        if cell.wall is None:
            wall.cur_pos = (x, y)
            self.walls.append(wall)
            self.set(x, y, wall)

    def get_maze(self):
        maze = []

        for i in range(self.height):
            row = []
            for j in range(self.width):
                cell = 0 if self.is_empty(j, i)  else 1
                row.append(cell)
            maze.append(row)

        return maze


    def get_furniture(self, i, j):
        cell = self.get(i,j)
        return cell.furniture

    def get_obj_dim(self, obj):
        cell = self.get(*obj.cur_pos)
        if obj in cell.objs:
            return cell.objs.index(obj)

    def get_all_objs(self, i, j):
        cell = self.get(i, j)
        objs = [] if cell.objs is None else cell.objs
        # print(f"Processing {len(objs)}")
        return [obj for obj in objs if obj is not None and not isinstance(obj, FurnitureObj)]

    def get_all_items(self, i, j):
        cell = self.get(i, j)
        all_items = [cell.wall, cell.furniture] + cell.objs
        return [obj for obj in all_items if obj is not None]

    def is_empty(self, i, j):
        cell = self.get(i,j)
        if cell.furniture is not None:
            return False
        for obj in cell.objs:
            if obj is not None:
                return False
        return True

    def remove(self, i, j, v):
        assert 0 <= i < self.width
        assert 0 <= j < self.height
        assert isinstance(v, WorldObj) and not isinstance(v, FurnitureObj)

        cell = self.get(i, j)
        assert v in cell.objs, f'trying to remove obj {v} not in cell'
        # dim = cell.objs.index(v)
        # cell.objs[dim] = None
        cell.objs.remove(v)
        v.cur_pos = None
        assert v not in cell.objs

    # TODO: fix set
    def set(self, i, j, v, dim=0):
        assert 0 <= i < self.width, f'{i}'
        assert 0 <= j < self.height, f'{j}'

        cell = self.get(i, j)

        if isinstance(v, Wall) or isinstance(v, Door):
            cell.add_wall(v)
        elif isinstance(v, FurnitureObj):
            for pos in v.all_pos:
                cell = self.get(*pos)
                cell.add_furniture(v)
        elif isinstance(v, WorldObj):
            cell.add_obj(v, dim)

    def set_all_objs(self, i, j, objs):
        cell = self.get(i, j)
        cell.objs = objs

    def horz_wall(self, x, y, length=None, obj_type=Wall, color='grey'):
        if length is None:
            length = self.width - x
        for i in range(0, length):
            self.add_wall(obj_type(color=color), x + i, y)

    def vert_wall(self, x, y, length=None, obj_type=Wall, color='grey'):
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
                v = self.get_all_objs(i, j)
                grid.set_all_objs(j, grid.height - 1 - i, v)

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
                    v = self.get_all_objs(x, y)
                    grid.set_all_objs(i, j, v)
                else:
                    grid.set_all_objs(i, j, [Wall()] * 3)

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

        for obj in [v for v in objs if not isinstance(v, FurnitureObj)]:
            if is_obj(obj):
                if not obj.inside_of or 'openable' not in obj.inside_of.states.keys() or obj.inside_of.check_abs_state(state='openable'):
                    render_objs.append(obj)
                # else:
                #     render_objs.append(None)
            # else:
            #     render_objs.append(obj)

        # Hash map lookup key for the cache
        key = (agent_dir, highlight, tile_size)
        objs_encoding = [obj.encode() if is_obj(obj) else None for obj in render_objs]
        furniture_encoding = [furniture.encode() if is_obj(furniture) else None]

        key = tuple(furniture_encoding + objs_encoding) + key

        # TODO: should be uncommented
        if key in cls.tile_cache:
            return cls.tile_cache[key]

        img = np.zeros(shape=(tile_size * subdivs, tile_size * subdivs, 3), dtype=np.uint8)

        # # Draw the grid lines (top and left edges)
        fill_coords(img, point_in_rect(0, 0.031, 0, 1), (100, 100, 100))
        fill_coords(img, point_in_rect(0, 1, 0, 0.031), (100, 100, 100))

        if furniture:
            furniture.render_background(img)

        full, half = np.shape(img)[0], int(np.shape(img)[0] / 2)
        y_coords = [(0, half), (0, half), (half, full), (half, full)]
        x_coords = [(0, half), (half, full), (0, half), (half, full)]

        for i in range(len(render_objs)):
            obj = render_objs[i]

            if is_obj(obj):
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
            tri_fn = rotate_fn(tri_fn, cx=0.5, cy=0.5, theta=0.5 * math.pi * agent_dir)
            fill_coords(img, tri_fn, (255, 0, 0))

        # Highlight the cell if needed
        if highlight:
            highlight_img(img)
        # if len(render_objs) > 1:
        #     cv2.imwrite('/home/tanmayx/memory_object_search_compress/outputs/env_rollouts/icon.png', img)
        # Downsample the image to perform supersampling/anti-aliasing
        img = downsample(img, subdivs)

        # Cache the rendered tile
        cls.tile_cache[key] = img

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
                # else:
                #     furniture, obj = self.grid[self.render_dim].get(i, j)
                #     state_values = self.state_values.get(obj, None)
                #
                #     img[ymin:ymax, xmin:xmax, :] = GridDimension.render_tile(
                #         furniture,
                #         obj,
                #         state_values,
                #         agent_dir=agent_dir if agent_here else None,
                #         highlight=highlight_mask[i, j],
                #         tile_size=tile_size,
                #         draw_grid_lines=True
                #     )

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
                    v = self.get_all_objs(i, j)
                    for obj in v:
                        encoding = obj.encode() if is_obj(obj) else np.array([OBJECT_TO_IDX['empty'], 0, 0])
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
