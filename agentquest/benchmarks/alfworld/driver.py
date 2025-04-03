import glob
import json
import os
import random
import re
from collections.abc import Callable
from os.path import join as pjoin

import textworld
import textworld.gym
from Levenshtein import ratio as lr
from pydantic import ValidationError

from agentquest.lib import Action, Driver, Metrics, Observation, State
from agentquest.lib.utils import log_message
from alfworld.agents.environment.alfred_tw_env import (
    AlfredDemangler,
    AlfredExpert,
    AlfredExpertType,
)
from alfworld.agents.utils.misc import add_task_to_grammar
from alfworld.info import ALFWORLD_DATA


class AlfWorldUtils:
    """Utility class for managing AlfWorld environments and data.

    Provides functionality for loading problems, initializing environments,
    and parsing game data.
    """

    @staticmethod
    def load_data(
        data_path: str = ALFWORLD_DATA, category: str = "all", source: str = "train"
    ) -> list[str]:
        """Load AlfWorld problem data based on category and source.
        Args:
            data_path (str): Path to AlfWorld data directory.
            category (str): Problem category ("pick_and_place", "look_at_obj_in_light", "pick_clean_then_place", "pick_heat_then_place", "pick_cool_then_place", "pick_two_obj_and_place", "all").
            source (str): Data source ('train', 'valid_seen', 'valid_unseen', 'all').
        Returns:
            list[str]: Possible Alfworld problem paths.
        Raises:
            ValueError: If problem files cannot be found.
        """
        sources = ["train", "valid_seen", "valid_unseen", "valid_train", "all"]
        categories = [
            "pick_and_place",
            "look_at_obj_in_light",
            "pick_clean_then_place",
            "pick_heat_then_place",
            "pick_cool_then_place",
            "pick_two_obj_and_place",
            "all",
        ]
        assert (
            category in categories
        ), f'Invalid category: {category}. Provide one of the following: {", ".join(categories)}'
        assert (
            source in sources
        ), f'Invalid source: {source}. Source should be one of the following: {", ".join(sources)}'
        # Load problems
        if source != "all":
            problems = glob.glob(
                pjoin(data_path, "json_2.1.1", source, "**", "initial_state.pddl"),
                recursive=True,
            )
        else:
            problems = glob.glob(
                pjoin(data_path, "json_2.1.1", "**", "initial_state.pddl"),
                recursive=True,
            )
            if len(problems) == 0:
                raise ValueError(
                    f"Can't find problem files in {data_path}. Did you run alfworld-download?"
                )

        def filter_conditions(p):
            return (
                "movable_recep" not in p  # According to alfworld example code
                and (category == "all" or category in p)
                and (source == "all" or source in p)
            )

        filtered_problems = [
            os.path.dirname(p) for p in problems if filter_conditions(p)
        ]
        return filtered_problems

    @staticmethod
    def pick_random_problem() -> str:
        """Select a random problem from all available problems."""
        problems = glob.glob(
            pjoin(ALFWORLD_DATA, "**", "initial_state.pddl"), recursive=True
        )
        # Remove problem which contains movable receptacles.
        problems = [p for p in problems if "movable_recep" not in p]
        if len(problems) == 0:
            raise ValueError(
                f"Can't find problem files in {ALFWORLD_DATA}. Did you run alfworld-data?"
            )
        return os.path.dirname(random.choice(problems))

    @staticmethod
    def get_admissible_commands(info: dict) -> str:
        """Return a string of list of admissible commands."""
        admissible_commands = str(info["admissible_commands"])
        return (
            "Admissible commands:\n"
            + admissible_commands
            + "\n"
            + "Your response should be in format: 'Action: <action_command>'"
        )

    @staticmethod
    def initiate_env(
        problem: str,
        domain=pjoin(ALFWORLD_DATA, "logic", "alfred.pddl"),
        grammar=pjoin(ALFWORLD_DATA, "logic", "alfred.twl2"),
    ):
        """Initialize AlfWorld environment with specified problem.
        Args:
            problem (str): Path to problem directory.
            domain (str): Path to PDDL domain file.
            grammar (str): Path to grammar file.
        Returns:
            gym.Env: Initialized game environment.
        """
        log_message(level="Info", message=f"Playing {problem}")
        GAME_LOGIC = {
            "pddl_domain": open(domain).read(),
            "grammar": open(grammar).read(),
        }
        # Load state and trajectory files
        pddl_file = os.path.join(problem, "initial_state.pddl")
        json_file = os.path.join(problem, "traj_data.json")
        with open(json_file, "r") as fp:
            traj_data = json.load(fp)
        GAME_LOGIC["grammar"] = add_task_to_grammar(GAME_LOGIC["grammar"], traj_data)

        # dump game file
        gamedata = dict(**GAME_LOGIC, pddl_problem=open(pddl_file).read())
        gamefile = os.path.join(os.path.dirname(pddl_file), "game.tw-pddl")
        json.dump(gamedata, open(gamefile, "w"))

        # register a new gym environment
        expert = AlfredExpert(expert_type=AlfredExpertType.PLANNER)
        request_infos = textworld.EnvInfos(won=True, admissible_commands=True)
        env_id = textworld.gym.register_game(
            gamefile,
            request_infos,
            max_episode_steps=1000000,
            wrappers=[AlfredDemangler(), expert],
        )
        return textworld.gym.make(env_id)

    @staticmethod
    def extract_goal_of_task(task_obs: str):
        "Extract goal description from game task observation."
        hook_string = "Your task is to: "
        idx_1 = task_obs.find(hook_string)
        idx_2 = task_obs[idx_1:].find(".")
        return task_obs[idx_1 : idx_1 + idx_2][len(hook_string) :]

    @staticmethod
    def parse_agent_output(raw_text: str) -> dict:
        """
        Parse agent's action command from raw text.
        Args:
            raw_text (str): Raw input text containing admissible command. Expected Parsing Format: `Action: <action_command>
        Returns:
            dict: Parsed dictionary for AlfWorldAction creation e.g. {'value':'look'}
        Raises:
            ValueError: If raw text cannot be parsed.
        """
        pattern = r"action:\s*(.+)"
        match = re.search(pattern, raw_text.lower())
        if match:
            return {"value": str(match.group(1))}
        else:
            raise ValueError(
                "Could not parse agent output. Make sure it is in the format: `Action: <action_command>`"
            )


class AlfWorldState(State):
    """
    Placeholder class for AlfWorld State inherited from base class State.
    Attributes:
        value (str):
        policy_commands (list[str]): Oracle solution with best path to success for a problem from current state of the game. Important to calculate progress.
    """

    policy_commands: list[str]


class AlfWorldObservation(Observation):
    """Placeholder class for AlfWorldObservation inherited from base class Observation.
    Attributes:
        output (str):
        success (bool):
        can_proceed (bool):
    """

    pass


class AlfWorldAction(Action):
    """Place holder class for AlfWorld action command, inherited from base class Action.
    Attributes:
        value (str):
    """

    pass


class AlfWorldMetrics(Metrics):
    """Metrics class for evaluating AlfWorld interactions and progress.

    Attributes:
        goal (str): Target goal state description.
        success (bool):
        interactions (list[tuple[AlfWorldAction, AlfWorldState, AlfWorldObservation]]):
        milestones (list[str]): Sequence of required actions in the beginning to complete task.
        problem (str): Current problem identifier/path.
        valid_interaction_history (list[tuple[AlfWorldAction, AlfWorldState, AlfWorldObservation]]): History of valid action-state-observation triplets.
    """

    def __init__(self, goal: str, problem: str, milestones: list[str] = []):
        super().__init__(goal)
        self.milestones = milestones
        self.problem = problem
        self.valid_interaction_history: list[
            tuple[AlfWorldAction, AlfWorldState, AlfWorldObservation]
        ] = []

    def set_milestones(self, milestones: list[list[str]]):
        self.milestones = milestones

    def add_to_valid_interaction(
        self, interaction: tuple[AlfWorldAction, AlfWorldState, AlfWorldObservation]
    ):
        self.valid_interaction_history.append(interaction)

    def export(self, **kwargs) -> dict:
        exported_data = super().export(**kwargs)
        exported_data = {
            **exported_data,
            "milestones": self.milestones,
            "problem": self.problem,
        }
        return exported_data

    def progress_function(self, state: AlfWorldState) -> float:
        """Compare the number of policy commands (remaining shortest path to solution) of a state to the number of original set of milestones."""
        diff = len(self.milestones) - len(state.policy_commands)
        if diff <= 0:
            return 0.0
        else:
            return diff / len(self.milestones)

    def similarity_function(
        self, action_1: AlfWorldAction, action_2: AlfWorldAction
    ) -> float:
        """Compare similarity between two actions using Levenshtein ratio."""
        return lr(action_1.value, action_2.value)


class AlfWorldDriver(Driver):
    """
    Driver class for managing AlfWorld environment interactions.
    Attributes:
        goal (str): Current task goal.
        env: AlfWorld gym environment instance.
        current_state (AlfWorldState): Current game state, last command accepted by the game.
        metrics (AlfWorldMetrics): Metrics object to record the progress of the game.
    Args:
        problem (str): Path to problem directory. Random if not specified.
    """

    def __init__(self, problem: str):
        if not problem:
            problem = AlfWorldUtils.pick_random_problem()
        if "movable_recep" in problem:
            raise ValueError(
                "This problem contains movable receptacles, which is not supported by AlfWorld."
            )
        super().__init__(
            goal="",
            metrics_class=AlfWorldMetrics,
            metrics_args={"problem": problem},
        )
        self.env = AlfWorldUtils.initiate_env(problem)

    def set_goal(self, goal: str):
        self.goal = goal
        self.metrics.goal = goal

    def reset(self) -> AlfWorldObservation:
        """Reset environment and initialize new run.
        Returns:
            AlfWorldObservation: Initial observation with game instructions
                and available commands.
        """
        super().reset()
        obs, info = self.env.reset()
        self.set_goal(AlfWorldUtils.extract_goal_of_task(str(obs)))
        self.current_state = AlfWorldState(
            value="", policy_commands=info["policy_commands"]
        )
        self.metrics.set_milestones(info["policy_commands"])
        admissible_commands = AlfWorldUtils.get_admissible_commands(info)
        obj = f"{obs}\n{admissible_commands}"
        return AlfWorldObservation(output=obj, success=False, can_proceed=True)

    def step(self, action: AlfWorldAction) -> AlfWorldObservation:
        """Execute action in environment.
        Args:
            action (AlfWorldAction): Action object with admissible command.
        Returns:
            AlfWorldObservation: Observation object with information about changes in the environment.
        """
        super().step(action)
        obs, _, done, info = self.env.step(action.value)

        valid_interaction = False
        if "Nothing happens." not in obs:
            self.current_state = AlfWorldState(
                value=action.value, policy_commands=info["policy_commands"]
            )
            valid_interaction = True

        if not done:
            admissible_commands = AlfWorldUtils.get_admissible_commands(info)
            obs = f"{obs}\n{admissible_commands}"
        else:
            obs = f"You Won!!!\n{obs}"
            self.metrics.set_success(True)

        obs = AlfWorldObservation(output=obs, success=done, can_proceed=not done)
        if valid_interaction:
            self.metrics.add_to_valid_interaction(
                interaction=(action, self.current_state, obs)
            )
        return obs

    def step_raw(
        self, raw_text: str, custom_parser: Callable | None = None
    ) -> AlfWorldObservation:
        """Process raw text input to form AlfWorldAction object and calls AlfWorld step.
        Args:
            raw_text (str): Raw input in 'Action: <action_command>' format.
            custom_parser (Callable | None): Optional custom parsing function.
        Returns:
            AlfWorldObservation: Game state after processing input.
        Raises:
            ValueError: For invalid input format and parsing errors.
        """
        try:
            if custom_parser:
                parsed_data = custom_parser(raw_text)
                return self.step(AlfWorldAction(**parsed_data))
            else:
                parsed_data = AlfWorldUtils.parse_agent_output(raw_text)
                return self.step(AlfWorldAction(**parsed_data))
        except (ValueError, ValidationError) as e:
            log_message(
                level="warning",
                message=f"Exception encountered: {str(e)}",
            )
            return AlfWorldObservation(output=str(e), success=False, can_proceed=True)
