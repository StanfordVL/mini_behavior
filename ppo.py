from collections import OrderedDict

import gym
from gym.spaces import Dict, Discrete, MultiDiscrete, Tuple, Box
import numpy as np
import ray
from ray.rllib.algorithms import ppo
from ray.rllib.models import ModelCatalog
from ray.rllib.models.torch.torch_modelv2 import TorchModelV2
from ray.tune.registry import register_env
from torch import nn

from bddl.objs import OBJECT_TO_IDX
from lm import SayCanOPT
from mini_behavior.actions import get_allowable_action_strings
from mini_behavior.actions import ACTION_FUNC_MAPPING
from mini_behavior.envs import InstallingAPrinterEnv

IDX_TO_GOAL = {
    1: "install a printer",
}


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
        high[:, 0] = num_actions
        high[:, 1] = max_obj_types
        high[:, 2] = max_obj_instances

        self.observation_space = Dict(
            {
                "available_actions": Box(
                    low=low,
                    high=high,
                    dtype=int,
                ),
                "valid_plan": Discrete(self.max_plan_length),
                "goal": Discrete(num_missions),
            }
        )

        self.action_space = MultiDiscrete(
            [num_actions, max_obj_types, max_obj_instances]
        )

    @staticmethod
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
        return np.array(discretized_affordances), valid

    def obs_wrapper(self):
        action_str = get_allowable_action_strings(self.env)
        discretized_affordances, valid = self.discretize_affordances(
            action_str, pad_len=self.max_plan_length
        )
        obs = OrderedDict()
        # obs["available_actions"] = action_str
        obs["available_actions"] = discretized_affordances
        obs["valid_plan"] = valid
        obs["goal"] = 1
        return obs

    def step(self, action: tuple):

        action_type = list(ACTION_FUNC_MAPPING.values())[action[0]]
        if action[1] > len(self.env.obj_instances):
            reward = 0
            terminated = False
            truncated = False
            info = {}
        else:
            action = (action_type, list(self.env.obj_instances.values())[action[1]])
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
        breakpoint()
        action_idxs = []
        for actions, goal in zip(
            input_dict["obs"]["available_actions"], input_dict["obs"]["goal"]  # type: ignore
        ):
            goal_idx = goal.argmax().item()
            if goal_idx not in IDX_TO_GOAL:
                goal_idx = 1
            self.lm.initialize_task(IDX_TO_GOAL[goal_idx])
            breakpoint()
            action_idx = self.lm.get_action(actions)
            action_idxs.append(action_idx)
        return input_dict["obs"]["available_actions"][action_idx]

    @staticmethod
    def undiscretize_affordances(affordances, valid):
        affordances = affordances[:valid]
        text_affordances = []
        for affordance in affordances:
            action = affordance[0]
            breakpoint()
            obj_type = affordances[1]
            obj_instance = affordance[2]

            text_affordances.append((action_str, f"{obj_str}_{obj_instance}"))
        return text_affordances

    def value_function(self):
        breakpoint()
        pass

    def to(self, device):
        return self

    def parameters(self):
        return self.lm.model.get_input_embeddings().parameters()

    def eval(self):
        pass


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
