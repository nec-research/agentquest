from Levenshtein import ratio as g
import numpy as np


def get_repetitions(actions, THETA_A):
    unique_act = set()  # Initialise unique actions
    for i, a in enumerate(actions):
        # Check for repetitions
        if all([g(a, actions[x]) < THETA_A for x in range(i)]):
            unique_act.add(a)
    return len(actions)-len(unique_act)


def get_mastermind_repetitions(actions):
    return get_repetitions(actions, 1.0)


def get_autopenbench_repetitions(actions, THETA_A):
    formatted_actions = []
    for action in actions:
        tool = action.__class__.__name__
        str_action = f'{tool}({action})'
        formatted_actions.append(str_action)

    return get_repetitions(formatted_actions, THETA_A)


def get_alfworld_progress(state, milestones):
    actions = [x[0] for x in state]
    observations = [x[1] for x in state]
    obj_pickeds = [x[2] for x in state]
    gt_idx = np.argmax([len(set(actions).intersection(set(x)))
                       for x in milestones])
    game_gt = milestones[gt_idx]
    gt_step = 0
    for i in range(len(state)):
        action = actions[i]
        observation = observations[i]
        if action == game_gt[gt_step] and gt_step < len(game_gt):
            gt_step += 1
        else:
            if i > 0 and obj_pickeds[i-1] and 'put' in action and not obj_pickeds[i]:
                gt_step -= 1
    return gt_step


def get_mastermind_progress(state, milestones):
    reached_milestones = 0
    # Get the digits in correct position
    for i, j in zip(state, milestones):
        if i == j:
            reached_milestones += 1
    return reached_milestones


def get_autopenbench_progress(evaluator, state, milestones=None):
    """Wrapper for the AutoPenBench evaluator

    Args:
        evaluator (autopenbench.evaluation.Evaluator): AutoPenBench evaluator
        state (str): current execution step (at least Action + Observation)
        milestones (None, optional): Not used.

    Returns:
        int: number of reached command milestones
    """
    evaluator.evaluate_step(state)
    return evaluator.reached_milestones
