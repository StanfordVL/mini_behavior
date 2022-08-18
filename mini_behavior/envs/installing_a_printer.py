from mini_behavior.roomgrid import *
from mini_behavior.register import register


class InstallingAPrinterEnv(RoomGrid):
    """
    Environment in which the agent is instructed to install a printer
    """

    def __init__(
            self,
            mode='not_human',
            room_size=16,
            num_rows=1,
            num_cols=1,
            max_steps=1e5,
    ):
        num_objs = {'printer': 1, 'table': 1}

        self.mission = 'install a printer'

        super().__init__(mode=mode,
                         num_objs=num_objs,
                         room_size=room_size,
                         num_rows=num_rows,
                         num_cols=num_cols,
                         max_steps=max_steps
                         )

    def _gen_objs(self):
        printer = self.objs['printer'][0]
        table = self.objs['table'][0]

        self.place_obj(table)
        self.place_obj(printer)

    def _init_conditions(self):
        for obj_type in ['printer', 'table']:
            assert obj_type in self.objs.keys(), f"No {obj_type}"

        printer = self.objs['printer'][0]

        assert printer.check_abs_state(self, 'onfloor')
        assert not printer.check_abs_state(self, 'toggleable')

        return True

    def _reward(self):
        return 0

    def _end_conditions(self):
        printer = self.objs['printer'][0]
        table = self.objs['table'][0]

        if printer.check_rel_state(self, table, 'ontop') and printer.check_abs_state(self, 'toggleable'):
            return True
        else:
            return False


# non human input env
register(
    id='MiniGrid-InstallingAPrinter-16x16-N2-v0',
    entry_point='mini_behavior.envs:InstallingAPrinterEnv'
)

# human input env
register(
    id='MiniGrid-InstallingAPrinter-16x16-N2-v1',
    entry_point='mini_behavior.envs:InstallingAPrinterEnv',
    kwargs={'mode': 'human'}
)
