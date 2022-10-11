from csv import reader
import json

path = "/Users/emilyjin/Downloads/20 BEHAVIOR Activities - obj_actions (3).csv"
out_file = "mini_behavior/utils/object_actions.json"
obj_actions = {}

with open(path, 'r') as f:
    csv_reader = reader(f)

    actions = ['pickup', 'drop', 'drop_in', 'toggle', 'open', 'close', 'slice', 'cook']
    rows = [row for row in csv_reader]
    for row in rows[2:]:
        actions_list = []
        row_actions = row[1:]
        for i in range(len(actions)):
            if row_actions[i] == 'x':
                actions_list.append(actions[i])

        obj_actions[row[0]] = actions_list
        print(f'{row[0]}: {obj_actions[row[0]]}')

with open(out_file, 'w') as f:
    json.dump(obj_actions, f, sort_keys=True, indent=4, separators=(',', ': '))
