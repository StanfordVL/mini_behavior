from mini_behavior.roomgrid import *
from mini_behavior.register import register


class OrganizingFileCabinetEnv(RoomGrid):
    """
    Environment in which the agent is instructed to clean a car
    """

    def __init__(
            self,
            mode='primitive',
            room_size=16,
            num_rows=1,
            num_cols=1,
            max_steps=1e5,
            num_objs=None
    ):
        if num_objs is None:
            num_objs = {'marker': 1, 'chair': 1, 'document': 4, 'table': 1, 'cabinet': 1, 'folder': 2}

        self.mission = 'open packages'

        super().__init__(mode=mode,
                         num_objs=num_objs,
                         room_size=room_size,
                         num_rows=num_rows,
                         num_cols=num_cols,
                         max_steps=max_steps
                         )

    def _gen_objs(self):
        chair = self.objs['chair'][0]
        table = self.objs['table'][0]
        cabinet = self.objs['cabinet'][0]
        marker = self.objs['marker'][0]
        folders = self.objs['folder']
        documents = self.objs['document']

        # place all furniture
        self.place_obj(chair)
        self.place_obj(table)
        self.place_obj(cabinet)

        pos_0, pos_1, pos_2 = self._rand_subset(table.all_pos, 3)
        pos_3, pos_4 = self._rand_subset(cabinet.all_pos, 2)

        # put marker on chair
        self.put_obj(marker, *chair.cur_pos, 1)

        # put documents
        self.put_obj(documents[0], *pos_0, 2)
        self.put_obj(documents[1], *pos_3, 0)
        self.put_obj(documents[2], *pos_1, 2)
        self.put_obj(documents[3], *pos_4, 1)

        # put folders
        self.put_obj(folders[0], *pos_2, 2)
        self.place_obj(folders[1])

    def _init_conditions(self):
        for obj_type in ['chair', 'table', 'cabinet', 'marker', 'document', 'folder']:
            assert obj_type in self.objs.keys(), f"No {obj_type}"

        chair = self.objs['chair'][0]
        table = self.objs['table'][0]
        cabinet = self.objs['cabinet'][0]
        marker = self.objs['marker'][0]
        folders = self.objs['folder']
        documents = self.objs['document']

        assert marker.check_rel_state(self, chair, 'onTop')
        assert documents[0].check_rel_state(self, table, 'onTop')
        assert documents[1].check_rel_state(self, cabinet, 'inside')
        assert documents[2].check_rel_state(self, table, 'onTop')
        assert documents[3].check_rel_state(self, cabinet, 'inside')
        assert folders[0].check_rel_state(self, table, 'onTop')
        assert folders[1].check_abs_state(self, 'onfloor')

        return True



    def _end_conditions(self):
        chair = self.objs['chair'][0]
        table = self.objs['table'][0]
        cabinet = self.objs['cabinet'][0]
        marker = self.objs['marker'][0]
        folders = self.objs['folder']
        documents = self.objs['document']

        if not marker.check_rel_state(self, table, 'onTop'):
            return False

        for document in documents:
            if not document.check_rel_state(self, cabinet, 'inside'):
                return False

        for folder in folders:
            if not folder.check_rel_state(self, cabinet, 'inside'):
                return False

        return True


# non human input env
register(
    id='MiniGrid-OrganizingFileCabinet-16x16-N2-v0',
    entry_point='mini_behavior.envs:OrganizingFileCabinetEnv'
)

# human input env
register(
    id='MiniGrid-OrganizingFileCabinet-16x16-N2-v1',
    entry_point='mini_behavior.envs:OrganizingFileCabinetEnv',
    kwargs={'mode': 'cartesian'}
)
