from mini_behavior.roomgrid import *
from mini_behavior.register import register
from mini_behavior.objects import OBJECT_CLASS

DEFAULT_OBJS = ['countertop', 'plate', 'ashcan', 'hamburger', 'ball', 'apple', 'carton', 'juice']


def create_transition_matrices(objs, num_rooms):
    """
    return dict transitions, where transitions[obj] is the transition matrix for any obj in objs.
    the probability of obj going from room i --> j is: transitions[obj][i, j]
    """
    transitions = {}
    for obj in objs:
        probs = np.random.rand(num_rooms, num_rooms)
        probs /= np.expand_dims(np.sum(probs, axis=1), 1)
        transitions[obj] = probs

    return transitions


class TransitionEnv(RoomGrid):
    """
    at every episode, randomly sample num_choose objects from given object list
    at every step, place objects in rooms based on matrix of transition probabilities
    """

    def __init__(
            self,
            objs=None,
            transition_probs=None,
            num_choose=4,
            mode='primitive',
            room_size=8,
            num_rows=2,
            num_cols=2,
            max_steps=10,
            seed=1337
    ):
        if objs is None:
            objs = DEFAULT_OBJS

        self.available_objs = objs
        self.num_choose = num_choose
        self.num_rooms = num_rows * num_cols

        # generate matrix
        if transition_probs is None:
            self.transition_probs = create_transition_matrices(objs, self.num_rooms)
        else:
            for obj in objs:
                assert obj in transition_probs.keys(), f'{obj} missing transition matrix'
                assert np.all(np.shape(transition_probs[obj]) == np.array([self.num_rooms, self.num_rooms])), f'{obj} matrix has incorrect dimensions'
            self.transition_probs = transition_probs

        # randomly pick num_choose objs
        self.seed(seed=seed)
        chosen_objs = self._rand_subset(objs, num_choose)

        # initialize num_objs, key=obj name (str), value=num of the obj (1)
        num_objs = {obj: 1 for obj in chosen_objs}

        super().__init__(mode=mode,
                         num_objs=num_objs,
                         room_size=room_size,
                         num_rows=num_rows,
                         num_cols=num_cols,
                         max_steps=max_steps,
                         seed=seed
                         )

        self.mission = 'find the objs as they transition between rooms'

        actions = {'left': 0,
                   'right': 1,
                   'forward': 2}

        self.actions = IntEnum('Actions', actions)

    def choose_objs(self):
        chosen_objs = self._rand_subset(self.available_objs, self.num_choose)
        num_objs = {obj: 1 for obj in chosen_objs}

        # initialize num_objs, key=obj name (str), value=num of the obj (1)
        return num_objs

    def reset(self):
        num_objs = self.choose_objs()

        self.objs = {}
        self.obj_instances = {}
        for obj in num_objs.keys():
            self.objs[obj] = []
            for i in range(num_objs[obj]):
                obj_name = '{}_{}'.format(obj, i)
                obj_instance = OBJECT_CLASS[obj](obj_name)
                self.objs[obj].append(obj_instance)
                self.obj_instances[obj_name] = obj_instance

        super().reset()

    def _gen_objs(self):
        # randomly place objs on the grid
        for obj in self.obj_instances.values():
            self.place_obj(obj)

    def step(self, action):
        super().step(action)

        # use transition prob to decide what room the obj should be in
        for obj in self.obj_instances.values():
            if obj.type != 'door':
                cur_room = self.room_num_from_pos(*obj.cur_pos) # int
                probs = self.transition_probs[obj.get_class()][cur_room]
                new_room = np.random.choice(self.num_rooms, 1, p=probs)[0] # int
                room_idx = self.room_idx_from_num(new_room) # tuple
                self.grid.remove(*obj.cur_pos, obj) # remove obj from grid
                self.place_in_room(*room_idx, obj) # add obj to grid

        obs = self.gen_obs()
        reward = self._reward()
        done = self._end_conditions()
        return obs, reward, done, {}

    def _end_conditions(self):
        return self.step_count == self.max_steps


register(
    id='MiniGrid-TransitionEnv-8x8x4-N2-v0',
    entry_point='mini_behavior.envs:TransitionEnv',
)

register(
    id='MiniGrid-TransitionEnv-8x8x4-N2-v1',
    entry_point='mini_behavior.envs:TransitionEnv',
    kwargs={'mode': 'cartesian'}
)
