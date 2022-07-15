import numpy

import utils
from utils import device


# Parse arguments
env = 'MiniGrid-ThrowLeftoversMulti-16x16-N2-v0'
model = 'throw_leftovers_model'
seed = 0
shift = 0
argmax = False
pause = 0.1
gif = None
episodes = 1000000
memory = False
text = False

# Set seed for all randomness sources

utils.seed(seed)

# Set device

print(f"Device: {device}\n")

# Load environment

env = utils.make_env(env, seed)
for _ in range(shift):
    env.reset()
print("Environment loaded\n")

# Load agent

model_dir = utils.get_model_dir(model)
agent = utils.Agent(env.observation_space, env.action_space, model_dir,
                    argmax=argmax, use_memory=memory, use_text=text)
print("Agent loaded\n")

# Run the agent

if gif:
   from array2gif import write_gif
   frames = []

# Create a window to view the environment
env.render('human')

for episode in range(episodes):
    obs = env.reset()

    while True:
        env.render('human')
        if gif:
            frames.append(numpy.moveaxis(env.render("rgb_array"), 2, 0))

        action = agent.get_action(obs)
        obs, reward, done, _ = env.step(action)
        agent.analyze_feedback(reward, done)

        if done or env.window.closed:
            break

    if env.window.closed:
        break

if gif:
    print("Saving gif... ", end="")
    write_gif(numpy.array(frames), gif+".gif", fps=1/pause)
    print("Done.")
