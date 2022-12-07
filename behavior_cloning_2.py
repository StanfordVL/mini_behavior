import numpy as np
from transformers import AutoModelForCausalLM, AutoTokenizer
import torch
import math
import json
import random

from lm import SoftEmbedding
import torch
from tensorboardX import SummaryWriter

DEVICE = "cuda" if torch.cuda.is_available() else "cpu"

SAYCAN_PROMPT = """You are a robotic task planner.
Task: {}
Plan:"""


class SayCanOPT:
    def __init__(self, task, use_soft_prompt=True):
        self.task = task
        self.action_history = []
        # self.model = AutoModelForCausalLM.from_pretrained("facebook/opt-6.7b", torch_dtype=torch.float16).to(DEVICE)
        # self.tokenizer = AutoTokenizer.from_pretrained("facebook/opt-6.7b", use_fast=False)
        self.model = AutoModelForCausalLM.from_pretrained(
            "facebook/opt-350m"#, torch_dtype=torch.float16
        ).to(DEVICE)
        self.tokenizer = AutoTokenizer.from_pretrained(
            "facebook/opt-350m", use_fast=False
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

    def train_step(self, affordances, affordance_labels):
        logits = torch.zeros(len(affordances))
        labels = []
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
    logits = torch.zeros(plan_length, plan_length)
    for idx in range(plan_length):
        step_logits = model.train_step(affordances, affordance_labels)
        logits[idx] = step_logits
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
    dataset_train_task = random.choice(dataset[:-1])
    dataset_test_task = dataset[-1]

    original_task = dataset_train_task['mission']
    test_task = dataset_test_task['mission']
    lm = SayCanOPT(task=original_task)
    affordance_labels = dataset_train_task['affordance_labels']
    affordances = list(range(len(affordance_labels)))
    true_plan = list(range(len(affordance_labels)))

    test_affordance_labels = dataset_test_task['affordance_labels']
    test_affordances = list(range(len(test_affordance_labels)))
    test_true_plan = list(range(len(test_affordance_labels)))
    test_plan_length = len(test_affordances)

    true_logits = torch.nn.functional.one_hot(torch.tensor(true_plan), len(affordances)).float()
    test_true_logits = torch.nn.functional.one_hot(torch.tensor(test_true_plan), len(affordances)).float()

    parameters = lm.model.get_input_embeddings().parameters()
    optimizer = torch.optim.Adam(parameters, lr=1e-4)
    optimizer.zero_grad()

    writer = SummaryWriter()
    plan_length = len(affordances)
    for i in range(1000):
        print(i)

        loss, logits = train_step(optimizer, lm, plan_length, affordances, affordance_labels, true_logits)
        predicted_plan = torch.argmax(logits, dim=1)
        acc = (predicted_plan == torch.tensor(true_plan)).float().mean()
        print(f"Plan accuracy {acc}")
        writer.add_scalar('plan-accuracy/train', acc, i)
        print(f"Loss: {loss}")
        writer.add_scalar('loss/train', loss, i)
        print(f"Predicted plan: {predicted_plan}")

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
