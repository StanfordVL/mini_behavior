def get_obj_env_cell(self):
    obj = self.obj
    env = self.env
    cell = env.grid.get(*obj.cur_pos)

    return obj, env, cell


def get_obj_cell(self, env):
    obj = self.obj
    cell = env.grid.get(*obj.cur_pos)

    return obj, cell