from collections import OrderedDict

import gym
from gym.spaces import Box, Dict, Tuple, Discrete
import numpy as np
import ray
from ray.rllib.algorithms import ppo
from ray.rllib.models import ModelCatalog
from ray.rllib.models.torch.torch_modelv2 import TorchModelV2
from ray.rllib.policy.view_requirement import ViewRequirement
from ray.tune.logger import pretty_print
from ray.tune.registry import register_env
from torch import nn

from bddl.objs import OBJECT_TO_IDX
from lm import SayCanOPT
from mini_behavior.actions import get_allowable_action_strings
from mini_behavior.actions import ACTION_FUNC_MAPPING
from mini_behavior.envs import InstallingAPrinterEnv
from utils import discretize_affordances, ACTION_FUNC_IDX, IDX_TO_OBJECT, IDX_TO_GOAL


class CompatibilityWrapper(gym.Env):
    def __init__(self, config, env):
        self.env = env(config)
        actions = len(ACTION_FUNC_MAPPING)
        obj_types = max(OBJECT_TO_IDX.values())
        obj_instances = 10
        self.max_actions = 20
        self.max_action_history = 20

        self.action_history = np.zeros((self.max_action_history, 3))
        self.cur_idx = 0

        self.action_space = Tuple(
            [Discrete(actions), Discrete(obj_types), Discrete(obj_instances)]
        )
        self.observation_space = Dict(
            {
                "available_actions": Box(
                    low=np.array([[0, 0, 0]] * self.max_actions),
                    high=np.array([[actions, obj_types, obj_instances]] * self.max_actions),
                    dtype=int,
                ),
                "action_history": Box(
                    low=np.array([[0, 0, 0]] * self.max_action_history),
                    high=np.array([[actions, obj_types, obj_instances]] * self.max_action_history),
                    dtype=int,
                ),
                "valid_plan": Box(low=0, high=20, dtype=int),
                "goal": Box(low=0, high=20, dtype=int),
            }
        )

    def obs_wrapper(self):
        action_str = get_allowable_action_strings(self.env)
        discretized_affordances, valid = discretize_affordances(
            action_str, pad_len=self.max_actions
        )
        obs = OrderedDict()
        obs["available_actions"] = discretized_affordances
        obs["action_history"] = self.action_history.copy()
        obs["valid_plan"] = np.array([valid], dtype=int)
        obs["goal"] = np.array([1], dtype=int)
        return obs

    def step(self, action):
        self.action_history[self.cur_idx] = action
        self.cur_idx += 1
        reward = 0
        terminated = False
        truncated = True
        info = {}

        action_type = ACTION_FUNC_IDX[action[0]]  # type: ignore
        obj_type = IDX_TO_OBJECT[action[1]]  # type: ignore
        obj_instance = action[2]  # type: ignore
        obj_str = f"{obj_type}_{obj_instance}"

        if obj_str in self.env.obj_instances:
            if action_type.can(self.env.obj_instances[obj_str]):
                action = (action_type, self.env.obj_instances[obj_str])
                obs, reward, terminated, truncated, info = self.env.step(action)

        obs = self.obs_wrapper()
        if self.cur_idx > self.max_action_history:
            truncated = True
        return obs, reward, terminated or truncated, info

    def reset(self):
        obs, _ = self.env.reset()
        obs = self.obs_wrapper()
        self.action_history = np.zeros((self.max_action_history, 3))
        self.cur_idx = 0
        return obs


class OptModel(TorchModelV2, nn.Module):
    def __init__(self, obs_space, action_space, num_outputs, model_config, name):
        TorchModelV2.__init__(
            self, obs_space, action_space, num_outputs, model_config, name
        )
        nn.Module.__init__(self)

        self.lm = SayCanOPT(use_soft_prompt=True)

    def forward(self, input_dict, state, seq_lens):

        available_actions = input_dict["obs"]["available_actions"]  # type: ignore
        batch_goal = input_dict["obs"]["goal"]  # type: ignore
        batch_valid = input_dict["obs"]["valid_plan"].int()  # type: ignore

        batch_size = available_actions.shape[0]

        chosen_actions = []
        for batch_idx in range(batch_size):
            goal = int(batch_goal[batch_idx].item())
            valid = int(batch_valid[batch_idx].item())

            # Dummy for initializing model
            if goal not in IDX_TO_GOAL or valid == 0:
                self.lm.initialize_task(IDX_TO_GOAL[0])
                action_idx = self.lm.get_action([("dummy", "object")])
                chosen_actions.append((0, 0, 0))
            else:
                breakpoint()
                self.lm.initialize_task(IDX_TO_GOAL[goal])  # type: ignore

                actions = []
                for action_candidate in available_actions:
                    (
                        batch_action_type,
                        batch_obj_type,
                        batch_obj_instance,
                    ) = action_candidate
                    action_type = batch_action_type[batch_idx]
                    obj_type = batch_obj_type[batch_idx]
                    obj_instance = batch_obj_instance[batch_idx]
                    action = (action_type, obj_type, obj_instance)
                    actions.append(action)

                text_actions = undiscretize_affordances(actions, valid.item())  # type: ignore
                action_idx = self.lm.get_action(text_actions)
                chosen_actions.append(actions[action_idx])

        processed_actions = []
        for action in chosen_actions:
            idx_0, idx_1, idx_2 = action
            one_hot_0 = np.eye(self.action_space[0].n)[idx_0]  # type: ignore
            one_hot_1 = np.eye(self.action_space[1].n)[idx_1]  # type: ignore
            one_hot_2 = np.eye(self.action_space[2].n)[idx_2]  # type: ignore
            one_hot = np.hstack([one_hot_0, one_hot_1, one_hot_2])
            processed_actions.append(one_hot)

        processed_actions = np.array(processed_actions)
        return processed_actions, []

    def value_function(self):
        # https://github.com/openai/summarize-from-feedback/blob/master/summarize_from_feedback/reward_model.py
        return self.lm.get_reward()


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
        "sgd_minibatch_size": 4,
        "train_batch_size": 16,
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
