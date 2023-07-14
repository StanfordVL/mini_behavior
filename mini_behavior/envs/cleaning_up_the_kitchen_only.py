from mini_behavior.roomgrid import *
from mini_behavior.register import register


class CleaningUpTheKitchenOnlyEnv(RoomGrid):
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
        num_objs = {'bin': 1, 'soap': 1, 'cabinet': 2, 'electric_refrigerator': 1, 'rag': 1, 'dustpan': 1,
                        'broom': 1, 'blender': 1, 'sink': 1, 'casserole': 1, 'plate': 1, 'vegetable_oil': 1,
                        'apple': 1, 'countertop': 1} # 'window': 1,

        self.mission = 'clean up the kitchen'

        super().__init__(mode=mode,
                         num_objs=num_objs,
                         room_size=room_size,
                         num_rows=num_rows,
                         num_cols=num_cols,
                         max_steps=max_steps
                         )

    def _gen_objs(self):
        cabinets = self.objs['cabinet']
        electric_refrigerator = self.objs['electric_refrigerator'][0]
        sink = self.objs['sink'][0]
        countertop = self.objs['countertop'][0]
        bin = self.objs['bin'][0]

        soap = self.objs['soap'][0]
        rag = self.objs['rag'][0]
        broom = self.objs['broom'][0]
        dustpan = self.objs['dustpan'][0]
        blender = self.objs['blender'][0]
        casserole = self.objs['casserole'][0]
        plate = self.objs['plate'][0]
        vegetable_oil = self.objs['vegetable_oil'][0]
        apple = self.objs['apple'][0]

        self.place_obj(cabinets[0])
        self.place_obj(cabinets[1])
        self.place_obj(electric_refrigerator)
        self.place_obj(bin)
        self.place_obj(sink)
        self.place_obj(countertop)

        cabinet_pos = self._rand_subset(cabinets[0].all_pos, 3)
        self.put_obj(soap, *cabinet_pos[0], 1)
        self.put_obj(rag, *cabinet_pos[1], 1)
        rag.states['soakable'].set_value(False)
        self.put_obj(dustpan, *cabinet_pos[2], 1)
        dustpan.states['dustyable'].set_value(True)

        for obj in [soap, rag, dustpan]:
            obj.states['inside'].set_value(cabinets[0], True)

        self.place_obj(broom)
        broom.states['dustyable'].set_value(True)
        self.place_obj(blender)
        blender.states['stainable'].set_value(True)

        fridge_pos = self._rand_subset(electric_refrigerator.all_pos, 4)
        self.put_obj(casserole, *fridge_pos[0], 1)
        self.put_obj(plate, *fridge_pos[1], 1)
        plate.states['stainable'].set_value(True)
        self.put_obj(vegetable_oil, *fridge_pos[2], 1)
        self.put_obj(apple, *fridge_pos[3], 1)

        for obj in [casserole, plate, vegetable_oil, apple]:
            obj.states['inside'].set_value(electric_refrigerator, True)

        # (dusty floor.n.01_1)
        cabinets[0].states['dustyable'].set_value(True)
        cabinets[1].states['dustyable'].set_value(True)

    def _init_conditions(self):
        for obj_type in ['bin', 'soap', 'cabinet', 'electric_refrigerator', 'rag', 'dustpan', 'broom', 'blender',
                         'sink', 'casserole', 'plate', 'vegetable_oil', 'apple', 'countertop']:
            assert obj_type in self.objs.keys(), f"No {obj_type}"

        return True



    def _end_conditions(self):
        cabinets = self.objs['cabinet']
        electric_refrigerator = self.objs['electric_refrigerator'][0]
        sink = self.objs['sink'][0]
        countertop = self.objs['countertop'][0]

        soap = self.objs['soap'][0]
        rag = self.objs['rag'][0]
        blender = self.objs['blender'][0]
        casserole = self.objs['casserole'][0]
        plate = self.objs['plate'][0]
        vegetable_oil = self.objs['vegetable_oil'][0]
        apple = self.objs['apple'][0]

        if not blender.check_rel_state(self, countertop, 'onTop'):
            return False

        if not soap.check_rel_state(self, sink, 'nextto'):
            return False

        exists = False
        for cabinet in cabinets:
            if vegetable_oil.check_rel_state(self, cabinet, 'inside') and not plate.check_rel_state(self, cabinet, 'inside'):
                exists = True
                break

        if not exists:
            return False

        for cabinet in cabinets:
            if not vegetable_oil.check_rel_state(self, cabinet, 'inside') and plate.check_rel_state(self, cabinet, 'inside'):
                exists = True
                break

        if not exists:
            return False

        for cabinet in cabinets:
            if cabinet.check_abs_state(self, 'dustyable'):
                return False

        if plate.check_abs_state(self, 'stainable'):
            return False

        if not rag.check_rel_state(self, sink, 'inside') and not rag.check_rel_state(self, sink, 'nextto'):
            return False

        if not casserole.check_rel_state(self, electric_refrigerator, 'inside') or not apple.check_rel_state(self, electric_refrigerator, 'inside'):
            return False

        return True


# non human input env
register(
    id='MiniGrid-CleaningUpTheKitchenOnly-16x16-N2-v0',
    entry_point='mini_behavior.envs:CleaningUpTheKitchenOnlyEnv'
)

# human input env
register(
    id='MiniGrid-CleaningUpTheKitchenOnly-16x16-N2-v1',
    entry_point='mini_behavior.envs:CleaningUpTheKitchenOnlyEnv',
    kwargs={'mode': 'cartesian'}
)
