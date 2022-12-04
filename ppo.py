import ray
from ray.rllib.algorithms import ppo
from ray.rllib.models import ModelCatalog
from ray.rllib.models.torch.torch_modelv2 import TorchModelV2
from mini_behavior.actions import get_allowable_action_strings
from collections import OrderedDict

import gym
from gym.spaces import Text, Tuple, Dict, Discrete

from lm import SayCanOPT
from mini_behavior.envs import InstallingAPrinterEnv  # type: ignore
from ray.tune.registry import register_env
from mini_behavior.actions import ACTION_FUNC_MAPPING
from ray.rllib.utils.spaces.repeated import Repeated
from torch import nn


def sample(self):
    return [
        self.child_space.sample()
        for _ in range(self.np_random.integers(1, self.max_len + 1))
    ]


Repeated.sample = sample

chars = set("abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789_")

class CompatibilityWrapper(gym.Env):
    def __init__(self, config, env):
        self.env = env(config)
        self.observation_space = Dict(
            {
                "available_actions": Repeated(
                    Tuple(
                        [
                            Discrete(20),
                            Discrete(20),
                            # Text(max_length=50, charset=chars),
                            # Text(max_length=50, charset=chars),
                        ]
                    ),
                    max_len=50,
                )
            }
        )

        self.action_space = Tuple([Discrete(len(ACTION_FUNC_MAPPING)), Discrete(20)])

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

        action_str = get_allowable_action_strings(self.env)
        obs = OrderedDict()
        # obs["available_actions"] = action_str
        obs["available_actions"] = [(0, 1)]
        return obs, reward, terminated or truncated, info

    def reset(self):
        obs, info = self.env.reset()
        action_str = get_allowable_action_strings(self.env)
        obs = OrderedDict()
        obs["available_actions"] = [(0, 1)]
        return obs


class OptModel(TorchModelV2, nn.Module):
    def __init__(self, obs_space, action_space, num_outputs, model_config, name):
        super().__init__(obs_space, action_space, num_outputs, model_config, name)
        # self.model_config = model_config
        # self.obs_space = obs_space
        # self.action_space = action_space
        # self.num_outputs = num_outputs
        # self.name = name
        self.lm = SayCanOPT(use_soft_prompt=True)

    def forward(self, input_dict, state, seq_lens):
        self.lm.initialize_task("test")
        breakpoint()
        affordances = []
        affordance_labels = []
        self.lm.get_action(affordances, affordance_labels)
        pass

    def value_function(self):
        breakpoint()
        pass

    def to(self, device):
        return self

    def get_initial_state(self):
        return []

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
