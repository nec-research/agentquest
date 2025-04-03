import importlib.resources
import json
import re
from collections import Counter
from collections.abc import Callable

from Levenshtein import ratio as lr
from pydantic import ValidationError

from agentquest.lib import Action, Driver, Metrics, Observation, State
from agentquest.lib.utils import log_message


class MasterMindObservation(Observation):
    """Placeholder Observation class for Mastermind, inherited from base class `Observation`.
    Attributes:
        output (str):
        success (bool):
        can_proceed (bool):
    """

    pass


class MasterMindAction(Action):
    """Placeholder Action class for Mastermind, inherited from base class `Action`.
    Attributes:
        value (str):
    """

    pass


class MasterMindState(State):
    """Placeholder State class for Mastermind, inherited from base class `State`.
    Attributes:
        value (str):
    """

    pass


class MasterMindUtils:
    def get_initial_instructions() -> str:
        message = (
            "You are tasked to play the Mastermind game.\n"
            "The host chooses a number and gives you the amount of digits. You have to guess the correct number as fast as you can.\n"
            "The number can contain repetitions and any possible digit between: 0, 1, 2, 3, 4, 5, 6, 7, 8, 9.\n"
            "At each round, you provide a number as a guess. At each step, the host provides you this information:\n"
            "1. The number of correct digits in the wrong position.\n"
            "2. The number of correct digits in the correct position.\n"
            "The game ends when the host outputs 'You Won!'\n"
            "Carefully choose your strategy. Avoid brute force.\n"
            "The guess must be in the following format:\n"
            "Guess: <number>\n"
        )
        return message

    @staticmethod
    def get_correct_positions(str1: str, str2: str) -> int:
        """Get the number of correct digits in the correct position"""
        number_and_position = 0
        for i, j in zip(str1, str2):
            if i == j:
                number_and_position += 1
        return number_and_position

    @staticmethod
    def count_common_elements(str1: str, str2: str) -> int:
        """Get the number correct digits independent from their position"""
        common_elements = Counter(str1) & Counter(str2)
        count = sum(common_elements.values())
        return count

    @staticmethod
    def plural(x, y) -> str:
        return f"{x}" if y < 2 else f"{x}s"

    @staticmethod
    def load_data(
        data_path: str = "__default__", category: str = "4 digits"
    ) -> list[str]:
        """
        Loads the data from a JSON file and returns the list of numbers corresponding to a specified category.
        Args:
            data_path (str, optional): The file path to the JSON data file. If __default__, it defaults to 'agentquest/benchmarks/hangman/data.json'.
            category (str, optional): The category of numbers to load. Possible categories "4 digits", "5 digits", "6 digits", "7 digits", "8 digits".
        Returns:
            list[str]: A list of numbers corresponding to the specified category.
        Raises:
            AssertionError: If the provided category is invalid or not found in the available categories.
        """
        categories = ["4 digits", "5 digits", "6 digits", "7 digits", "8 digits"]
        assert (
            category in categories
        ), f'Invalid category: {category}. Category can be one of the following: {", ".join(categories)}'
        if data_path == "__default__":
            with importlib.resources.open_text(
                "agentquest.benchmarks.mastermind", "data.json"
            ) as fp:
                data = json.loads(fp.read())
        else:
            with open(data_path, "r") as fp:
                data = json.load(fp)
        return data[category]

    @staticmethod
    def parse_agent_output(raw_text: str) -> dict:
        """
        Parses the agent's output to extract the guessed number in the expected format.
        Args:
            raw_text (str): The raw output text from the agent, which should contain a guess in the format "Guess: <number>".
        Returns:
            dict: A dictionary containing the parsed guess, e.g., {"value": "1234"}.
        Raises:
            ValueError: If the raw text is not in the expected format.
        """
        pattern = r"guess:\s*(\d+)"
        match = re.search(pattern, raw_text.lower())
        if match:
            return {"value": str(int(match.group(1)))}
        else:
            raise ValueError(
                "Could not parse agent output. Make sure it is in the format: Guess: <number>"
            )


class MasterMindDriver(Driver):
    """
    Inherits from the Driver class and provides specific implementation for the MasterMind game logic.

    Attributes:
        goal (str): The goal number for the game.
        num_digits (int): The number of digits of the goal number.
        current_state (MasterMindState): Current state of the game, i.e. last valid guess.
        metrics (MasterMindMetrics): Metrics object to keep record of the progress of the game.
    """

    def __init__(self, goal: str):
        super().__init__(goal=goal, metrics_class=MasterMindMetrics)
        self.num_digits = len(self.goal)

    def reset(self) -> MasterMindObservation:
        """
        Resets the game state and providing initial instructions.
        Returns:
            MasterMindObservation: An observation containing the initial instructions and the start message.
        """
        super().reset()
        obs = MasterMindObservation(
            output=MasterMindUtils.get_initial_instructions()
            + f"Start guessing the {self.num_digits} digits number.",
            success=False,
            can_proceed=True,
        )
        self.current_state = State(value="0" * self.num_digits)
        return obs

    def step(self, action: MasterMindAction) -> MasterMindObservation:
        """
        Takes an action object (a guess) and evaluates it against the goal, providing feedback in the form of
        a MasterMindObservation.
        Args:
            action (MasterMindAction): Contains the guess number in it's value attribute.
        Returns:
            MasterMindObservation: An observation object containing feedback on the guess.
        """
        super().step(action=action)
        guess_value = action.value[: self.num_digits]
        self.current_state = State(value=guess_value)

        if guess_value == self.goal:
            self.metrics.set_success(True)
            obs = MasterMindObservation(
                output="You Won!", success=True, can_proceed=False
            )
            return obs

        number_and_position = MasterMindUtils.get_correct_positions(
            self.goal, guess_value
        )
        number_only = MasterMindUtils.count_common_elements(self.goal, guess_value)
        number_only -= number_and_position

        # Instantiate the current observation
        obs = MasterMindObservation(
            output=(
                f"Wrong! Your guess has {number_and_position} correct "
                f'{MasterMindUtils.plural("digit", number_and_position)} in the correct '
                f'{MasterMindUtils.plural("position", number_and_position)} and '
                f'{number_only} correct {MasterMindUtils.plural("digit", number_only)} '
                f'in the wrong {MasterMindUtils.plural("position", number_only)}. Keep guessing.'
            ),
            success=False,
            can_proceed=True,
        )
        return obs

    def step_raw(
        self, raw_text: str, custom_parser: Callable | None = None
    ) -> MasterMindObservation:
        """
        Args
            raw_text (str): The raw output from the agent, expected to contain a guess in the format `Guess: <number>`
            custom_parser (Callable, optional): A custom parser function to process the raw text. If None, the default parser is used.
        Returns
            MasterMindObservation: An observation object returned by step function.
        """
        try:
            if custom_parser:
                parsed_data = custom_parser(raw_text)
                return self.step(MasterMindAction(**parsed_data))
            else:
                parsed_data = MasterMindUtils.parse_agent_output(raw_text)
                return self.step(MasterMindAction(**parsed_data))
        except (ValueError, ValidationError) as e:
            log_message(
                level="warning",
                message=f"Exception encountered: {str(e)}",
            )
            return MasterMindObservation(output=str(e), success=False, can_proceed=True)


class MasterMindMetrics(Metrics):
    """
    A metrics class for evaluating MasterMind game states and actions.
    Attributes:
        goal (str): Target sequence that represents the winning state.
        success (bool):
        interactions (list[tuple[MasterMindAction, MasterMindState, MasterMindObservation]]):
    """

    def __init__(self, goal: str):
        super().__init__(goal=goal)

    def similarity_function(
        self, action_1: MasterMindAction, action_2: MasterMindAction
    ) -> float:
        """Compute similarity between two MasterMind actions."""
        return lr(action_1.value, action_2.value)

    def progress_function(self, state: State) -> float:
        """Calculate progress towards the goal state."""
        reached_milestones = 0
        for i, j in zip(state.value, self.goal):
            if i == j:
                reached_milestones += 1
        return reached_milestones / (len(self.goal))
