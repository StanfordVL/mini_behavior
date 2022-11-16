import numpy as np
from transformers import AutoModelForCausalLM, AutoTokenizer
import torch
import math

from lm import SoftEmbedding
import torch

SAYCAN_PROMPT = """You are a robotic task planner.
Task: {}
Plan:"""


class SayCanOPT:
    def __init__(self, task, use_soft_prompt=True):
        self.task = task
        self.action_history = []
        # self.model = AutoModelForCausalLM.from_pretrained("facebook/opt-6.7b", torch_dtype=torch.float16).cuda()
        # self.tokenizer = AutoTokenizer.from_pretrained("facebook/opt-6.7b", use_fast=False)
        self.model = AutoModelForCausalLM.from_pretrained(
            "facebook/opt-350m", torch_dtype=torch.float16
        ).cuda()
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

    def get_action(self, affordances, affordance_labels):
        affordance_likelihoods = {}
        max_likelihood = -np.inf
        best_affordance = None
        best_label_str = None
        for affordance, label in zip(affordances, affordance_labels):
            label_obj = " ".join(label[1].split("_")[:-1])
            label_action = (
                label[0]
                .replace("goto", "go to")
                .replace("pickup", "pick up")
                .replace("putdown", "put down")
                .replace("drop_in", "drop in")
            )
            label_str = " ".join([label_action, "the", label_obj])
            prompt = self.get_prompt_from_history() + label_str
            affordance_likelihoods[label] = self.get_text_likelihood(prompt)
            if affordance_likelihoods[label] > max_likelihood:
                max_likelihood = affordance_likelihoods[label]
                best_affordance = affordance
                best_label_str = label_str
        self.action_history.append(best_label_str)
        print(affordance_likelihoods, best_label_str)
        return best_affordance

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
        input_ids = self.tokenizer(prompt, return_tensors="pt").input_ids.cuda()

        if self.use_soft_prompt:
            input_ids = torch.cat(
                [torch.full((1, self.n_tokens), 50256).cuda(), input_ids], 1
            )

        outputs = self.model(input_ids, labels=input_ids)
        # sentence_prob = outputs['logits'].max(dim=2).values.sum()

        return -math.exp(outputs["loss"].item())

    def train_step(self, affordances, affordance_labels):
        logits = torch.zeros(len(affordances))
        labels = []
        for idx, label in enumerate(affordance_labels):
            label_obj = " ".join(label[1].split("_")[:-1])
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

            input_ids = self.tokenizer(prompt, return_tensors="pt").input_ids.cuda()

            if self.use_soft_prompt:
                input_ids = torch.cat(
                    [torch.full((1, self.n_tokens), 50256).cuda(), input_ids], 1
                )

            outputs = self.model(input_ids, labels=input_ids)
            # sentence_prob = outputs['logits'].max(dim=2).values.sum()

            logits[idx] = -torch.exp(outputs["loss"])

        idx = torch.argmax(logits)
        self.action_history.append(idx)
        return logits


if __name__ == "__main__":
    lm = SayCanOPT(task="Pickup the printer from the floor, put it on the table, and turn it on")
    affordance_labels = [
        ("pickup", "printer_0"),
        ("toggle", "printer_0"),
        ("goto", "printer_0"),
        ("goto", "table_0"),
        ("putdown", "printer_0"),
    ]
    affordances = [0, 1, 2, 3, 4]
    true_plan = [2, 0, 3, 4, 1]
    true_logits = torch.nn.functional.one_hot(torch.tensor(true_plan), len(affordances)).float()

    parameters = lm.model.get_input_embeddings().parameters()
    optimizer = torch.optim.Adam(parameters, lr=1e-8)
    optimizer.zero_grad()

    plan_length = len(affordances)
    for _ in range(100):

        logits = torch.zeros(plan_length, plan_length)
        predicted_plan = []
        for idx in range(plan_length):
            step_logits = lm.train_step(affordances, affordance_labels)
            logits[idx] = step_logits

        loss = torch.nn.functional.cross_entropy(logits, true_logits)

        acc = (np.array(predicted_plan) == np.array(true_plan)).mean()
        print(f"Plan accuracy {acc}")
        print(f"Loss: {loss}")

        loss.backward()
        optimizer.step()
        optimizer.zero_grad()

