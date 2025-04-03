import copy
import importlib.resources
import json
import re
from collections.abc import Callable

from Levenshtein import ratio as lr
from pydantic import ValidationError, field_validator

from agentquest.lib import Action, Driver, Metrics, Observation, State
from agentquest.lib.utils import log_message


class SudokuUtils:
    """Utility class for Sudoku, providing static methods for game instructions, board conversion, data loading, and parsing agent outputs."""

    @staticmethod
    def get_initial_instructions() -> str:
        message = (
            "Welcome to Sudoku.\n"
            'Sudoku is a logic-based number puzzle game played on a 9x9 grid, divided into nine 3x3 subgrids called "regions."\n'
            "The objective is to fill the grid so that each row, each column, and each 3x3 region contains all digits from 1 to 9 without repetition.\n"
            "The puzzle starts with some cells pre-filled with numbers, which serve as clues.\n"
            "You will be provided the state of the game every time the game progresses.\n"
            "Your response should contain what the next number will be and in which row and column.\n"
            "The rows and columns both range from 0 to 8 (zero-based indexing), and the value of digits is from 1 to 9.\n"
            "The response should be exactly in the following format:\n"
            "Row: <row_number>, Column: <column_number>, Value: <value>\n"
        )
        return message

    @staticmethod
    def convert_board_to_list_of_lists(board_state: str) -> list[list[str]]:
        return [x.split("|") for x in board_state.split("\r\n")]

    @staticmethod
    def load_data(data_path: str = "__default__", category: str = "easy"):
        """
        Loads Sudoku puzzles from a JSON file based on the specified difficulty category.

        Args:
            data_path (str, optional): The path to the JSON file containing Sudoku puzzles.
                                       if __default__ then Defaults to "./games.json".
            category (str, optional): The difficulty level of the puzzles to load.
                                      Must be one of ["easy", "medium", "hard"].
                                      Defaults to "easy".

        Returns:
            dict: A dictionary containing puzzles for the specified category.

        Raises:
            AssertionError: If the specified category is not in ["easy", "medium", "hard"].
        """

        categories = ["easy", "medium", "hard"]
        assert (
            category in categories
        ), f"Invalid category: {category}. Category can be one of the following: {', '.join(categories)}"
        if data_path == "__default__":
            with importlib.resources.open_text(
                "agentquest.benchmarks.sudoku", "data.json"
            ) as fp:
                data = json.loads(fp.read())
        else:
            with open(data_path, "r") as fp:
                data = json.load(fp)
        return data[category]

    @staticmethod
    def parse_agent_output(raw_text: str) -> dict:
        """
        Parses the agent's output text to extract the row, column, and value for a SudokuAction.
        Args:
            raw_text (str): The agent's response in the format:
                            "Row: <row_number>, Column: <column_number>, Value: <value>".

        Returns:
            dict: A dictionary containing:
                - "row" (int): The row index of the move (0-8).
                - "column" (int): The column index of the move (0-8).
                - "value" (str): The value to be placed at the specified cell (1-9).

        Raises:
            ValueError: If the text does not match the expected format.
        """
        pattern = r"row:\s*(\d+),\s*column:\s*(\d+),\s*value:\s*(\d+)"
        match = re.search(pattern, raw_text.lower())
        if match:
            return {
                "row": int(match.group(1)),
                "column": int(match.group(2)),
                "value": str(int(match.group(3))),
            }
        else:
            raise ValueError(
                "Could not parse agent output. Make sure it is in format: Row: <row_number>, Column: <column_number>, Value: <value>"
            )


class SudokuAction(Action):
    """
    Represents an action in a Sudoku game, including the row, column, and value to be placed.

    Attributes:
        row (int): The row index where the action is performed (0-8).
        column (int): The column index where the action is performed (0-8).
        value (str): The value (1-9) to place in the specified cell.
    """

    row: int
    column: int

    @field_validator("value")
    @classmethod
    def check_value(cls, value: str) -> str:
        """
        Validates the `value` field to ensure it is a single-digit string between 1 and 9.
        """
        if len(value) != 1:
            raise ValueError("must be a number from 1 to 9")
        if int(value) < 1 or int(value) > 9:
            raise ValueError("must be a number from 1 to 9")
        return str(value)

    @field_validator("row", "column")
    @classmethod
    def check_row_column(cls, value: int) -> int:
        """Validates the `row` and `column` fields to ensure they are integers between 0 and 8."""
        if value < 0 or value > 8:
            raise ValueError("must be a number from 0 to 8")
        return value


class SudokuObservation(Observation):
    """
    Represents an observation returned after an action in the Sudoku game.
    Attributes:
        output (str):
        success (bool):
        can_proceed (bool):
    """

    pass


class SudokuState(State):
    """
    Represents the current state of the Sudoku grid.
    Attributes:
        value (list[list[str]]): A 2D list representing the 9x9 Sudoku grid.
                                 Empty cells are represented by "*".
    """

    value: list[list[str]]

    @field_validator("value")
    def validate_state_value(cls, value: list[list[str]]) -> list[list[str]]:
        """Validates the `value` field to ensure it represents a 9x9 Sudoku grid."""
        if len(value) != 9:
            raise ValueError("State must be a list of list of strings of shape (9,9).")
        for row in value:
            if len(row) != 9:
                raise ValueError(
                    "State must be a list of list of strings of shape (9,9)."
                )
        return value


class SudokuMetrics(Metrics):
    """A metrics class for evaluating the progress and quality of actions in a Sudoku benchmark.
    Attributes:
        goal (list[list[str]]):
        success (bool):
        interactions (list[tuple[SudokuAction, SudokuState, SudokuObservation]]): All interactions between agent and the game
    """

    def __init__(self, goal: list[list[str]]):
        """
        Initializes the SudokuMetrics instance with the target solution (goal).
        Args:
            goal (list[list[str]]): A 2D list representing the solution grid of the Sudoku puzzle.
        """
        super().__init__(goal=goal)

    def similarity_function(
        self, action_1: SudokuAction, action_2: SudokuAction
    ) -> float:
        """
        Determines the similarity between two Sudoku actions based on their values.
        """
        return lr(
            str(action_1.row) + str(action_1.column) + str(action_1.value),
            str(action_2.row) + str(action_2.column) + str(action_2.value),
        )

    def progress_function(self, state: SudokuState) -> int:
        """
        Calculates the progress of the game by counting the number of cells which match the goal state.
        """

        incorrect_cells = 0
        for i in range(0, 9):
            for j in range(0, 9):
                if state.value[i][j] == "*":
                    continue
                elif state.value[i][j] != self.goal[i][j]:
                    incorrect_cells += 1

        filled_cells = sum(1 for cell in sum(state.value, []) if cell != "*")
        return (filled_cells - incorrect_cells) / 81


class SudokuDriver(Driver):
    """
    A driver class for managing the logic and progression of a Sudoku benchmark.
    Attributes:
        goal (list[list[str]]): The target Sudoku grid, typically representing the solution.
        initial_state (SudokuState): The starting state of the Sudoku grid.
        current_state (SudokuState): State of the game, updated every time the game progresses.
        metrics (SudokuMetrics): metrics object which records the interactions
    """

    def __init__(self, goal: list[list[str]], initial_state: list[list[str]]):
        super().__init__(goal, metrics_class=SudokuMetrics)
        self.goal = goal
        self.initial_state = SudokuState(value=initial_state)

    def reset(self) -> SudokuObservation:
        """
        Resets the game to its initial state, sets current_state attribute and provides the initial instructions to the player.

        Returns:
            SudokuObservation:
        """
        super().reset()
        self.current_state = copy.deepcopy(self.initial_state)
        return SudokuObservation(
            output=SudokuUtils.get_initial_instructions()
            + "Current game state: \n"
            + str(self.current_state.value),
            success=False,
            can_proceed=True,
        )

    def step(self, action: SudokuAction) -> SudokuObservation:
        """
        Processes a player's action, updates the game state, and returns the updated game state.
        Args:
            action (SudokuAction): An action object containing the row, column,
                                   and value to be placed on the Sudoku grid.
        Returns:
            SudokuObservation: Updated game state.
        """
        super().step(action)
        row = action.row
        column = action.column
        value = str(action.value)

        if self.invalid_quadrant(row, column, value):
            return SudokuObservation(
                output=(
                    f"Inadmissible action. There is already a {value} in the "
                    "provided quadrant."
                ),
                success=False,
                can_proceed=True,
            )
        if self.invalid_rows(row, value):
            return SudokuObservation(
                output=f"Inadmissible action. {value} is already in row {row}.",
                success=False,
                can_proceed=True,
            )
        if self.invalid_cols(column, value):
            return SudokuObservation(
                output=f"Inadmissible action. {value} is already in column {column}.",
                success=False,
                can_proceed=True,
            )
        if self.already_a_number(row, column):
            return SudokuObservation(
                output=(
                    "Inadmissible action. You cannot change the value of a "
                    "starting number."
                ),
                success=False,
                can_proceed=True,
            )

        self.current_state.value[row][column] = value
        if not self.is_finished():
            obs = SudokuObservation(
                output=str(self.current_state.value),
                success=False,
                can_proceed=True,
            )
        elif self.valid_game():
            self.metrics.set_success(True)
            obs = SudokuObservation(
                output="You won!!!", success=True, can_proceed=False
            )
        else:
            obs = SudokuObservation(
                output="You lost!!!", success=True, can_proceed=False
            )
        return obs

    def step_raw(
        self, raw_text: str, custom_parser: Callable | None = None
    ) -> SudokuObservation:
        """
        Parses raw text input from an agent and executes the corresponding action.
        Args
            raw_text: raw_text output from the agent. Expected Data Format: Row: <row_number>, Column: <column_number>, Value: <value>\n
            custom_parser: function that parses raw_text and returns dictionary to be provided as arguments to SudokuAction.
        Returns
            SudokuObservation object returned by step function.
        """
        try:
            if custom_parser:
                parsed_data = custom_parser(raw_text)
                return self.step(SudokuAction(**parsed_data))
            else:
                parsed_data = SudokuUtils.parse_agent_output(raw_text)
                return self.step(SudokuAction(**parsed_data))
        except (ValueError, ValidationError) as e:
            log_message(
                level="warning",
                message=f"Exception encountered: {str(e)}",
            )
            return SudokuObservation(output=str(e), success=False, can_proceed=True)

    def invalid_rows(self, row: int, value: str):
        return value in self.current_state.value[row]

    def invalid_cols(self, column: int, value: str):
        return any(self.current_state.value[i][column] == value for i in range(9))

    def already_a_number(self, row: int, column: int):
        return self.initial_state.value[row][column] != "*"

    def invalid_quadrant(self, row: int, column: int, value: str):
        row_idx = (row // 3) * 3
        col_idx = (column // 3) * 3

        for i in range(3):
            for j in range(3):
                if self.current_state.value[row_idx + i][col_idx + j] == value:
                    return True
        return False

    def is_finished(self):
        return all("*" not in row for row in self.current_state.value)

    def valid_game(self):
        for i in range(9):
            for j in range(9):
                if self.current_state.value[i][j] != self.goal[i][j]:
                    return False
        return True
