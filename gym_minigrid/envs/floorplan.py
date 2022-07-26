import os
import numpy as np
from gym_minigrid.minigrid import Grid, MiniGridEnv
from gym_minigrid.register import register
from gym_minigrid.objects import Wall
from gym_minigrid.scene_to_grid import img_to_array


# generate grid
class FloorPlanEnv(MiniGridEnv):
    def __init__(self,
                 img_path='grids_from_scenes/rs_int_floor_trav_no_obj_0.png',
                 num_objs=None
                 ):

        self.img_path = img_path
        self.floor_plan = img_to_array(img_path) # assume img_path is to grid version of floorplan

        if num_objs is None:
            num_objs = {'goal': 1}

        self.height, self.width = np.shape(self.floor_plan)
        self.num_objs = num_objs

        super().__init__(width=self.width,
                         height=self.height,
                         num_objs=self.num_objs)

    def _gen_grid(self, width, height):
        self.grid = Grid(width, height)
        # add walls
        for i in range(self.height):
            for j in range(self.width):
                if self.floor_plan[i, j] == 0:
                    self.put_obj(Wall(), j, i)

        goal = self.objs['goal'][0]
        self.target_pos = self.place_obj(goal)

        self.place_agent()
        self.mission = 'generate env from floor plan'

    def step(self, action):
        obs, reward, done, info = super().step(action)

        reward = self._reward()
        done = self._end_condition()

        return obs, reward, done, {}

    def _reward(self):
        if self._end_condition():
            return 1
        else:
            return 0

    def _end_condition(self):
        if np.all(self.agent.cur_pos == self.target_pos):
            return True
        else:
            return False


# register environments of all floorplans in grids dir
all_scenes_path = os.path.join(os.path.dirname('gym_minigrid'), 'gym_minigrid/grids')
all_scenes = os.listdir(all_scenes_path)

for img in all_scenes:
    img_name = img
    if '/' in img_name:
        img_name = img_name.split('/')[1]
    if '.' in img_name:
        img_name = img_name.split('.')[0]
    env_id = 'MiniGrid-{}-0x0-N1-v0'.format(img_name)

    register(
        id=env_id,
        entry_point='gym_minigrid.envs:FloorPlanEnv',
        kwargs={'img_path': '{}/{}'.format(all_scenes_path, img)}
    )
