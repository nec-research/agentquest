import importlib.resources
import json
import re
from collections.abc import Callable

import enchant
from Levenshtein import ratio as lr
from pydantic import ValidationError, field_validator

from agentquest.lib import Action, Driver, Metrics, Observation, State
from agentquest.lib.utils import log_message


class WordleAction(Action):
    """
    Represents a player's guess action in Wordle.
    Attributes:
        value (str): A five letter word.
    Raises:
        ValueError: If input is not alphabetical or not exactly five letter word.
    """

    @field_validator("value")
    @classmethod
    def check_wordle_input(cls, value: str) -> str:
        if not value.isalpha():
            raise ValueError("Only alphabetical characters allowed.")
        if len(value) != 5:
            raise ValueError("Only five letter word input is allowed.")
        else:
            return value.lower()


class WordleState(State):
    """Represents the current state of a Wordle game.
    Attributes:
        value (str): Last guessed word.
        lives (int): Remaining number of guesses, starting at 6
        words_guessed (list[str]): Words guessed so far.
    """

    lives: int = 6
    words_guessed: list[str] = []

    def set_value(self, new_value: str):
        self.value = new_value.lower()

    def add_to_guessed_list(self, new_value: str):
        self.words_guessed.append(new_value.lower())

    def decrease_lives_by_one(self):
        self.lives -= 1


class WordleObservation(Observation):
    """Represents the output from the Wordle game after every action.
    Attributes:
        output (str):
        success (bool):
        can_proceed (bool):
    """

    pass


class WordleUtils:
    @staticmethod
    def get_initial_instructions() -> str:
        message = (
            "Welcome to Wordle. Your goal is to guess a 5 letter word only containing letters in the English alphabet.\n"
            "Letters correctly guessed in the correct position will be shown with a '\u2713' in place.\n"
            "Letters correctly guessed but in the wrong position will be shown with a '\u26a0' in place.\n"
            "Letters incorrectly guessed will be shown with a '\u2718' in place."
            "You have six lives.\n"
            "Take a guess by providing a 5 letter word. The response must be in the following format.\n"
            "Word: <word>"
        )
        return message

    @staticmethod
    def load_game(data_path: str = "__default__"):
        """
        Loads the data from a JSON file and returns the list of numbers corresponding to a specified category.
        Args:
            data_path (str, optional): The file path to the JSON data file. If __default__, defaults to './data.json'.
            category (str, optional): The category of problems to load. Possible categories "5 letters".
        Returns:
            list[str]: A list of words corresponding to the specified category.
        Raises:
            AssertionError: If the provided category is invalid or not found in the available categories.
        """
        category = "5 letters"  # To support other categories as argument in future.
        categories = ["5 letters"]
        assert (
            category in categories
        ), f'Invalid category: {category}. Category can be one of the following: {", ".join(categories)}'
        if data_path == "__default__":
            with importlib.resources.open_text(
                "agentquest.benchmarks.wordle", "data.json"
            ) as fp:
                data = json.loads(fp.read())
        else:
            with open(data_path, "r") as fp:
                data = json.load(fp)
        return data[category]

    @staticmethod
    def print_wordle_word(word: str):
        """Prints one word in nice wordle like boxes."""
        boxes = []
        for char in word:
            # for reset demonstration
            if char == "":
                boxes.append("│   │")
            else:
                boxes.append(f"│ {char.upper()} │")

        return f"\n{''.join(boxes)}"

    @staticmethod
    def parse_agent_output(raw_text: str) -> dict:
        """Parses player input to extract the guessed word.
        Args:
            raw_text (str): Raw input text containing the word guess.
        Returns:
            dict: Dictionary with 'value' key containing the parsed word.
        Raises:
            ValueError: If input doesn't match expected 'Word: <word>' format.
        """
        pattern = r"word:\s*(\S+)"
        match = re.search(pattern, raw_text.lower())
        if match:
            return {"value": str(match.group(1))}
        else:
            raise ValueError(
                "Could not parse agent output. Make sure it is in the format: `Word: <word>`"
            )

    @staticmethod
    def is_valid_english_word(guess_word: str) -> bool:
        dictionary = enchant.Dict("en_US")
        return dictionary.check(guess_word)

    @staticmethod
    def compare_guess_vs_goal_word(guess_word: str, goal_word: str) -> list:
        """Compares the guess word vs goal word in wordle and provides a list output.
        Returns:
            list: Values: "clrp", "clwp", "wl" for correct letter in right position, correct letter in wrong position and wrong letter, for each letter in guess word in order.
        """
        guess_word = guess_word.lower()
        goal_word = goal_word.lower()
        comparison_status = ["wl"] * 5
        for i, (p, g) in enumerate(zip(guess_word, goal_word)):
            if p == g:
                comparison_status[i] = "clrp"

        for i, p in enumerate(guess_word):
            if p in goal_word and comparison_status[i] != "clrp":
                comparison_status[i] = "clwp"

        return comparison_status

    @staticmethod
    def convert_status_list_to_display_symbol(status: list[str]) -> list:
        conversion_dict = {"clrp": "\u2713", "clwp": "\u26a0", "wl": "\u2718"}
        return [conversion_dict[st] for st in status]


class WordleMetrics(Metrics):
    """Metrics class for Wordle
    Attributes:
        goal (str): The goal five letter word.
        success (bool):
        interactions (list[tuple[WordleAction, WordleState, WordleObservation]]):
    """

    def __init__(self, goal: str):
        super().__init__(goal)

    def similarity_function(self, action_1: WordleAction, action_2: WordleAction):
        """Returns the levenshtein ratio between two"""
        return lr(action_1.value, action_2.value)

    def progress_function(self, state: WordleState) -> float:
        """Calculates progress of a WordleState counting correct letters in right position guessed so far. Does not take into account the correct letters in wrong position."""
        comparison_lists = [
            WordleUtils.compare_guess_vs_goal_word(guess, self.goal)
            for guess in state.words_guessed
        ]
        clrp_count = 0
        for i in range(len(self.goal)):
            if any([clist[i] == "clrp" for clist in comparison_lists]):
                clrp_count += 1
        return clrp_count / len(self.goal)


class WordleDriver(Driver):
    """Driver class for Wordle.
    Attributes:
        goal (str): The goal five letter word.
        current_state (WordleState): Current game state including the guessed words and lives.
        metrics (WordleMetrics): Metrics object to record the progress of the game.
    """

    def __init__(
        self,
        goal: str,
    ):
        super().__init__(goal.lower(), metrics_class=WordleMetrics, metrics_args={})

    def reset(self) -> WordleObservation:
        """Reset game state to initial conditions. Sets the current state attribute.
        Returns:
            WordleObservation: Initial instructions and game state.
        """
        super().reset()
        self.current_state = WordleState(value="", lives=6, words_guessed=[])
        return WordleObservation(
            output=WordleUtils.get_initial_instructions(),
            success=False,
            can_proceed=True,
        )

    def step(self, action: WordleAction) -> WordleObservation:
        """Process a player's guess word and update game state.
        Args:
            action (WordleAction): Player's word guess in value.
        Returns:
            WordleObservation: Observation object with information about game state.
        """
        if not WordleUtils.is_valid_english_word(action.value):
            return WordleObservation(
                output=f"Invalid input. The word {action.value} is not a valid English word.",
                success=False,
                can_proceed=True,
            )
        if action.value.lower() in self.current_state.words_guessed:
            return WordleObservation(
                output=f"The word {action.value} is already guessed. Guess a new word.",
                success=False,
                can_proceed=True,
            )
        # Input is valid
        self.current_state.decrease_lives_by_one()
        self.current_state.set_value(action.value)
        self.current_state.add_to_guessed_list(action.value)

        comparison_status = WordleUtils.compare_guess_vs_goal_word(
            action.value, self.goal
        )
        display_symbols = WordleUtils.convert_status_list_to_display_symbol(
            comparison_status
        )
        output_str = (
            WordleUtils.print_wordle_word(action.value)
            + "\n"
            + WordleUtils.print_wordle_word(display_symbols)
            + "\n"
        )
        if action.value == self.goal:
            self.metrics.set_success(True)
            output_str += f"You have won!!! The word was {self.goal}"
            return WordleObservation(output=output_str, success=True, can_proceed=False)
        else:
            for i, st in enumerate(comparison_status):
                if st == "clrp":
                    output_str += f"Letter {action.value[i]} is a correct letter in right position.\n"
                elif st == "clwp":
                    output_str += f"Letter {action.value[i]} is a correct letter in wrong position.\n"
                else:
                    output_str += f"Letter {action.value[i]} is a wrong letter.\n"

        if self.current_state.lives == 0 and action.value != self.goal:
            output_str += f"You have lost. You have 0 lives remaining. The word was {self.goal}. \n"
            return WordleObservation(
                output=output_str, success=False, can_proceed=False
            )
        output_str += f"You have {self.current_state.lives} lives remaining. \n"
        return WordleObservation(output=output_str, success=False, can_proceed=True)

    def step_raw(
        self, raw_text: str, custom_parser: Callable | None = None
    ) -> WordleObservation:
        """Process raw text input into Wordle action and calls the step function.
        Args:
            raw_text (str): Raw input in 'Word: <word>' format.
            custom_parser (Callable | None): Optional custom parsing function.
        Returns:
            WordleObservation: Game state after processing input.
        """
        try:
            if custom_parser:
                parsed_data = custom_parser(raw_text)
                return self.step(WordleAction(**parsed_data))
            else:
                parsed_data = WordleUtils.parse_agent_output(raw_text)
                return self.step(WordleAction(**parsed_data))
        except (ValueError, ValidationError) as e:
            log_message(
                level="warning",
                message=f"Exception encountered: {str(e)}",
            )
            return WordleObservation(output=str(e), success=False, can_proceed=True)
