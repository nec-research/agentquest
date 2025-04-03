import importlib.resources
import json
import re
from collections.abc import Callable

from pydantic import ValidationError, field_validator

from agentquest.lib import Action, Driver, Metrics, Observation, State
from agentquest.lib.utils import log_message


class HangmanUtils:
    """Utility class providing Hangman game visuals and parsing functionality."""

    display_states = [
        """
  +---+
  |   |
      |
      |
      |
      |
=========
""",
        """
  +---+
  |   |
  O   |
      |
      |
      |
=========
""",
        """
  +---+
  |   |
  O   |
  |   |
      |
      |
=========
""",
        """
  +---+
  |   |
  O   |
 /|   |
      |
      |
=========
""",
        """
  +---+
  |   |
  O   |
 /|\  |
      |
      |
=========
""",
        """
  +---+
  |   |
  O   |
 /|\  |
 /    |
      |
=========
""",
        """
  +---+
  |   |
  O   |
 /|\  |
 / \  |
      |
=========
""",
    ]

    @staticmethod
    def get_initial_instructions() -> str:
        message = (
            "Let's play Hangman! Your objective is to guess the target word one letter at a time.\n"
            "The question marks represent letters in the word yet to be guessed.\n"
            "As you guess letters correctly, they will be revealed in their correct positions.\n"
            "You start with 6 lives. For each incorrect guess, one life will be deducted.\n"
            "Take a guess by providing a letter. The response must be in the following format:\n"
            "Letter: <letter>\n"
        )

        return message

    @staticmethod
    def parse_agent_output(raw_text: str) -> dict:
        """Parses player input to extract the guessed letter.
        Args:
            raw_text (str): Raw input text containing the letter guess.
        Returns:
            dict: Dictionary with 'value' key containing the parsed letter.
        Raises:
            ValueError: If input doesn't match expected 'Letter: <letter>' format.
        """
        pattern = r"letter:\s*([a-z])"
        match = re.search(pattern, raw_text.lower())
        if match:
            return {"value": str(match.group(1))}
        else:
            raise ValueError(
                "Could not parse agent output. Make sure it is in the format: `Letter: <letter>`"
            )

    @staticmethod
    def load_data(
        data_path: str = "__default__", category: str = "4 letters"
    ) -> list[str]:
        """
        Loads the data from a JSON file and returns the list of numbers corresponding to a specified category.
        Args:
            data_path (str, optional): The file path to the JSON data file. If __default__, it defaults to 'agentquest/benchmarks/hangman/data.json'.
            category (str, optional): The category of problems to load. Possible categories "4 letters", "5 letters", "6 letters".
        Returns:
            list[str]: A list of words corresponding to the specified category.
        Raises:
            AssertionError: If the provided category is invalid or not found in the available categories.
        """
        categories = ["4 letters", "5 letters", "6 letters"]
        assert (
            category in categories
        ), f'Invalid category: {category}. Category can be one of the following: {", ".join(categories)}'
        if data_path == "__default__":
            with importlib.resources.open_text(
                "agentquest.benchmarks.hangman", "data.json"
            ) as fp:
                data = json.loads(fp.read())
        else:
            with open(data_path, "r") as fp:
                data = json.load(fp)
        return data[category]


class HangmanAction(Action):
    """
    Represents a player's guess action in Hangman.
    Attributes:
        value (str): A single lowercase alphabetical character representing the guessed letter.
    Raises:
        ValueError: If input is not alphabetical or not exactly one character.
    """

    @field_validator("value")
    @classmethod
    def check_hangman_input(cls, value: str) -> str:
        if not value.isalpha():
            raise ValueError("Only alphabetical characters allowed.")
        if len(value) != 1:
            raise ValueError("Only one character input is allowed.")
        else:
            return value.lower()


class HangmanObservation(Observation):
    """Placeholder Observation class for Hangman inherited from base Observation class.
    Attributes:
        output (str):
        success (bool):
        can_proceed (bool):
    """

    pass


class HangmanState(State):
    """
    Represents the current state of a Hangman game.
    Attributes:
        value (str): Current word state with unguessed letters masked.
        lives (int): Remaining incorrect guesses allowed, starting at 6.
        letters_guessed (list[str]): All letters that have been guessed so far.
    """

    lives: int
    letters_guessed: list[str]

    def describe_state(self) -> str:
        """Generates a formatted description of the current game state."""
        return (
            f"Game current state.\nWord: {self.value}\nYou have {self.lives} guesses left.\nYou have already guessed following letters: {', '.join(self.letters_guessed)} \n"
            + "-" * 25
            + "\n"
            + HangmanUtils.display_states[6 - self.lives]
            + "\n"
        )


class HangmanMetrics(Metrics):
    """A metrics class for evaluating Hangman game states and actions.
    Attributes:
        goal (str): Target word that represents the winning state.
        success (bool):
        interactions (list[tuple[HangmanAction, HangmanState, HangmanObservation]]):
    """

    def __init__(self, goal: str):
        super().__init__(goal)

    def similarity_function(
        self, action_1: HangmanAction, action_2: HangmanAction
    ) -> float:
        """Compare similarity between two Hangman actions.
        Args:
            action_1 (HangmanAction): First action to compare.
            action_2 (HangmanAction): Second action to compare.
        Returns:
            float: similarity score
        """
        if action_1.value.lower() == action_2.value.lower():
            return 1
        else:
            return 0

    def progress_function(self, state: HangmanState) -> float:
        """Calculate progress towards guessing the target word.
        Args:
            state (HangmanState): Current game state to evaluate.
        Returns:
            float: Ratio of correctly guessed letters to total letters in goal word.
        """
        match_count = 0
        for i, letter in enumerate(self.goal):
            if state.value[i].lower() == letter.lower():
                match_count += 1
        return match_count / len(self.goal)


class HangmanDriver(Driver):
    """Driver class controlling Hangman game logic and state transitions.

    Attributes:
        goal (str): Target word players must guess.
        current_state (HangmanState): Current game state including guessed letters and lives.
        metrics (HangmanMetrics): Metrics object to record the progress of the game.
    """

    def __init__(self, goal: str):
        super().__init__(goal.lower(), metrics_class=HangmanMetrics)

    def reset(self) -> HangmanObservation:
        """Reset game state to initial conditions.
        Returns:
            HangmanObservation: Initial game state with instruction.
        """
        super().reset()
        self.current_state = HangmanState(
            value="?" * len(self.goal), lives=6, letters_guessed=[]
        )
        return HangmanObservation(
            output=HangmanUtils.get_initial_instructions()
            + f"Your target word is {len(self.goal)} characters long.\n"
            + self.current_state.describe_state(),
            success=False,
            can_proceed=True,
        )

    def find_matching_letters(self, guess: str) -> str:
        """Update game state by revealing matching letters in target word."""
        exploded_state_value = list(self.current_state.value)
        for i in range(len(self.goal)):
            if guess.lower() == self.goal[i]:
                exploded_state_value[i] = guess.lower()
        self.current_state.value = "".join(exploded_state_value)

    def step(self, action: HangmanAction) -> HangmanObservation:
        """Process a player's guess and update game state.
        Args:
            action (HangmanAction): Player's letter guess.
        Returns:
            HangmanObservation: Observation object with information about game state.
        """
        super().step(action)
        if action.value in self.current_state.letters_guessed:
            return HangmanObservation(
                output=f"You have already guessed the letter {action.value}.\n"
                + self.current_state.describe_state(),
                success=False,
                can_proceed=True,
            )

        output_string = ""
        if action.value.lower() in self.goal.lower():
            self.find_matching_letters(action.value.lower())
            output_string += f"The guessed letter {action.value} was correct. \n"
        else:
            self.current_state.lives -= 1
            output_string += f"The guessed letter {action.value} was incorrect. \n"

        self.current_state.letters_guessed.append(action.value)
        if self.current_state.lives == 0:
            output_string += (
                f"You have lost. No more lives remaining.\nThe word was {self.goal}. \n"
            )
            return HangmanObservation(
                output=output_string + self.current_state.describe_state(),
                success=False,
                can_proceed=False,
            )

        if "?" not in self.current_state.value:
            self.metrics.set_success(True)
            output_string += "You have won !!! \n"
            return HangmanObservation(
                output=output_string + self.current_state.describe_state(),
                success=True,
                can_proceed=False,
            )

        return HangmanObservation(
            output=output_string + self.current_state.describe_state(),
            success=False,
            can_proceed=True,
        )

    def step_raw(
        self, raw_text: str, custom_parser: Callable | None = None
    ) -> HangmanObservation:
        """Process raw text input into Hangman action and calls the step function.
        Args:
            raw_text (str): Raw input in 'Letter: <letter>' format.
            custom_parser (Callable | None): Optional custom parsing function.
        Returns:
            HangmanObservation: Game state after processing input.
        """
        try:
            if custom_parser:
                parsed_data = custom_parser(raw_text)
                return self.step(HangmanAction(**parsed_data))
            else:
                parsed_data = HangmanUtils.parse_agent_output(raw_text)
                return self.step(HangmanAction(**parsed_data))
        except (ValueError, ValidationError) as e:
            log_message(
                level="warning",
                message=f"Exception encountered: {str(e)}",
            )
            return HangmanObservation(output=str(e), success=False, can_proceed=True)
