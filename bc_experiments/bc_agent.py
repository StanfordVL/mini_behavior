import torch

import torch.nn as nn
import numpy as np


class Agent:
    """An agent.

    It is able:
    - to choose an action given an observation,
    - to analyze the feedback (i.e. reward and done state) of its action."""

    def __init__(self, obs_space, action_space, model_path):

        obs_space_size = len(obs_space)
        action_space_size = action_space.n

        self.model = nn.Sequential(
            nn.Linear(obs_space_size, 32),
            nn.ReLU(),

            nn.Linear(32, 64),
            nn.ReLU(),

            nn.Linear(64, 100),
            nn.ReLU(),

            nn.Linear(100, 256),
            nn.ReLU(),

            nn.Linear(256, 100),
            nn.ReLU(),

            nn.Linear(100, 64),
            nn.ReLU(),

            nn.Linear(64, 32),
            nn.ReLU(),

            nn.Linear(32, action_space_size),
            # nn.Softmax()
        )

        self.model = torch.load(model_path)
        device = torch.device("cuda:0" if torch.cuda.is_available() else "cpu")
        self.model.to(device)

        self.model.eval()

    def get_action(self, obs):
        input = np.array([obs['agent_x'], obs['agent_y'], obs['agent_dir'], obs['printer_inhandofrobot'], obs['printer_toggledon'], obs['printer_ontop_table']])
        input = torch.tensor(input.astype(np.float32))
        with torch.no_grad():
            output = self.model(input)

        action = torch.argmax(output)
        action = int(action.cpu())

        return action
