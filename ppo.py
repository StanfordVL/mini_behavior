from collections import OrderedDict

import gym
from gym.spaces import Dict, Discrete, Box
import numpy as np
import ray
from ray.rllib.algorithms import ppo
from ray.rllib.models import ModelCatalog
from ray.rllib.models.torch.torch_modelv2 import TorchModelV2
from ray.tune.registry import register_env
from torch import nn
import torch

from bddl.objs import OBJECT_TO_IDX
from lm import SayCanOPT
from mini_behavior.actions import get_allowable_action_strings
from mini_behavior.actions import ACTION_FUNC_MAPPING
from mini_behavior.envs import InstallingAPrinterEnv

ACTION_FUNC_IDX = {idx: val for idx, val in enumerate(ACTION_FUNC_MAPPING)}
IDX_TO_OBJECT = {val: idx for idx, val in OBJECT_TO_IDX.items()}

IDX_TO_GOAL = {
    1: "install a printer",
}


def discretize_affordances(affordances, pad_len=None):
    discretized_affordances = []
    for affordance in affordances:
        action = affordance[0]
        obj_type, obj_instance = affordance[1].split("_")

        obj_instance = int(obj_instance)
        discretized_obj_type = OBJECT_TO_IDX[obj_type]
        discretized_action = list(ACTION_FUNC_MAPPING).index(action)

        discretized_affordances.append(
            [discretized_action, discretized_obj_type, obj_instance]
        )
    # mask = [1] * len(discretized_affordances)
    valid = len(discretized_affordances)

    if pad_len:
        to_pad = pad_len - len(discretized_affordances)
        discretized_affordances = discretized_affordances + [[0, 0, 0]] * to_pad
        # mask = mask + [0] * to_pad
    return np.array(discretized_affordances, dtype=int), valid


def undiscretize_affordances(affordances, valid):
    affordances = affordances[:valid]
    text_affordances = []
    for affordance in affordances:
        action = affordance[0].item()
        obj_type = affordance[1].item()
        obj_instance = affordance[2].item()

        action_str = ACTION_FUNC_IDX[action]
        obj_str = IDX_TO_OBJECT[obj_type]

        text_affordances.append((action_str, f"{obj_str}_{obj_instance}"))
    return text_affordances


class CompatibilityWrapper(gym.Env):
    def __init__(self, config, env):
        self.env = env(config)
        num_actions = len(ACTION_FUNC_MAPPING)
        max_obj_types = max(OBJECT_TO_IDX.values())
        max_obj_instances = 20
        self.max_plan_length = 20
        num_missions = 3
        low = np.zeros((20, 3))
        high = np.zeros((20, 3))
        high[:, 0] = num_actions - 1
        high[:, 1] = max_obj_types
        high[:, 2] = max_obj_instances

        self.observation_space = Dict(
            {
                "available_actions": Box(
                    low=low,
                    high=high,
                    dtype=int,
                ),
                "valid_plan": Discrete(20),
                "goal": Discrete(20),
            }
        )
        # self.action_space = Tuple((
        #     Box(
        #         low=low,
        #         high=high,
        #         dtype=int,
        #     ),
        #     Box(low=0, high=self.max_plan_length, dtype=int)))
        # self.action_space = Box(
        #         low=low,
        #         high=high,
        #         dtype=int,
        #     )
        self.possible_actions =num_actions * max_obj_types * max_obj_instances
        self.action_space = Discrete(self.possible_actions)
        # self.action_space = MultiDiscrete(
        #     [num_actions, max_obj_types, max_obj_instances]
        # )

        # self.action_space = MultiDiscrete(
        #     [num_actions, max_obj_types, max_obj_instances]
        # )

    def obs_wrapper(self):
        action_str = get_allowable_action_strings(self.env)
        discretized_affordances, valid = discretize_affordances(
            action_str, pad_len=self.max_plan_length
        )
        obs = OrderedDict()
        # obs["available_actions"] = action_str
        obs["available_actions"] = discretized_affordances
        obs["valid_plan"] = valid
        obs["goal"] = 1
        return obs

    def convert_text_to_action(self):
        pass

    def step(self, action):
        # text_actions = undiscretize_affordances(action, valid=len(action))
        # text_actions = undiscretize_affordances(action[0], action[1].item())
        reward = 0
        terminated = False
        truncated = True
        info = {}

        action_str = get_allowable_action_strings(self.env)
        # for text_action in text_actions:
        #     action_type = ACTION_FUNC_MAPPING[text_action[0]]
        #     if text_action[1] not in self.env.obj_instances:
        #         break
        #     else:
        #         obj = self.env.obj_instances[text_action[1]]
        #         action = (action_type, obj)
        #         obs, reward, terminated, truncated, info = self.env.step(action)
       
        if action < len(action_str):
            action = action_str[action]
            action_type = ACTION_FUNC_MAPPING[action[0]]
            obj = self.env.obj_instances[action[1]]
            action = (action_type, obj)
            obs, reward, terminated, truncated, info = self.env.step(action)
        obs = self.obs_wrapper()
        return obs, reward, terminated or truncated, info

    def reset(self):
        obs, _ = self.env.reset()
        obs = self.obs_wrapper()
        return obs


class OptModel(TorchModelV2, nn.Module):
    def __init__(self, obs_space, action_space, num_outputs, model_config, name):
        super().__init__(obs_space, action_space, num_outputs, model_config, name)
        self.lm = SayCanOPT(use_soft_prompt=True)

    def forward(self, input_dict, state, seq_lens):

        available_actions = input_dict["obs"]["available_actions"].int()  # type: ignore
        goal = input_dict["obs"]["goal"].int()  # type: ignore
        valid_plan = input_dict["obs"]["valid_plan"].int()  # type: ignore

        selected_actions = []

        for actions, goal, valid in zip(available_actions, goal, valid_plan):
            goal_idx = goal.argmax().item()
            if goal_idx not in IDX_TO_GOAL:
                goal_idx = 1
                valid = torch.tensor([0, 1])
            self.lm.initialize_task(IDX_TO_GOAL[goal_idx])
            text_actions = undiscretize_affordances(actions, valid.argmax())  # type: ignore
            action_idx = self.lm.get_action(text_actions)
            selected_actions.append(action_idx)

        return torch.tensor(selected_actions).reshape(-1, 1).cuda(), []

    def value_function(self):
        # https://github.com/openai/summarize-from-feedback/blob/master/summarize_from_feedback/reward_model.py
        return self.lm.get_reward()

    def to(self, device):
        return self

    def train(self):
        self.lm.model.train()
        return self

    def parameters(self):
        return self.lm.model.get_input_embeddings().parameters()

    def eval(self):
        self.lm.model.eval()
        return self


ModelCatalog.register_custom_model("opt_model", OptModel)

register_env(
    "MiniGrid-InstallingAPrinter-16x16-N2-v1",
    lambda cfg: CompatibilityWrapper(cfg, InstallingAPrinterEnv),
)

# ray.init(local_mode=True)
ray.init()
algo = ppo.PPO(
    env="MiniGrid-InstallingAPrinter-16x16-N2-v1",
    config={
        "framework": "torch",
        "model": {
            "custom_model": "opt_model",
            # Extra kwargs to be passed to your model's c'tor.
            "custom_model_config": {},
        },
        # "preprocessor_pref": None,
        "num_gpus": 1,
        "num_workers": 0,
        # "num_gpus_per_worker": 1,
    },
)
for i in range(1000):
   # Perform one iteration of training the policy with PPO
   result = algo.train()
   print(pretty_print(result))

   if i % 100 == 0:
       checkpoint = algo.save()
       print("checkpoint saved at", checkpoint)
