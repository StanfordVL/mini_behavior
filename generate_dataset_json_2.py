from mini_behavior.planning.tasks import task_to_plan
import gymnasium as gym
from lm import format_affordance_label, format_task_context
import numpy as np
import json

from mini_behavior.actions import ACTION_FUNC_MAPPING

ACTION_FUNC_TO_NAME = {v: k for k, v in ACTION_FUNC_MAPPING.items()}

MAX_PLAN_LENGTH = 15

dataset = []

for task_name in task_to_plan.keys():
    env_id = f'{task_name}-16x16-N2-v1'
    try:
        rng = np.random.default_rng()
        seed = rng.integers(int(1e6))
        env = gym.make(env_id)
        env.reset(seed=seed, options={})
    except:
        continue
    plan = list(task_to_plan[task_name](env))
    plan_text = [format_affordance_label((ACTION_FUNC_TO_NAME[affordance_chosen[0]], affordance_chosen[1].name)) for affordance_chosen in plan]
    mission = env.mission
    if len(plan) > MAX_PLAN_LENGTH:
        continue
    dataset.append({'affordance_labels': [], 'mission': mission})
    # dataset[env_id]['mission'] = env.mission
    for i, affordance_chosen in enumerate(plan):
        possible_affordances, possible_affordance_labels = env.affordances()
        # positive_label = format_affordance_label((ACTION_FUNC_TO_NAME[affordance_chosen[0]], affordance_chosen[1].name))
        positive_label = (ACTION_FUNC_TO_NAME[affordance_chosen[0]], affordance_chosen[1].name)
        # negative_labels = [format_affordance_label((ACTION_FUNC_TO_NAME[affordance[0]], affordance[1].name)) for affordance in possible_affordances if format_affordance_label((ACTION_FUNC_TO_NAME[affordance[0]], affordance[1].name)) != positive_label]
        context = format_task_context(env.mission, plan_text[:i])
        obs, reward, terminated, truncated, info = env.step(affordance_chosen)

        # dataset[env_id].append({})
        # dataset[env_id][i]['context'] = context
        dataset[-1]['affordance_labels'].append(positive_label)
        # dataset[env_id][i]['negative_labels'] = negative_labels
        # breakpoint()
    print(len(dataset[-1]['affordance_labels']))
print(dataset)
json.dump(dataset, open('behavior_cloning_dataset_2.json', 'w'))