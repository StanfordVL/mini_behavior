from mini_behavior.roomgrid import *
from mini_behavior.register import register


class CleaningACarEnv(RoomGrid):
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
    ):
        num_objs = {'car': 1, 'rag': 1, 'shelf': 1, 'soap': 1, 'bucket': 1, 'sink': 1}

        self.mission = 'clean a car'

        super().__init__(mode=mode,
                         num_objs=num_objs,
                         room_size=room_size,
                         num_rows=num_rows,
                         num_cols=num_cols,
                         max_steps=max_steps
                         )

    def _gen_objs(self):
        car = self.objs['car'][0]
        rag = self.objs['rag'][0]
        shelf = self.objs['shelf'][0]
        soap = self.objs['soap'][0]
        bucket = self.objs['bucket'][0]
        sink = self.objs['sink'][0]

        self.place_obj(shelf)
        self.place_obj(car)
        self.place_obj(bucket)
        self.place_obj(sink)

        # place rag and soap on shelf
        rag_pos, soap_pos = self._rand_subset(shelf.all_pos, 2)
        self.put_obj(rag, *rag_pos, 2)
        self.put_obj(soap, *soap_pos, 2)

        # rag not soaked
        rag.states['soakable'].set_value(False)

        # dusty car
        car.states['dustyable'].set_value(True)

    def _init_conditions(self):
        for obj_type in ['car', 'rag', 'shelf', 'soap', 'bucket', 'sink']:
            assert obj_type in self.objs.keys(), f"No {obj_type}"

        car = self.objs['car'][0]
        rag = self.objs['rag'][0]
        shelf = self.objs['shelf'][0]
        soap = self.objs['soap'][0]
        bucket = self.objs['bucket'][0]

        assert car.check_abs_state(self, 'onfloor')
        assert rag.check_rel_state(self, shelf, 'onTop')
        assert not rag.check_abs_state(self, 'soakable')
        assert soap.check_rel_state(self, soap, 'onTop')
        assert car.check_abs_state(self, 'dustyable')
        assert bucket.check_abs_state(self, 'onfloor')

        return True



    def _end_conditions(self):
        car = self.objs['car'][0]
        rag = self.objs['rag'][0]
        soap = self.objs['soap'][0]
        bucket = self.objs['bucket'][0]

        if not car.check_abs_state(self, 'dustyable') and soap.check_rel_state(self, bucket, 'inside') and rag.check_rel_state(self, bucket, 'inside'):
            return True
        else:
            return False


# non human input env
register(
    id='MiniGrid-CleaningACar-16x16-N2-v0',
    entry_point='mini_behavior.envs:CleaningACarEnv'
)

# human input env
register(
    id='MiniGrid-CleaningACar-16x16-N2-v1',
    entry_point='mini_behavior.envs:CleaningACarEnv',
    kwargs={'mode': 'cartesian'}
)
