import gym
from gym_minigrid.wrappers import ImgObsWrapper
from mini_behavior.utils.wrappers import MiniBHFullyObsWrapper
import mini_behavior
from stable_baselines3 import PPO
import numpy as np
from stable_baselines3.common.env_util import make_vec_env
from stable_baselines3.common.torch_layers import BaseFeaturesExtractor
import torch.nn as nn
import torch

partial_obs = True

class MinigridFeaturesExtractor(BaseFeaturesExtractor):
    def __init__(self, observation_space: gym.Space, features_dim: int = 512, normalized_image: bool = False) -> None:
        super().__init__(observation_space, features_dim)
        n_input_channels = observation_space.shape[0]
        self.cnn = nn.Sequential(
            nn.Conv2d(n_input_channels, 32, (2, 2)),
            nn.ReLU(),
            nn.Conv2d(32, 32, (2, 2)),
            nn.ReLU(),
            nn.Conv2d(32, 64, (2, 2)),
            nn.ReLU(),
            nn.Flatten(),
        )

        # Compute shape by doing one forward pass
        with torch.no_grad():
            n_flatten = self.cnn(torch.as_tensor(observation_space.sample()[None]).float()).shape[1]

        self.linear = nn.Sequential(nn.Linear(n_flatten, features_dim), nn.ReLU())

    def forward(self, observations: torch.Tensor) -> torch.Tensor:
        return self.linear(self.cnn(observations))

policy_kwargs = dict(
    features_extractor_class=MinigridFeaturesExtractor,
    features_extractor_kwargs=dict(features_dim=128),
)

# Env wrapping
env = gym.make("MiniGrid-InstallingAPrinter-6x6-N2-v0")
if not partial_obs:
    env = MiniBHFullyObsWrapper(env)
env = ImgObsWrapper(env)

# Policy training
model = PPO("CnnPolicy", env, policy_kwargs=policy_kwargs, verbose=1, tensorboard_log="./logs/")
model.learn(1e6)

if not partial_obs:
    model.save("model/ppo_cnn")
else:
    model.save("model/ppo_partial")
