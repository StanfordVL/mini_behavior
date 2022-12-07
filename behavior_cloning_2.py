import numpy as np
from transformers import AutoModelForCausalLM, AutoTokenizer
import torch
import math
import json
import random
import argparse
import gymnasium as gym
import mini_behavior.envs

from lm import SoftEmbedding
import torch
from tensorboardX import SummaryWriter

DEVICE = "cuda" if torch.cuda.is_available() else "cpu"

SAYCAN_PROMPT = """You are a robotic task planner.
Task: {}
Plan:"""


class SayCanOPT:
    def __init__(self, task, model_name, use_soft_prompt=True):
        self.task = task
        self.action_history = []
        # self.model = AutoModelForCausalLM.from_pretrained("facebook/opt-6.7b", torch_dtype=torch.float16).to(DEVICE)
        # self.tokenizer = AutoTokenizer.from_pretrained("facebook/opt-6.7b", use_fast=False)
        self.model = AutoModelForCausalLM.from_pretrained(
            model_name#, torch_dtype=torch.float16
        ).to(DEVICE)
        self.tokenizer = AutoTokenizer.from_pretrained(
            model_name, use_fast=False
        )

        self.use_soft_prompt = use_soft_prompt
        if use_soft_prompt:
            n_tokens = 20
            self.n_tokens = n_tokens
            initialize_from_vocab = True

            s_wte = SoftEmbedding(
                self.model.get_input_embeddings(),
                n_tokens=n_tokens,
                initialize_from_vocab=initialize_from_vocab,
            )
            self.model.set_input_embeddings(s_wte)

        print("SayCan initialized with task:", task)

    def get_action(self, affordance_labels):
        affordance_likelihoods = []
        for label in affordance_labels:
            label_obj = label[1]
            label_action = (
                label[0]
                .replace("goto", "go to")
                .replace("pickup", "pick up")
                .replace("putdown", "put down")
                .replace("drop_in", "drop in")
            )
            label_str = " ".join([label_action, "the", label_obj])
            prompt = self.get_prompt_from_history() + label_str
            breakpoint()
            affordance_likelihoods.append(self.get_text_likelihood(prompt))
        return max(range(len(affordance_likelihoods)), key=lambda i: affordance_likelihoods[i])

    def get_prompt_from_history(self):
        prompt = SAYCAN_PROMPT.format(self.task)
        i = 1
        if self.action_history:
            for action in self.action_history:
                prompt += f"\n{i}. {action}"
                i += 1
        prompt += f"\n{i}. "
        return prompt

    def get_text_likelihood(self, prompt):
        print(prompt)
        input_ids = self.tokenizer(prompt, return_tensors="pt").input_ids.to(DEVICE)

        if self.use_soft_prompt:
            input_ids = torch.cat(
                [torch.full((1, self.n_tokens), 50256).to(DEVICE), input_ids], 1
            )

        outputs = self.model(input_ids, labels=input_ids)
        # sentence_prob = outputs['logits'].max(dim=2).values.sum()

        return -math.exp(outputs["loss"].item())

    def train_step(self, affordances, affordance_labels, skip=False):
        logits = torch.zeros(len(affordances))
        labels = []
        # if not skip:
        for idx, label in enumerate(affordance_labels):
            label_obj = label[1]
            label_action = (
                label[0]
                .replace("goto", "go to")
                .replace("pickup", "pick up")
                .replace("putdown", "put down")
                .replace("drop_in", "drop in")
            )
            label_str = " ".join([label_action, "the", label_obj])
            prompt = self.get_prompt_from_history() + label_str
            labels.append(label_str)
            # breakpoint()

            input_ids = self.tokenizer(prompt, return_tensors="pt").input_ids.to(DEVICE)

            if self.use_soft_prompt:
                input_ids = torch.cat(
                    [torch.full((1, self.n_tokens), 50256).to(DEVICE), input_ids], 1
                )

            outputs = self.model(input_ids, labels=input_ids)
            # sentence_prob = outputs['logits'].max(dim=2).values.sum()

            logits[idx] = -torch.exp(outputs["loss"])

        idx = torch.argmax(logits)
        self.action_history.append(labels[idx])
        return logits

def train_step(optimizer, model, plan_length, affordances, affordance_labels, true_logits, test=False):
    # num_not_skipped = 5 if not test else plan_length
    logits = torch.zeros(plan_length, plan_length)
    # skipped_steps = np.random.choice(plan_length, plan_length - num_not_skipped, replace=False)
    # idx_with_skips = 0
    for idx in range(plan_length):
        # if idx in skipped_steps:
            # step_logits = model.train_step(affordances, affordance_labels, skip=True)
        # else:
        step_logits = model.train_step(affordances, affordance_labels)
        logits[idx] = step_logits
        # idx_with_skips += 1
    loss = torch.nn.functional.cross_entropy(logits, true_logits)

    if not test:
        loss.backward()
        optimizer.step()
        optimizer.zero_grad()
    model.action_history = []
    return loss, logits

# tasks = {
#  "install_printer": [
#         ("pickup", "printer_0"),
#         ("toggle", "printer_0"),
#         ("goto", "printer_0"),
#         ("goto", "table_0"),
#         ("putdown", "printer_0"),
#     ]

# }
dataset = json.loads(open("behavior_cloning_dataset_2.json").read())
if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--model_name", type=str, default="facebook/opt-125m")
    parser.add_argument("--max_length", type=int, default=10)
    args = parser.parse_args()
    model_name = args.model_name
    max_length = args.max_length

    dataset_test_task = dataset[0]
    dataset_train = dataset[1:]

    test_task = dataset_test_task['mission']
    lm = SayCanOPT(model_name=model_name, task='')

    test_affordance_labels = dataset_test_task['affordance_labels'][:max_length]
    test_affordances = list(range(len(test_affordance_labels)))
    test_true_plan = list(range(len(test_affordance_labels)))
    test_plan_length = len(test_affordances)

    test_true_logits = torch.nn.functional.one_hot(torch.tensor(test_true_plan), len(test_affordances)).float()

    parameters = lm.model.get_input_embeddings().parameters()
    optimizer = torch.optim.Adam(parameters, lr=1e-4)
    optimizer.zero_grad()

    writer = SummaryWriter()
    for i in range(1000):
        print(i)

        random.shuffle(dataset_train)
        avg_acc = 0
        avg_solved = 0
        for dataset_train_task in dataset_train:
            original_task = dataset_train_task['mission']
            lm.task = original_task

            affordance_labels = dataset_train_task['affordance_labels'][:max_length]
            affordances = list(range(len(affordance_labels)))
            true_plan = list(range(len(affordance_labels)))
            plan_length = len(affordances)

            true_logits = torch.nn.functional.one_hot(torch.tensor(true_plan), len(affordances)).float()

            loss, logits = train_step(optimizer, lm, plan_length, affordances, affordance_labels, true_logits)
            predicted_plan = torch.argmax(logits, dim=1)
            acc = (predicted_plan == torch.tensor(true_plan)).float().mean()
            avg_acc += acc
            avg_solved += (acc == 1).float()
            print(f"Plan accuracy {acc}")
            writer.add_scalar('plan-accuracy/train', acc, i)
            print(f"Loss: {loss}")
            writer.add_scalar('loss/train', loss, i)
            print(f"Predicted plan: {predicted_plan}")
        avg_acc /= len(dataset_train)
        avg_solved /= len(dataset_train)
        print(f"Average plan accuracy {avg_acc}")
        print(f"Average proportion solved {avg_solved}")

        if i % 10 == 0:
            lm.task = test_task
            loss, logits = train_step(optimizer, lm, test_plan_length, test_affordances, test_affordance_labels, test_true_logits, test=True)
            predicted_plan = torch.argmax(logits, dim=1)
            acc = (predicted_plan == torch.tensor(test_true_plan)).float().mean()
            print(f"Test plan accuracy {acc}")
            writer.add_scalar('plan-accuracy/test', acc, i)
            print(f"Loss: {loss}")
            writer.add_scalar('loss/test', loss, i)
            lm.task = original_task
    
    # measure the success rate on n_rollouts of the test task
    # n_rollouts = 10
    # lm.task = test_task
    # success_rate = 0
    # rng = np.random.default_rng()
    # seed = rng.integers(int(1e6))
    # env = gym.make(dataset_test_task['env_id'])
    # for i in range(n_rollouts):
    #     env.reset(seed=seed, options={})
    #     while True:
    #         affordances, affordance_labels = env.affordances()
    #         action = lm.get_action(affordances, affordance_labels)

    #         obs, reward, terminated, truncated, info = env.step(action)

    #         print('step=%s, reward=%.2f' % (env.step_count, reward))

    #         if terminated or truncated:
    #             break
    #     # success_rate += lm.rollout()
    # success_rate /= n_rollouts
    # print(f"Success rate: {success_rate}")
