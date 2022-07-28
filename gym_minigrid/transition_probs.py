import numpy as np


def create_transition_matrices(objs, num_rooms):
    """
    return dict transitions, where transitions[obj] is the transition matrix for any obj in objs.
    the probability of obj going from room i --> j is: transitions[obj][i, j]
    """
    transitions = {}
    for obj in objs:
        probs = np.random.rand(num_rooms, num_rooms)
        probs /= np.expand_dims(np.sum(probs, axis=1), 1)
        transitions[obj] = probs

    return transitions

