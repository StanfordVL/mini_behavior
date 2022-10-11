from mini_behavior.roomgrid import *
from mini_behavior.register import register
from mini_behavior.grid import is_obj
from mini_behavior.actions import Pickup, Drop, Toggle
from mini_behavior.objects import Wall
from bddl import ACTION_FUNC_MAPPING
from mini_behavior.floorplan import *

from enum import IntEnum
from gym import spaces
import math
from .installing_a_printer import InstallingAPrinterEnv


class SimpleInstallingAPrinterEnv(InstallingAPrinterEnv):
    """
    Environment in which the agent is instructed to install a printer
    """
    class Actions(IntEnum):
        left = 0
        right = 1
        forward = 2
        pickup = 3
        drop = 4
        toggle = 5

    def __init__(
            self,
            mode='not_human',
            room_size=16,
            num_rows=1,
            num_cols=1,
            max_steps=50,
    ):
        self.printer = None
        self.table = None

        super().__init__(mode=mode,
                         room_size=room_size,
                         num_rows=num_rows,
                         num_cols=num_cols,
                         max_steps=max_steps
                         )

        self.actions = SimpleInstallingAPrinterEnv.Actions
        self.action_space = spaces.Discrete(len(self.actions))

        self.observation_space = spaces.Dict(
            {
                "agent_x": spaces.Discrete(room_size),
                "agent_y": spaces.Discrete(room_size),
                "printer_inhandofrobot": spaces.Discrete(2),
                "printer_toggledon": spaces.Discrete(2),
                "printer_ontop_table": spaces.Discrete(2),
                "agent_dir": spaces.Discrete(4),
            }
        )

        self.reward_range = (-math.inf, math.inf)

    def gen_obs(self):
        self.printer = self.objs['printer'][0]
        self.table = self.objs['table'][0]

        printer_inhandofrobot = int(self.printer.check_abs_state(self, 'inhandofrobot'))
        printer_ontop_table = int(self.printer.check_rel_state(self, self.table, 'onTop'))
        printer_toggledon = int(self.printer.check_abs_state(self, 'toggledon'))

        obs = {
            "agent_x": self.agent_pos[0],
            "agent_y": self.agent_pos[1],
            "agent_dir": self.agent_dir,
            "printer_inhandofrobot": printer_inhandofrobot,
            "printer_toggledon": printer_ontop_table,
            "printer_ontop_table": printer_toggledon,
        }

        return obs

    def _gen_objs(self):
        printer = self.objs['printer'][0]
        table = self.objs['table'][0]

        # table_pos = (5, 3)
        # printer_pos = (8, 12)
        table_pos = (1, 2)
        printer_pos = (6, 5)
        self.put_obj(table, *table_pos, 0)
        self.put_obj(printer, *printer_pos, 0)

    def step(self, action):
        self.step_count += 1
        # Get the position and contents in front of the agent
        fwd_pos = self.front_pos
        fwd_cell = self.grid.get(*fwd_pos)

        # Rotate left
        if action == self.actions.left:
            self.agent_dir -= 1
            if self.agent_dir < 0:
                self.agent_dir += 4

        # Rotate right
        elif action == self.actions.right:
            self.agent_dir = (self.agent_dir + 1) % 4

        # Move forward
        elif action == self.actions.forward:
            can_overlap = True
            for dim in fwd_cell:
                for obj in dim:
                    if is_obj(obj) and not obj.can_overlap:
                        can_overlap = False
                        break
            if can_overlap:
                self.agent_pos = fwd_pos
        elif action == self.actions.pickup:
            if Pickup(self).can(self.printer):
                Pickup(self).do(self.printer)
        elif action == self.actions.drop:
            if Drop(self).can(self.printer):
                Drop(self).do(self.printer, 2)
        elif action == self.actions.toggle:
            if Toggle(self).can(self.printer):
                Toggle(self).do(self.printer)

        self.update_states()
        reward = self._reward()
        done = self._end_conditions() # self.step_count >= self.max_steps
        obs = self.gen_obs()

        return obs, reward, done, {}

    def _reward(self):
        if self._end_conditions():
            self.reward += 100
        else:
            self.reward -= 1

        return self.reward


register(
    id='MiniGrid-SimpleInstallingAPrinter-16x16-N2-v0',
    entry_point='mini_behavior.envs:SimpleInstallingAPrinterEnv'
)

register(
    id='MiniGrid-SimpleInstallingAPrinter-8x8-N2-v0',
    entry_point='mini_behavior.envs:SimpleInstallingAPrinterEnv',
    kwargs={'room_size': 8}
)



class SimpleInstallingAPrinterTwoEnv(InstallingAPrinterEnv):
    """
    Environment in which the agent is instructed to install a printer
    """
    class Actions(IntEnum):
        left = 0
        right = 1
        forward = 2
        pickup = 3
        drop = 4
        toggle = 5

    def __init__(
            self,
            mode='not_human',
            room_size=17,
            num_rows=1,
            num_cols=1,
            max_steps=50,
    ):
        self.printer = None
        self.table = None

        super().__init__(mode=mode,
                         room_size=room_size,
                         num_rows=num_rows,
                         num_cols=num_cols,
                         max_steps=max_steps
                         )

        self.actions = SimpleInstallingAPrinterEnv.Actions
        self.action_space = spaces.Discrete(len(self.actions))

        self.observation_space = spaces.Dict(
            {
                "agent_x": spaces.Discrete(room_size),
                "agent_y": spaces.Discrete(8),
                "printer_inhandofrobot": spaces.Discrete(2),
                "printer_toggledon": spaces.Discrete(2),
                "printer_ontop_table": spaces.Discrete(2),
                "agent_dir": spaces.Discrete(4),
            }
        )

        self.reward_range = (-math.inf, math.inf)

    def _gen_grid(self, width, height):
        super()._gen_grid(width, height)
        self.agent_pos = None
        for i in range(8, 15):
            self.grid.horz_wall(0, i)
        self.grid.vert_wall(8, 0, 3)
        self.grid.vert_wall(8, 4)
        self.place_agent()

    def gen_obs(self):
        self.printer = self.objs['printer'][0]
        self.table = self.objs['table'][0]

        printer_inhandofrobot = int(self.printer.check_abs_state(self, 'inhandofrobot'))
        printer_ontop_table = int(self.printer.check_rel_state(self, self.table, 'onTop'))
        printer_toggledon = int(self.printer.check_abs_state(self, 'toggledon'))

        obs = {
            "agent_x": self.agent_pos[0],
            "agent_y": self.agent_pos[1],
            "agent_dir": self.agent_dir,
            "printer_inhandofrobot": printer_inhandofrobot,
            "printer_toggledon": printer_ontop_table,
            "printer_ontop_table": printer_toggledon,
        }

        return obs

    def _gen_objs(self):
        printer = self.objs['printer'][0]
        table = self.objs['table'][0]

        # table_pos = (5, 3)
        # printer_pos = (8, 12)
        table_pos = (1, 2)
        printer_pos = (6, 5)
        self.put_obj(table, *table_pos, 0)
        self.put_obj(printer, *printer_pos, 0)

        self.put_obj(Wall(), 3, 5, 0)

    def step(self, action):
        self.step_count += 1
        # Get the position and contents in front of the agent
        fwd_pos = self.front_pos
        fwd_cell = self.grid.get(*fwd_pos)

        # Rotate left
        if action == self.actions.left:
            self.agent_dir -= 1
            if self.agent_dir < 0:
                self.agent_dir += 4

        # Rotate right
        elif action == self.actions.right:
            self.agent_dir = (self.agent_dir + 1) % 4

        # Move forward
        elif action == self.actions.forward:
            can_overlap = True
            for dim in fwd_cell:
                for obj in dim:
                    if is_obj(obj) and not obj.can_overlap:
                        can_overlap = False
                        break
            if can_overlap:
                self.agent_pos = fwd_pos
        elif action == self.actions.pickup:
            if Pickup(self).can(self.printer):
                Pickup(self).do(self.printer)
        elif action == self.actions.drop:
            if Drop(self).can(self.printer):
                Drop(self).do(self.printer, 2)
        elif action == self.actions.toggle:
            if Toggle(self).can(self.printer):
                Toggle(self).do(self.printer)

        self.update_states()
        reward = self._reward()
        done = self._end_conditions() # self.step_count >= self.max_steps
        obs = self.gen_obs()

        return obs, reward, done, {}

    def _reward(self):
        if self._end_conditions():
            self.reward += 100
        else:
            self.reward -= 1

        return self.reward



register(
    id='MiniGrid-SimpleInstallingAPrinterTwo-8x8-N2-v0',
    entry_point='mini_behavior.envs:SimpleInstallingAPrinterTwoEnv',
)



class SimpleInstallingAPrinterFloorplanEnv(FloorPlanEnv):
    """
    Environment in which the agent is instructed to install a printer
    """
    class Actions(IntEnum):
        left = 0
        right = 1
        forward = 2
        pickup = 3
        drop = 4
        toggle = 5

    def __init__(
            self,
            mode='human',
            scene_id='rs_int',
            num_objs=None,
            max_steps=50
    ):
        self.printer = None
        self.table = None

        num_objs = {'printer': 1, 'table': 1}

        self.mission = 'install a printer'

        super().__init__(mode=mode,
                         scene_id=scene_id,
                         num_objs=num_objs,
                         max_steps=max_steps
                         )

        self.actions = SimpleInstallingAPrinterEnv.Actions
        self.action_space = spaces.Discrete(len(self.actions))

        self.observation_space = spaces.Dict(
            {
                "agent_x": spaces.Discrete(self.grid.width),
                "agent_y": spaces.Discrete(self.grid.height),
                "printer_inhandofrobot": spaces.Discrete(2),
                "printer_toggledon": spaces.Discrete(2),
                "printer_ontop_table": spaces.Discrete(2),
                "agent_dir": spaces.Discrete(4),
            }
        )

        self.reward_range = (-math.inf, math.inf)

    def gen_obs(self):
        self.printer = self.objs['printer'][0]
        self.table = self.objs['table'][0]

        printer_inhandofrobot = int(self.printer.check_abs_state(self, 'inhandofrobot'))
        printer_ontop_table = int(self.printer.check_rel_state(self, self.table, 'onTop'))
        printer_toggledon = int(self.printer.check_abs_state(self, 'toggledon'))

        obs = {
            "agent_x": self.agent_pos[0],
            "agent_y": self.agent_pos[1],
            "agent_dir": self.agent_dir,
            "printer_inhandofrobot": printer_inhandofrobot,
            "printer_toggledon": printer_ontop_table,
            "printer_ontop_table": printer_toggledon,
        }

        return obs

    def _gen_objs(self):
        printer = self.objs['printer'][0]
        table = self.objs['table'][0]

        # table_pos = (5, 3)
        # printer_pos = (8, 12)
        table_pos = (20, 30)
        printer_pos = (40, 10)
        table.width = 8
        table.height = 6
        self.put_obj(table, *table_pos, 0)
        self.put_obj(printer, *printer_pos, 0)

    def step(self, action):
        self.step_count += 1
        # Get the position and contents in front of the agent
        fwd_pos = self.front_pos
        fwd_cell = self.grid.get(*fwd_pos)

        # Rotate left
        if action == self.actions.left:
            self.agent_dir -= 1
            if self.agent_dir < 0:
                self.agent_dir += 4

        # Rotate right
        elif action == self.actions.right:
            self.agent_dir = (self.agent_dir + 1) % 4

        # Move forward
        elif action == self.actions.forward:
            can_overlap = True
            for dim in fwd_cell:
                for obj in dim:
                    if is_obj(obj) and not obj.can_overlap:
                        can_overlap = False
                        break
            if can_overlap:
                self.agent_pos = fwd_pos
        elif action == self.actions.pickup:
            if Pickup(self).can(self.printer):
                Pickup(self).do(self.printer)
        elif action == self.actions.drop:
            if Drop(self).can(self.printer):
                Drop(self).do(self.printer, 2)
        elif action == self.actions.toggle:
            if Toggle(self).can(self.printer):
                Toggle(self).do(self.printer)

        self.update_states()
        reward = self._reward()
        done = self._end_conditions() # self.step_count >= self.max_steps
        obs = self.gen_obs()

        return obs, reward, done, {}

    def _reward(self):
        if self._end_conditions():
            self.reward += 100
        else:
            self.reward -= 1

        return self.reward

    def _end_conditions(self):
        printer = self.objs['printer'][0]
        table = self.objs['table'][0]

        if printer.check_rel_state(self, table, 'onTop') and printer.check_abs_state(self, 'toggleable'):
            return True
        else:
            return False

register(
    id='MiniGrid-SimpleInstallingAPrinterRSInt-8x8-N2-v0',
    entry_point='mini_behavior.envs:SimpleInstallingAPrinterFloorplanEnv',
)


class SimpleInstallingAPrinterDistractEnv(SimpleInstallingAPrinterEnv):
    """
    Environment in which the agent is instructed to install a printer
    """

    def __init__(
            self,
            mode='human',
            room_size=16,
            num_rows=1,
            num_cols=1,
            max_steps=50,
    ):

        super().__init__(mode=mode,
                         room_size=room_size,
                         num_rows=num_rows,
                         num_cols=num_cols,
                         max_steps=max_steps
                         )

        self.reward_range = (-math.inf, math.inf)

    def _gen_objs(self):
        printer = self.objs['printer'][0]
        table = self.objs['table'][0]

        # table_pos = (5, 3)
        # printer_pos = (8, 12)
        table_pos = (1, 2)
        printer_pos = (6, 5)
        self.put_obj(table, *table_pos, 0)
        self.put_obj(printer, *printer_pos, 0)

        self.put_obj(Wall(), 3, 5, 0)


register(
    id='MiniGrid-SimpleInstallingAPrinterDistract-16x16-N2-v0',
    entry_point='mini_behavior.envs:SimpleInstallingAPrinterDistractEnv',
    kwargs={'mode': 'not_human'}
)


register(
    id='MiniGrid-SimpleInstallingAPrinterDistract-8x8-N2-v0',
    entry_point='mini_behavior.envs:SimpleInstallingAPrinterDistractEnv',
    kwargs={'mode': 'not_human', 'room_size': 8}
)