"""
Extra progress function for ALFWorld.
Task type: pick_heat_then_place
"""

import re

from agentquest.benchmarks.alfworld import AlfWorldMetrics


class PickHeatThenPlaceFSM:
    """
    State 0, initial: Object not picked up and not heated. (Start)
    State 1, object picked up: Correct object picked up and not heated
    State 2, object heated and picked up: Correct object heated and in hand
    State 3, object heated and not picked up: Correct object heated and not in hand
    State 4, object placed correctly: Hot object placed in correct position. (End)

    Allowed actions: [take, put, heat, cool, clean]
    """

    states = [
        "initial",
        "object picked up",
        "object heated and not picked up",
        "object heated and picked up",
        "object placed correctly",
    ]

    def __init__(self, correct_obj: str, final_pos: str):
        self.correct_obj = correct_obj
        self.final_pos = final_pos
        self.state = 0

    def next(self, action: str, pos: str = ""):
        if self.state == 0:  # initial
            if action == "take":
                self.state = 1

        if self.state == 1:  # object picked up
            if action == "put":
                self.state = 0

            elif action == "heat":
                self.state = 3

        if self.state == 3:  # object heated and picked up
            if action == "put" and pos == self.final_pos:
                self.state = 4  # final
            if action == "put" and pos != self.final_pos:
                self.state = 2
            elif action == "cool":
                self.state = 1

        if self.state == 2:  # object heated and not picked up
            if action == "take":
                self.state = 3


def extract_obj_pos_from_problem(problem: str):
    """problem= /home/bgautam/.cache/alfworld/json_2.1.1/valid_seen/pick_heat_then_place_in_recep-Tomato-None-Fridge-23/trial_T20190909_082320_103350"""
    text = next(x for x in problem.split("/") if "pick_heat_then_place" in x)
    correct_obj = text.split("-")[1]
    final_pos = text.split("-")[3]
    return correct_obj.lower(), final_pos.lower()


def get_recep_from_put_observation(output: str):
    """
    Expected observation output in format: You put the {obj id} on the {recep id}.
    The string may contain other text before or after this pattern.
    Returns the recep id.
    """
    try:
        match = re.search(r"you put the .*? the (.+?)\.", output.lower())
        if match:
            return match.group(1).strip()  # Return the extracted recep id
        else:
            raise ValueError("Output format does not match the expected pattern.")
    except Exception as e:
        print(f"Error parsing observation: {e}")
        return ""


def get_progress_pick_heat_then_place(metrics: AlfWorldMetrics):
    correct_obj, final_pos = extract_obj_pos_from_problem(metrics.problem)

    fsm = PickHeatThenPlaceFSM(correct_obj, final_pos)
    fsm_states = []

    for action, _, observation in metrics.interactions:
        if (
            "nothing happens" in observation.output.lower()
            and correct_obj not in action.value.lower()
        ):
            fsm_states.append(fsm.state)
            continue

        elif (
            "take" in action.value.lower()
            and "you pick up" in observation.output.lower()
        ):
            fsm.next(action="take")

        elif (
            "heat" in action.value.lower() and "you heat" in observation.output.lower()
        ):
            fsm.next(action="heat")

        elif (
            "cool" in action.value.lower() and "you cool" in observation.output.lower()
        ):
            fsm.next(action="cool")

        elif (
            "put" in action.value.lower()
            and "you put" in observation.output.lower()
            and final_pos in get_recep_from_put_observation(observation.output.lower())
        ):
            fsm.next(action="put", pos=final_pos)

        elif (
            "put" in action.value.lower()
            and "you put" in observation.output.lower()
            and final_pos
            not in get_recep_from_put_observation(observation.output.lower())
        ):
            fsm.next(action="put")

        fsm_states.append(fsm.state)

    qualitative = [PickHeatThenPlaceFSM.states[s] for s in fsm_states]
    quantitative = [s * 0.25 for s in fsm_states]
    return qualitative, quantitative
