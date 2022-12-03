import ray
from ray.rllib.algorithms import ppo
from ray.rllib.models import ModelCatalog
from ray.rllib.models.torch.torch_modelv2 import TorchModelV2

import gym
from gym.spaces import Text, Tuple, Discrete

from lm import SayCanOPT
from mini_behavior.envs import InstallingAPrinterEnv  # type: ignore
from ray.tune.registry import register_env

class CompatibilityWrapper(gym.Env):
    def __init__(self, config, env):
        breakpoint()
        self.env = env(config)
        self.observation_space = Text(max_length=1000)
        self.action_space 

        self.action_space = 
    def step(self, action):
        breakpoint()
        pass

class OptModel(TorchModelV2):
    def __init__(self, obs_space, action_space, num_outputs, model_config, name):
        breakpoint()
        # self.lm = SayCanOPT()
        pass

    def forward(self, input_dict, state, seq_lens):
        breakpoint()
        pass

    def value_function(self):
        breakpoint()
        pass


ModelCatalog.register_custom_model("opt_model", OptModel)

register_env('MiniGrid-InstallingAPrinter-16x16-N2-v1', lambda cfg: CompatibilityWrapper(cfg, InstallingAPrinterEnv))

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
