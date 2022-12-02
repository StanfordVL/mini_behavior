from bddl.actions import ACTION_FUNC_MAPPING

def solve_boxing(env):
    plan = []
    for idx in range(7):
        plan += [
           ("goto", f"book_{idx}"),
           ("pickup", f"book_{idx}"),
        ]

    plan.append(("goto", "box_0"))
    for idx in range(7):
        plan.append(("drop_in", f"book_{idx}"))

    for elem in plan:
        yield (ACTION_FUNC_MAPPING[elem[0]], env.obj_instances[elem[1]]) #type: ignore

def solve_boxing_debug(env):
    plan = []
    for idx in range(3):
        plan += [
           ("goto", f"book_{idx}"),
           ("pickup", f"book_{idx}"),
        ]

    plan.append(("goto", "box_0"))
    for idx in range(3):
        plan.append(("drop", f"book_{idx}"))
    for idx in range(3):
        plan.append(("pickup", f"book_{idx}"))

    for elem in plan:
        yield (ACTION_FUNC_MAPPING[elem[0]], env.obj_instances[elem[1]]) #type: ignore

