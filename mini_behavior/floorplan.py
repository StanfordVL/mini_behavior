import os
import numpy as np
from mini_behavior.minibehavior import MiniBehaviorEnv
from mini_behavior.grid import BehaviorGrid
from mini_behavior.register import register
from mini_behavior.objects import Wall
from mini_behavior.utils.scene_to_grid import img_to_array

FLOORPLANS_DIR = os.path.join(os.path.dirname(os.path.abspath(__name__)), "mini_behavior", "floorplans")


def get_floorplan(scene_id) :
    return os.path.join(FLOORPLANS_DIR, f"{scene_id}_floor_trav_no_obj_0.png")


# generate grid
class FloorPlanEnv(MiniBehaviorEnv):
    def __init__(self,
                 img_path=None,
                 mode='cartesian',
                 scene_id='beechwood_0_int',
                 num_objs=None,
                 max_steps=1e5,
                 ):

        self.scene_id = scene_id
        img_path = get_floorplan(scene_id)
        self.img_path = img_path
        self.floor_plan = img_to_array(img_path) # assume img_path is to grid version of floorplan

        if num_objs is None:
            num_objs = {'goal': 1}

        self.height, self.width = np.shape(self.floor_plan)
        self.num_objs = num_objs
        self.mission = ''

        super().__init__(mode=mode,
                         width=self.width,
                         height=self.height,
                         num_objs=self.num_objs,
                         max_steps=max_steps)


    def add_walls(self):
        # add walls based on floor plan
        for i in range(self.height):
            for j in range(self.width):
                if self.floor_plan[i, j] == 0:
                    self.put_obj(Wall(), j, i)

    def _gen_grid(self, width, height):
        self.grid = BehaviorGrid(width, height)
        self.add_walls()
        self._gen_objs()
        assert self._init_conditions(), "Does not satisfy initial conditions"
        self.place_agent()

    def _gen_objs(self):
        goal = self.objs['goal'][0]
        self.target_pos = self.place_obj(goal)

    def _end_conditions(self):
        pass
        # if np.all(self.agent_pos == self.target_pos):
        #     return True
        # else:
        #     return False


# register environments of all floorplans in floorplans dir
all_scenes = os.listdir(FLOORPLANS_DIR)

for img in all_scenes:
    img_name = img
    if '/' in img_name:
        img_name = img_name.split('/')[1]
    if '.' in img_name:
        img_name = img_name.split('.')[0]
    env_id = 'MiniGrid-{}-0x0-N1-v0'.format(img_name)

    register(
        id=env_id,
        entry_point='mini_behavior.envs:FloorPlanEnv',
        kwargs={'img_path': '{}/{}'.format(FLOORPLANS_DIR, img)}
    )
