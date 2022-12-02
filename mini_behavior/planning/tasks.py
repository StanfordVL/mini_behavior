from bddl.actions import ACTION_FUNC_MAPPING

def boxing_books_up_for_storage(env):
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

def installing_a_printer(env):
    plan = [
       ("goto", "printer_0"),
       ("pickup", "printer_0"),
       ("goto", "table_0"),
       ("drop", "printer_0"),
       ("toggle", "printer_0"),
    ]

    for elem in plan:
        yield (ACTION_FUNC_MAPPING[elem[0]], env.obj_instances[elem[1]]) #type: ignore

def collect_misplaced_items(env):
    plan = []

    items =  ['gym_shoe_0', 'necklace_0', 'notebook_0', 'sock_0', 'sock_1']
    for item in items:
        plan += [ ("goto", item), ("pickup", item)]

    plan.append(("goto", "table_1"))

    for item in items:
        plan += [ ("drop", item) ]

    for elem in plan:
        yield (ACTION_FUNC_MAPPING[elem[0]], env.obj_instances[elem[1]]) #type: ignore

def setting_up_candles(env):
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

def opening_packages(env):
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

def organizing_file_cabinet(env):
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

def storing_food(env):
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

def storing_food(env):
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

def cleaning_shoes(env):
    plan = [
       ("goto", "rag_0"),
       ("pickup", "rag_0"),
       ("goto", "sink_0"),
       ("toggle", "sink_0"),
       ("drop_in", "rag_0"),
       ("pickup", "rag_0"),
    ]

    shoes = env.objs['shoe']

    for shoe in shoes:
        plan += [
            ("goto", shoe.name),
            ("clean", shoe.name)
        ]
    for elem in plan:
        yield (ACTION_FUNC_MAPPING[elem[0]], env.obj_instances[elem[1]]) #type: ignore

def cleaning_a_car(env):
    plan = [
        ("goto", "rag_0"),
        ("pickup", "rag_0"),
        ("goto", "soap_0"),
        ("pickup", "soap_0"),
        ("goto", "sink_0"),
        ("drop_in", "rag_0"),
        ("toggle", "sink_0"),
        ("pickup", "rag_0"),
        ("goto", "car_0"),
        ("clean", "car_0"),
        ("goto", "bucket_0"),
        ("drop_in", "rag_0"),
        ("drop_in", "soap_0"),
    ]
    for elem in plan:
        yield (ACTION_FUNC_MAPPING[elem[0]], env.obj_instances[elem[1]]) #type: ignore

def moving_boxes_to_storage(env):
    plan = []
    cartons = env.objs['carton']

    for carton in cartons:
        plan += [
            ("goto", carton.name),
            ("pickup", carton.name)
        ]
    plan.append(("goto", "shelf_0"))
    for carton in cartons:
        plan += [
            ("drop_in", carton.name)
        ]
    for elem in plan:
        yield (ACTION_FUNC_MAPPING[elem[0]], env.obj_instances[elem[1]]) #type: ignore

def sorting_books(env):
    plan = []

    book = env.objs['book']
    hardback = env.objs['hardback']
    shelf = env.objs['shelf'][0]

    for obj in book + hardback:
        plan += [
            ("goto", obj.name),
            ("pickup", obj.name)
        ]
    plan.append(("goto", shelf.name))
    for obj in book + hardback:
        plan.append(("drop", obj.name))

    for elem in plan:
        yield (ACTION_FUNC_MAPPING[elem[0]], env.obj_instances[elem[1]]) #type: ignore

def watering_house_plants(env):
    plan = []

    plants = env.objs['pot_plant']

    for obj in plants:
        plan += [
            ("goto", obj.name),
            ("pickup", obj.name)
        ]

    plan += [
        ("goto", "sink_0"),
        ("toggle", "sink_0")
    ]

    for obj in plants:
        plan += [ ("drop_in", obj.name) ]

    for elem in plan:
        yield (ACTION_FUNC_MAPPING[elem[0]], env.obj_instances[elem[1]]) #type: ignore



task_to_plan = {
    'MiniGrid-BoxingBooksUpForStorage': boxing_books_up_for_storage,
    'MiniGrid-InstallingAPrinter': installing_a_printer,
    'MiniGrid-CollectMisplacedItems': collect_misplaced_items,
    'MiniGrid-SettingUpCandles': setting_up_candles,
    'MiniGrid-OpeningPackages': opening_packages,
    'MiniGrid-OrganizingFileCabinet': organizing_file_cabinet,
    'MiniGrid-StoringFood': storing_food,
    'MiniGrid-CleaningShoes': cleaning_shoes,
    'MiniGrid-CleaningACar': cleaning_a_car,
    'MiniGrid-MovingBoxesToStorage': moving_boxes_to_storage,
    'MiniGrid-SortingBooks': sorting_books,
    'MiniGrid-WateringHouseplants': watering_house_plants,
}
