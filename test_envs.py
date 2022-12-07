import gymnasium as gym
import mini_behavior

from lm import SayCan, SayCanOPTCompat

envs = [
    'MiniGrid-BoxingBooksUpForStorage-16x16-N2-v1',
    'MiniGrid-InstallingAPrinter-16x16-N2-v1',
    'MiniGrid-CollectMisplacedItems-16x16-N2-v1',
    'MiniGrid-SettingUpCandles-16x16-N2-v1',
    'MiniGrid-OpeningPackages-16x16-N2-v1',
    'MiniGrid-OrganizingFileCabinet-16x16-N2-v1',
    'MiniGrid-StoringFood-16x16-N2-v1',
    'MiniGrid-CleaningShoes-16x16-N2-v1',
    'MiniGrid-MovingBoxesToStorage-16x16-N2-v1',
    'MiniGrid-CleaningACar-16x16-N2-v1',
    'MiniGrid-SortingBooks-16x16-N2-v1',
    'MiniGrid-WateringHouseplants-16x16-N2-v1',
    'MiniGrid-PuttingAwayDishesAfterCleaning-16x16-N2-v1',
    'MiniGrid-ThrowingAwayLeftoversFour-8x8-N2-v1',
    'MiniGrid-ThrowLeftoversSceneEnv-0x0-N2-v1',
    'MiniGrid-WashingPotsAndPans-16x16-N2-v1',
]

use_gpt = False

saycan = SayCanOPTCompat()
for env_str in envs:
    limit = 0
    env = gym.make(env_str)
    env.reset()
    if use_gpt:
        saycan = SayCan(env.mission)
    else:
        saycan.set_task(env.mission)


    while True:
        affordances, affordance_labels = env.affordances()
        action = saycan.get_action(affordances, affordance_labels)
        obs, reward, terminated, truncated, info = env.step(action)
        limit += 1

        if limit == 20 or terminated or truncated:
            print(env.mission)
            print(saycan.action_history)
            print(terminated, truncated, limit)
            break
