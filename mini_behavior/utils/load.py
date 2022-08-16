import json
import os


def load_json(filename):
    path = os.path.abspath(filename)
    with open(path, 'r') as f:
        return json.load(f)
