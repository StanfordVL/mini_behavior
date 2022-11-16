from cmd import PROMPT
import openai
import numpy as np
from transformers import AutoModelForCausalLM, AutoTokenizer
import torch

openai.api_key = "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"

# SAYCAN_PROMPT = """Robot: Hi there, I'm a robot operating in an office kitchen.
# You can ask me to do various tasks and I'll tell you the sequence of actions I would do to accomplish your task.
# Human: hold the snickers
# Robot:
# 1. pick up the snickers[success: no][scene: snickers]
# 2. pick up the snickers
# 3. done.
# Human: put the trailmix here
# Robot:
# 1. put down the trailmix
# 2. done.
# Human: put a water bottle and an oatmeal next to the microwave
# Robot:
# 1. find a water
# 2. pick up the water[success: no]
# 3. pick up the water[success: no]
# 4. pick up the water
# 5. go to microwave
# 6. put down the water[scene: water, microwave]
# 7. find an oatmeal
# 8. pick up the oatmeal[scene: oatmeal]
# 9. go to the microwave
# 10. put down the oatmeal[scene: microwave, oatmeal, water]
# 11. done.
# Human: put a grapefruit from the table into the bowl
# Robot:
# 1. find a grapefruit
# 2. pick up the grapefruit
# 3. go to the bowl
# 4. put down the grapefruit
# 5. done.
# Human: get a sponge from the counter and put it in the sink
# Robot:
# 1. find a sponge
# 2. pick up the sponge[success: no][scene: sponge]
# 3. pick up the sponge[success: no]
# 4. pick up the sponge[scene: sponge]
# 5. go to the sink
# 6. put down the sponge
# 7. done.
# Human: move a drink from the table to the counter
# Robot:
# 1. find a water
# 2. pick up the water[scene: tea, grapefruit soda, kettle chips]
# 3. pick up the grapefruit soda
# 4. go to the counter
# 5. put down the grapefruit soda[success: no]
# 6. put down the grapefruit soda
# 7. done.
# Human: bring me some snacks
# Robot:
# 1. find a twix
# 2. pick up the twix[scene: pretzel]
# 3. find a pretzel
# 4. pick up the pretzel
# 5. bring it to you
# 6. put down the pretzel[scene: pretzel, dried fruit]
# 7. find an dried fruit
# 8. pick up the dried fruit
# 9. bring it to you
# 10. put down the dried fruit[scene: ]
# 11. done.
# Human: bring me a fruit
# Robot:
# 1. find an orange
# 2. pick up the orange[scene: apple, redbull]
# 3. pick up the apple[success: no]
# 5. pick up the apple
# 6. bring it to you
# 7. put down the apple
# 8. done.
# Human: deliver a can of coke to me
# Robot:
# 1. find a coke
# 2. pick up the coke
# 3. bring it to you
# 4. put down the coke
# 5. done.
# Human: I finished my drink, can you throw it away and bring me a mountain dew
# Robot:
# 1. find a sprite
# 2. pick up the sprite[scene: coke]
# 3. pick up the coke[success: no][scene: coke]
# 4. pick up the coke[scene: coke]
# 5. go to the trash
# 6. put down the coke
# 7. find a mountain dew
# 8. pick up the mountain dew
# 9. bring it to you
# 10. put down the mountain dew
# 11. done.
# Human: let go of the banana
# Robot:
# 1. put down the banana
# 2. done.
# Human: pick up the peanuts
# Robot:
# 1. pick up the peanuts
# 2. done.
# Human: bring me some snack
# Robot:
# 1. pick up the peanuts[success: no]
# 2. pick up the peanuts
# 3. pick up the blue chip bag
# 4. bring it to you
# 5. put down the blue chip bag
# 5. done.
# Human: throw away a coffee cup
# Robot:
# 1. find a coffee cup
# 2. pick up the coffee cup[success: no]
# 3. pick up the coffee cup
# 4. go to the trash
# 5. put down the coffee cup
# 6. done.
# Human: place a knife and a banana to the table
# Robot:
# 1. find a knife
# 2. pick up the knife[success: no]
# 3. pick up the knife
# 4. go to the table
# 5. put down the knife
# 6. find a banana
# 7. pick up the banana
# 8. go to the table
# 9. put down the banana[scene: banana, knife]
# 10. done.
# Human: {}
# Robot:"""
# SAYCAN_PROMPT = """Robot: Hi there, I'm a robot operating in an office kitchen.
# You can ask me to do various tasks and I'll tell you the sequence of actions I would do to accomplish your task.
# Human: hold the snickers
# Robot:
# 1. pick up the snickers
# 2. done.
# Human: put the trailmix here
# Robot:
# 1. put down the trailmix
# 2. done.
# Human: put a water bottle and an oatmeal next to the microwave
# Robot:
# 1. find a water
# 2. pick up the water
# 3. go to microwave
# 4. put down the water[scene: water, microwave]
# 5. find an oatmeal
# 6. pick up the oatmeal
# 7. go to the microwave
# 8. put down the oatmeal
# 9. done.
# Human: put a grapefruit from the table into the bowl
# Robot:
# 1. pick up the grapefruit
# 2. go to the bowl
# 3. put down the grapefruit
# 4. done.
# Human: get a sponge from the counter and put it in the sink
# Robot:
# 1. go to the counter
# 2. pick up the sponge
# 3. go to the sink
# 4. put down the sponge
# 5. done.
# Human: move a drink from the table to the counter
# Robot:
# 1. go to the table
# 2. pick up the water
# 3. go to the counter
# 4. put down the grapefruit soda
# 5. done.
# Human: bring me a fruit
# Robot:
# 1. go to the cabinet
# 2. open the cabinet
# 3. pick up the apple
# 4. bring it to you
# 5. put down the apple
# 6. done.
# Human: deliver a can of coke to me
# Robot:
# 1. go to the refrigerator
# 2. open the refrigerator
# 3. pick up the coke
# 4. bring it to you
# 5. put down the coke
# 6. done.
# Human: {}
# Robot:"""
SAYCAN_PROMPT = """You are a robotic task planner.
Task: {}
Plan:"""

class SayCan:
    def __init__(self, task):
        self.task = task
        self.action_history = []
        print("SayCan initialized with task:", task)

    def get_action(self, affordances, affordance_labels):
        affordance_likelihoods = {}
        max_likelihood = -np.inf
        best_affordance = None
        best_label_str = None
        for affordance, label in zip(affordances, affordance_labels):
            label_obj = ' '.join(label[1].split("_")[:-1])
            label_action = label[0].replace('goto', 'go to').replace('pickup', 'pick up').replace('putdown', 'put down').replace('drop_in', 'drop in')
            label_str = ' '.join([label_action, 'the', label_obj])
            prompt = self.get_prompt_from_history() + label_str
            print(prompt)
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
        response = openai.Completion.create(
            model="text-davinci-002",
            prompt=prompt,
            temperature=0,
            max_tokens=1,
            top_p=1,
            frequency_penalty=0,
            presence_penalty=0,
            logprobs=0,
            stop=["\n"],
            echo=True,
        )
        return sum(response["choices"][0]["logprobs"]["token_logprobs"][1:])

class SayCanOPT:
    def __init__(self, task):
        self.task = task
        self.action_history = []
        self.model = AutoModelForCausalLM.from_pretrained("facebook/opt-6.7b", torch_dtype=torch.float16).cuda()
        self.tokenizer = AutoTokenizer.from_pretrained("facebook/opt-6.7b", use_fast=False)
        # self.model = AutoModelForCausalLM.from_pretrained("facebook/opt-350m", torch_dtype=torch.float16).cuda()
        # self.tokenizer = AutoTokenizer.from_pretrained("facebook/opt-350m", use_fast=False)
        print("SayCan initialized with task:", task)

    def get_action(self, affordances, affordance_labels):
        affordance_likelihoods = {}
        max_likelihood = -np.inf
        best_affordance = None
        best_label_str = None
        for affordance, label in zip(affordances, affordance_labels):
            label_obj = ' '.join(label[1].split("_")[:-1])
            label_action = label[0].replace('goto', 'go to').replace('pickup', 'pick up').replace('putdown', 'put down').replace('drop_in', 'drop in')
            label_str = ' '.join([label_action, 'the', label_obj])
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
        input_ids = self.tokenizer(prompt, return_tensors="pt").input_ids.cuda()
        outputs = self.model(input_ids, labels=input_ids)
        sentence_prob = outputs['logits'].max(dim=2).values.sum()

        # print(sum_logits)
        # response = openai.Completion.create(
        #     model="text-davinci-002",
        #     prompt=prompt,
        #     temperature=0,
        #     max_tokens=1,
        #     top_p=1,
        #     frequency_penalty=0,
        #     presence_penalty=0,
        #     logprobs=0,
        #     stop=["\n"],
        #     echo=True,
        # )
        # sentence_prob_2 =  sum(response["choices"][0]["logprobs"]["token_logprobs"][1:])
        #should be around -91
        # breakpoint()
        return sentence_prob
