import json
import re
from collections.abc import Callable

import requests
from Levenshtein import ratio as lr
from pydantic import ValidationError

from agentquest.lib import Action, Driver, Metrics, Observation, State
from agentquest.lib.utils import log_message


class WebshopUtils:
    """Utility class for managing Webshop environments and data.

    Provides functionality for loading problems, initializing environments,
    and parsing game data.
    """

    BASE_INTERFACE_URL = "http://localhost:5555"

    @staticmethod
    def test_interface_api(base_url: str = BASE_INTERFACE_URL):
        print(base_url)
        response = requests.get(base_url)
        if response.status_code == 200:
            log_message("info", "Connection test to interface successful.")
            print(response.text)
        else:
            log_message("warning", "Connection test to interface failed.")
            print(response.text)

    @staticmethod
    def parse_agent_output(raw_text: str) -> dict:
        """
        Parse agent's action command from raw text.
        Args:
            raw_text (str): Raw input text containing admissible command. Expected Parsing Format: `Action: <action_command>
        Returns:
            dict: Parsed dictionary for WebshopAction creation e.g. {'value':'look'}
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

    @staticmethod
    def get_initial_instructions():
        return (
            "Welcome to WebShop, a simulated e-commerce website environment. "
            "Your goal is to find and buy the best product matching the instruction provided.\n"
            "There are two possible actions `search[<query>]` and `click[<clickable>]`. These actions will help you navigate through the WebShop environment. The list of possible actions and clickables are provided in the observation output after every action.\n"
            "Your output should in the following format:\nAction: <action>\n"
        )


class WebshopState(State):
    """
    Placeholder class for Webshop State inherited from base class State.
    Attributes:
        value (dict): response json as returned by the interface
    """

    value: dict


class WebshopObservation(Observation):
    """Placeholder class for WebshopObservation inherited from base class Observation.
    Attributes:
        output (str):
        success (bool):
        can_proceed (bool):
    """

    pass


class WebshopAction(Action):
    """Place holder class for Webshop action command, inherited from base class Action.
    Attributes:
        value (str):
    """

    pass


class WebshopMetrics(Metrics):
    """Metrics class for evaluating Webshop interactions and progress.

    Attributes:
        goal (str): Target goal state description.
        success (bool):
        interactions (list[tuple[WebshopAction, WebshopState, WebshopObservation]]):
    """

    def __init__(self, goal: str):
        super().__init__(goal)

    def get_progresses(self) -> list[float]:
        """Taking in the reward obtained from WebShop directly."""
        rewards = [state.value.get("reward", 0.0) for _, state, _ in self.interactions]
        return rewards

    def similarity_function(
        self, action_1: WebshopAction, action_2: WebshopAction
    ) -> float:
        """Compare similarity between two actions using Levenshtein ratio."""
        return lr(action_1.value, action_2.value)


class WebshopDriver(Driver):
    """
    Driver class for managing Webshop environment interactions.
    Attributes:
        goal (str): Current task goal.
        current_state (WebshopState): Current game state, last command accepted by the game.
        metrics (WebshopMetrics): Metrics object to record the progress of the game.
    Args:
        problem (str): Path to problem directory. Random if not specified.
    """

    def __init__(self, base_url: str = WebshopUtils.BASE_INTERFACE_URL):
        super().__init__(
            goal="",
            metrics_class=WebshopMetrics,
            metrics_args={},
        )
        self.base_url = base_url

    def set_goal(self, goal: str):
        self.goal = goal
        self.metrics.goal = goal

    def reset(self) -> WebshopObservation:
        """Reset environment and initialize new run.
        Returns:
            WebshopObservation: Initial observation with game instructions
                and available commands.
        """
        super().reset()
        response = requests.post(self.base_url + "/reset").json()
        self.current_state = WebshopState(value=response)
        self.set_goal(response.get("obs", ""))

        return WebshopObservation(
            output=WebshopUtils.get_initial_instructions()
            + response.get("obs", "")
            + f"\nAvailable actions in json:\n{json.dumps(response.get('available_actions', {}))}",
            success=response.get("done", False),
            can_proceed=not response.get("done", False),
        )

    def step(self, action: WebshopAction) -> WebshopObservation:
        """Execute action in environment.
        Args:
            action (WebshopAction): Action object with admissible command.
        Returns:
            WebshopObservation: Observation object with information about changes in the environment.
        """
        super().step(action)
        response = requests.post(
            self.base_url + "/step",
            data=json.dumps({"action": action.value}),
            headers={"Content-type": "application/json"},
        ).json()
        self.current_state = WebshopState(value=response)
        return WebshopObservation(
            output=response.get("obs", "")
            + f"\nAvailable actions in json\n{json.dumps(response.get('available_actions', {}))}",
            success=response.get("done", False),
            can_proceed=not response.get("done", False),
        )

    def step_raw(
        self, raw_text: str, custom_parser: Callable | None = None
    ) -> WebshopObservation:
        """Process raw text input to form WebshopAction object and calls Webshop step.
        Args:
            raw_text (str): Raw input in 'Action: <action_command>' format.
            custom_parser (Callable | None): Optional custom parsing function.
        Returns:
            WebshopObservation: Game state after processing input.
        Raises:
            ValueError: For invalid input format and parsing errors.
        """
        try:
            if custom_parser:
                parsed_data = custom_parser(raw_text)
                return self.step(WebshopAction(**parsed_data))
            else:
                parsed_data = WebshopUtils.parse_agent_output(raw_text)
                return self.step(WebshopAction(**parsed_data))
        except (ValueError, ValidationError) as e:
            log_message(
                level="warning",
                message=f"Exception encountered: {str(e)}",
            )
            return WebshopObservation(output=str(e), success=False, can_proceed=True)
