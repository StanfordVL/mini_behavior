import json
from gym_minigrid.objects import _OBJECTS


infile = "synsets_to_filtered_properties_pruned_igibson.json"
outfile = "object_properties.json"

obj_properties = {}

with open(infile, 'r') as f:
    objs_dict = json.load(f)
    obj_names = {obj.split('.')[0]: obj for obj in objs_dict.keys()}

    for obj in _OBJECTS:
        obj_name = obj_names[obj]
        obj_properties[obj] = objs_dict[obj_name]

print(obj_properties)

all_properties = set()
for properties in obj_properties.values():
    for prop in properties.keys():
        all_properties.add(prop)

print(all_properties)

obj_properties['all'] = list(all_properties)

with open(outfile, 'w') as f:
    json.dump(obj_properties, f, sort_keys=True, indent=4, separators=(',', ': '))


property_objs = {}
for prop in all_properties:
    objs = []
    for obj in _OBJECTS:
        if prop in obj_properties[obj].keys():
            objs.append(obj)
    property_objs[prop] = objs

property_objs['all'] = _OBJECTS

outfile = "property_objects.json"
print(property_objs)
with open(outfile, 'w') as f:
    json.dump(property_objs, f, sort_keys=True, indent=4, separators=(',', ': '))