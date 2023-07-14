from mini_behavior.roomgrid import *
from mini_behavior.register import register


class CleaningShoesEnv(RoomGrid):
    """
    Environment in which the agent is instructed to clean a car
    """

    def __init__(
            self,
            mode='primitive',
            room_size=8,
            num_rows=1,
            num_cols=1,
            max_steps=1e5,
    ):
        num_objs = {'soap': 1, 'bed': 1, 'rag': 1, 'towel': 1, 'shoe': 4, 'sink': 1}

        self.mission = 'clean shoes'

        super().__init__(mode=mode,
                         num_objs=num_objs,
                         room_size=room_size,
                         num_rows=num_rows,
                         num_cols=num_cols,
                         max_steps=max_steps
                         )

    def _gen_objs(self):
        bed = self.objs['bed'][0]
        soap = self.objs['soap'][0]
        rag = self.objs['rag'][0]
        towel = self.objs['towel'][0]
        sink = self.objs['sink'][0]

        shoes = self.objs['shoe']

        self.place_obj(bed)
        self.place_obj(towel)
        self.place_obj(sink)

        # place rag, soap, shoes on bed
        rag_pos, soap_pos, shoe_0, shoe_1, shoe_2, shoe_3 = self._rand_subset(bed.all_pos, 6)
        self.put_obj(rag, *rag_pos, 1)
        self.put_obj(soap, *soap_pos, 1)
        self.put_obj(shoes[0], *shoe_0, 1)
        self.put_obj(shoes[1], *shoe_1, 1)
        self.put_obj(shoes[2], *shoe_2, 1)
        self.put_obj(shoes[3], *shoe_3, 1)

        # stain 2 shoes
        for shoe in shoes[:2]:
            shoe.states['stainable'].set_value(True)
        # dusty 2 shoes
        for shoe in shoes[2:]:
            shoe.states['dustyable'].set_value(True)

        # not soaked rag
        rag.states['soakable'].set_value(False)

    def _init_conditions(self):
        for obj_type in ['soap', 'bed', 'rag', 'towel', 'shoe', 'sink']:
            assert obj_type in self.objs.keys(), f"No {obj_type}"

        bed = self.objs['bed'][0]
        soap = self.objs['soap'][0]
        rag = self.objs['rag'][0]
        towel = self.objs['towel'][0]
        shoes = self.objs['shoe']

        assert soap.check_rel_state(self, bed, 'onTop')
        assert rag.check_rel_state(self, bed, 'onTop')
        assert towel.check_abs_state(self, 'onfloor')

        for shoe in shoes:
            assert shoe.check_rel_state(self, bed, 'onTop')

        for shoe in shoes[:2]:
            assert shoe.check_abs_state(self, 'stainable')
        for shoe in shoes[2:]:
            assert shoe.check_abs_state(self, 'dustyable')

        assert not rag.check_abs_state(self, 'soakable')

        return True



    def _end_conditions(self):
        shoes = self.objs['shoe']
        towel = self.objs['towel'][0]

        for shoe in shoes:
            if shoe.check_abs_state(self, 'stainable') or shoe.check_abs_state(self, 'dustyable'):
                return False

        return towel.check_abs_state(self, 'onfloor')


# non human input env
register(
    id='MiniGrid-CleaningShoes-16x16-N2-v0',
    entry_point='mini_behavior.envs:CleaningShoesEnv'
)

# human input env
register(
    id='MiniGrid-CleaningShoes-16x16-N2-v1',
    entry_point='mini_behavior.envs:CleaningShoesEnv',
    kwargs={'mode': 'cartesian'}
)
