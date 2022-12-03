import ray
from ray.rllib.algorithms import ppo
from ray.rllib.models import ModelCatalog
from ray.rllib.models.torch.torch_modelv2 import TorchModelV2
from mini_behavior.actions import get_allowable_action_strings
from collections import OrderedDict

import gym
from gym.spaces import Text, Tuple, Discrete, Sequence, Dict

from lm import SayCanOPT
from mini_behavior.envs import InstallingAPrinterEnv  # type: ignore
from ray.tune.registry import register_env

import numpy as np

chars = set("abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789_")


class Repeated(gym.Space):
    """Represents a variable-length list of child spaces.

    Example:
        self.observation_space = spaces.Repeated(spaces.Box(4,), max_len=10)
            --> from 0 to 10 boxes of shape (4,)

    See also: documentation for rllib.models.RepeatedValues, which shows how
        the lists are represented as batched input for ModelV2 classes.
    """

    def __init__(self, child_space: gym.Space, max_len: int):
        super().__init__()
        self.child_space = child_space
        self.max_len = max_len

    def sample(self):
        return [
            self.child_space.sample()
            for _ in range(self.np_random.integers(1, self.max_len + 1))
        ]

    def contains(self, x):
        return (
            isinstance(x, (list, np.ndarray))
            and len(x) <= self.max_len
            and all(self.child_space.contains(c) for c in x)
        )

    def __repr__(self):
        return "Repeated({}, {})".format(self.child_space, self.max_len)


class CompatibilityWrapper(gym.Env):
    def __init__(self, config, env):
        self.env = env(config)
        self.observation_space = Dict(
            {
                "available_actions": Repeated(
                    Tuple(
                        [
                            Text(max_length=50, charset=chars),
                            Text(max_length=50, charset=chars),
                        ]
                    ),
                    max_len=20,
                )
            }
        )

        self.action_space = Tuple(
            [Text(max_length=50, charset=chars), Text(max_length=50, charset=chars)]
        )

    def step(self, action):
        obs, reward, terminated, truncated, info = self.env(action)
        action_str = get_allowable_action_strings(self.env)
        obs = OrderedDict()
        obs["available_actions"] = action_str

        breakpoint()
        return obs, reward, terminated or truncated, info

    def reset(self):
        obs, info = self.env.reset()
        action_str = get_allowable_action_strings(self.env)
        obs = OrderedDict()
        obs["available_actions"] = action_str

        breakpoint()
        self.observation_space.contains(obs)
        return obs


class OptModel(TorchModelV2):
    def __init__(self, obs_space, action_space, num_outputs, model_config, name):
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


ModelCatalog.register_custom_model("opt_model", OptModel)

register_env(
    "MiniGrid-InstallingAPrinter-16x16-N2-v1",
    lambda cfg: CompatibilityWrapper(cfg, InstallingAPrinterEnv),
)

ray.init(local_mode=True)
algo = ppo.PPO(
    env="MiniGrid-InstallingAPrinter-16x16-N2-v1",
    config={
        "framework": "torch",
        "model": {
            "custom_model": "opt_model",
            # Extra kwargs to be passed to your model's c'tor.
            "custom_model_config": {},
        },
    },
)
