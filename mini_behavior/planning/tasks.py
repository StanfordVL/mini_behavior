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

def solve_printer(env):
    plan = [
       ("goto", "printer_0"),
       ("pickup", "printer_0"),
       ("goto", "table_0"),
       ("drop", "printer_0"),
       ("toggle", "printer_0"),
    ]

    for elem in plan:
        yield (ACTION_FUNC_MAPPING[elem[0]], env.obj_instances[elem[1]]) #type: ignore

def solve_misplaced_items(env):
    plan = []

    items =  ['gym_shoe_0', 'necklace_0', 'notebook_0', 'sock_0', 'sock_1']
    for item in items:
        plan += [ ("goto", item), ("pickup", item)]

    plan.append(("goto", "table_1"))

    for item in items:
        plan += [ ("drop", item) ]

    for elem in plan:
        yield (ACTION_FUNC_MAPPING[elem[0]], env.obj_instances[elem[1]]) #type: ignore

def solve_candles(env):
    plan = []
    for idx in range(6):
        plan += [
           ("goto", f"candle_{idx}"),
           ("pickup", f"candle_{idx}"),
        ]

    plan.append(("goto", "table_0"))

    for idx in range(3):
        plan.append(("drop", f"candle_{idx}"))

    plan.append(("goto", "table_1"))

    for idx in range(3, 6):
        plan.append(("drop", f"candle_{idx}"))

    for elem in plan:
        yield (ACTION_FUNC_MAPPING[elem[0]], env.obj_instances[elem[1]]) #type: ignore

def solve_open_packages(env):
    plan = []
    for idx in range(2):
        plan += [
           ("goto", f"package_{idx}"),
           ("open", f"package_{idx}"),
        ]

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

def solve_organizing_pantry(env):
    oatmeals = env.objs['oatmeal']
    chips = env.objs['chip']
    vegetable_oils = env.objs['vegetable_oil']
    sugars = env.objs['sugar']
    cabinet = env.objs['cabinet'][0]

    plan = []
    for obj in oatmeals + chips + vegetable_oils + sugars:
        plan += [
           ("goto", obj.name),
           ("pickup", obj.name),
        ]
    plan.append(("goto", cabinet.name))
    plan.append(("open", cabinet.name))

    for obj in oatmeals + chips + vegetable_oils + sugars:
        plan += [
           ("drop_in", obj.name),
        ]

    for elem in plan:
        yield (ACTION_FUNC_MAPPING[elem[0]], env.obj_instances[elem[1]]) #type: ignore

def solve_organizing(env):
    plan = []
    plan += [
       ("goto", "marker_0"),
       ("pickup", "marker_0"),
    ]
    for idx in range(4):
        plan += [
           ("goto", f"document_{idx}"),
           ("pickup", f"document_{idx}"),
        ]

    for idx in range(2):
        plan += [
           ("goto", f"folder_{idx}"),
           ("pickup", f"folder_{idx}"),
        ]

    plan.append(("goto", "table_0"))
    plan.append(("drop", "marker_0"))
    plan.append(("goto", "cabinet_0"))
    plan.append(("open", "cabinet_0"))

    for idx in range(4):
        plan.append(("drop_in", f"document_{idx}"))

    for idx in range(2):
        plan.append(("drop_in", f"folder_{idx}"))

    for elem in plan:
        yield (ACTION_FUNC_MAPPING[elem[0]], env.obj_instances[elem[1]]) #type: ignore

