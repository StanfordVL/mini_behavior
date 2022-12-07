import numpy as np
from transformers import AutoModelForCausalLM, AutoTokenizer
import torch
import math
import json

from lm import SoftEmbedding
import torch
from tensorboardX import SummaryWriter

DEVICE = "cuda" if torch.cuda.is_available() else "cpu"

class SayCanOPT:
    def __init__(self, model_name, use_soft_prompt=True):
        self.action_history = []
        self.model = AutoModelForCausalLM.from_pretrained(
            model_name
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

    def get_action(self, context, affordance_labels):
        affordance_likelihoods = []
        for label in affordance_labels:
            prompt = context + label
            affordance_likelihoods.append(self.get_text_likelihood(prompt))
        return max(range(len(affordance_likelihoods)), key=lambda i: affordance_likelihoods[i])

    def get_text_likelihood(self, prompt):
        # print(prompt)
        input_ids = self.tokenizer(prompt, return_tensors="pt").input_ids.to(DEVICE)

        if self.use_soft_prompt:
            input_ids = torch.cat(
                [torch.full((1, self.n_tokens), 50256).to(DEVICE), input_ids], 1
            )

        outputs = self.model(input_ids, labels=input_ids)
        # sentence_prob = outputs['logits'].max(dim=2).values.sum()

        return -math.exp(outputs["loss"].item())

    def train_step(self, context, affordance_labels, num_possible_affordances):
        logits = torch.zeros(num_possible_affordances)
        labels = []
        for idx, label in enumerate(affordance_labels):
            prompt = context + label
            labels.append(label)

            input_ids = self.tokenizer(prompt, return_tensors="pt").input_ids.to(DEVICE)

            if self.use_soft_prompt:
                input_ids = torch.cat(
                    [torch.full((1, self.n_tokens), 50256).to(DEVICE), input_ids], 1
                )

            outputs = self.model(input_ids, labels=input_ids)
            # sentence_prob = outputs['logits'].max(dim=2).values.sum()

            logits[idx] = -torch.exp(outputs["loss"])
        logits[idx+1:] = -math.inf

        # idx = torch.argmax(logits)
        # self.action_history.append(labels[idx])
        return logits

def train_step(optimizer, model, plan_length, contexts, affordance_labels, num_possible_affordances, test=False):
    logits = torch.zeros(plan_length, num_possible_affordances)
    for idx in range(plan_length):
        breakpoint()
        step_logits = model.train_step(contexts[idx], affordance_labels[idx], num_possible_affordances)
        logits[idx] = step_logits
    loss = torch.nn.functional.cross_entropy(logits, true_logits)

    if not test:
        loss.backward()
        optimizer.step()
        optimizer.zero_grad()
    # model.action_history = []
    return loss, logits

if __name__ == "__main__":
    dataset = json.loads(open("behavior_cloning_dataset.json").read())

    lm = SayCanOPT(model_name="facebook/opt-350m", use_soft_prompt=True)

    parameters = lm.model.get_input_embeddings().parameters()
    optimizer = torch.optim.Adam(parameters, lr=1e-4)
    optimizer.zero_grad()

    writer = SummaryWriter()

    # breakpoint()

    dataset_train = dict(list(dataset.items())[len(dataset)//2:])
    dataset_test = dict(list(dataset.items())[:len(dataset)//2])
    # breakpoint()

    num_possible_affordances = max([max([len(plan_step["negative_labels"]) for plan_step in dataset[task]]) for task in list(dataset.keys())]) + 1

    for i in range(1000):

        task = np.random.choice(list(dataset_train.keys()))
        possible_affordances_by_step = [[plan_step["positive_label"]] + plan_step["negative_labels"] for plan_step in dataset[task]]
        contexts = [plan_step["context"] for plan_step in dataset[task]]

        plan_length = len(dataset[task])
        true_plan = torch.zeros(len(possible_affordances_by_step), dtype=torch.int64)
        true_logits = torch.nn.functional.one_hot(true_plan, num_possible_affordances).float()
        # mask the entries (i,j) in true_logits where j > len(possible_affordances_by_step[i])
        for idx, step in enumerate(possible_affordances_by_step):
            true_logits[idx, len(step):] = -math.inf
        # breakpoint()

        loss, logits = train_step(optimizer, lm, plan_length, contexts, possible_affordances_by_step, num_possible_affordances)
        predicted_plan = torch.argmax(logits, dim=1)
        acc = (predicted_plan == torch.tensor(true_plan)).float().mean()
        print(f"Plan accuracy {acc}")
        writer.add_scalar('plan-accuracy/train', acc, i)
        print(f"Loss: {loss}")
        writer.add_scalar('loss/train', loss, i)
        print(f"Predicted plan: {predicted_plan}")

        if i % 10 == 0:
            test_task = list(dataset_test.keys())[0]
            test_possible_affordances_by_step = [[plan_step["positive_label"]] + plan_step["negative_labels"] for plan_step in dataset[task]]
            test_contexts = [plan_step["context"] for plan_step in dataset[task]]
            test_plan_length = len(dataset[task])
            test_true_plan = torch.zeros(len(test_possible_affordances_by_step), dtype=torch.int64)
            test_true_logits = torch.nn.functional.one_hot(test_true_plan, num_possible_affordances).float()
            # mask the entries (i,j) in true_logits where j > len(possible_affordances_by_step[i])
            for idx, step in enumerate(possible_affordances_by_step):
                true_logits[idx, len(step):] = -math.inf
            loss, logits = train_step(optimizer, lm, test_plan_length, test_contexts, test_possible_affordances_by_step, num_possible_affordances, test=True)
            predicted_plan = torch.argmax(logits, dim=1)
            acc = (predicted_plan == torch.tensor(test_true_plan)).float().mean()
            print(f"Test plan accuracy {acc}")
            writer.add_scalar('plan-accuracy/test', acc, i)
            print(f"Loss: {loss}")
            writer.add_scalar('loss/test', loss, i)
