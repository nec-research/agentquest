import random
import re
from collections.abc import Callable
from math import log2

from pydantic import ValidationError, field_validator

from agentquest.lib import Action, Driver, Metrics, Observation, State
from agentquest.lib.utils import log_message


class TTFEAction(Action):
    """
    Represents an action in the 2048 game (TTFE - "Two Thousand Forty-Eight").
    The value corresponds to moving tiles in one of four directions: up (w), down (a), left (s), or right (d).
    Attributes:
        value (str):
    """

    @field_validator("value")
    @classmethod
    def check_value(cls, value: str) -> str:
        """Validates the action value to ensure it is a valid move character (w,a,s,d)."""
        if value.lower() not in ["w", "a", "s", "d"]:
            raise ValueError("Action should be one of the characters: w,a,s,d")
        return value.lower()


class TTFEObservation(Observation):
    """
    This is a placeholder class and inherits directly from `Observation` without adding new attributes or methods.
    Attributes:
        output (str):
        success (bool):
        can_proceed (bool):
    """

    pass


class TTFEState(State):
    """
    Represents the board of the 2048 game.
    Attributes:
        value (list[list[int]]): A 2D list representing the 4x4 grid of the game board,
                                 where each element is an integer corresponding to a tile value.
                                 Empty tiles are represented by 0.
    """

    value: list[list[int]]


class TTFEUtils:
    @staticmethod
    def find_max_value(state: TTFEState):
        max_value = float("-inf")
        for row in state.value:
            row_max = max(row)
            if row_max > max_value:
                max_value = row_max
        return max_value

    @staticmethod
    def get_initial_instructions() -> str:
        message = (
            "Welcome to 2048!\n"
            "Use 'w', 'a', 's', 'd' to move the tiles, where each move respectively moves all blocks that can move in the given direction:\n"
            "'up', 'left', 'down', 'right'.\n"
            "Your goal is to make the 2048 block, you work towards this by merging tiles of the same value with your movement keys.\n"
            "The merged block will be the sum of the previous values of the blocks. You lose when no valid moves are possible.\n"
            "Initially, two blocks appear, after each move following that a block will spawn. There is a 90 percent chance for it to be a '2' and a 10 percent chance for it to be a '4'.\n"
            "You will receive feedback after you make a move: verbally and with a matrix. Base your moves on the feedback provided.\n"
            "Your response should be strictly in the following format: \n"
            "Move: <w|a|s|d>\n"
        )
        return message

    @staticmethod
    def print_board(state: TTFEState):
        output = "╔══════╦══════╦══════╦══════╗\n"
        for i in range(4):
            output += (
                "║"
                + "║".join(
                    f"{num:^6}" if num != 0 else "      " for num in state.value[i]
                )
                + "║\n"
            )
            if i < 3:
                output += "╠══════╬══════╬══════╬══════╣\n"
        output += "╚══════╩══════╩══════╩══════╝\n"
        return output

    @staticmethod
    def compress(row: list[int]) -> list[int]:
        """Compresses a row by moving all non-zero values to the left and filling the remaining spaces with zeros."""
        return [num for num in row if num != 0] + [0] * row.count(0)

    @staticmethod
    def merge(row: list[int]) -> list[int]:
        """Merges adjacent tiles with the same value in a row."""
        for i in range(len(row) - 1):
            if row[i] == row[i + 1] and row[i] != 0:
                row[i] *= 2
                row[i + 1] = 0
        return row

    @staticmethod
    def reorientate(matrix: list[list[int]]) -> list[list[int]]:
        """Transpose the matrix"""
        return [
            [matrix[row][col] for row in range(len(matrix))]
            for col in range(len(matrix[0]))
        ]

    @staticmethod
    def parse_agent_output(raw_text: str) -> dict:
        """
        Parses the agent's raw text input to extract the move direction.
        Args:
            raw_text (str): The raw text input from the agent. Expected format: "Move: <w|a|s|d>"
        Returns:
            dict: A dictionary containing the parsed move value in the format {"value": <w|a|s|d>}.
        Raises:
            ValueError: If the input text does not match the expected format.
        """
        pattern = r"move:\s*([wasd])"
        match = re.search(pattern, raw_text.lower())
        if match:
            return {"value": str(match.group(1))}
        else:
            raise ValueError(
                "Could not parse agent output. Make sure it is in the format: Move: <w|a|s|d>"
            )


class TTFEMetrics(Metrics):
    """
    A subclass of the Metrics class.
    Attributes:
        goal (int):
        success (bool):
        interactions (list[tuple[TTFEAction, TTFEState, TTFEObservation]]): All interactions between agent and the game
        legal_move_history (list[tuple[TTFEAction, TTFEState, TTFEObservation]]): A history of legal moves made during the interaction.
        illegal_move_history (list[tuple[TTFEAction, TTFEState, TTFEObservation]]): A history of illegal moves made during the interaction.
    """

    def __init__(self, goal: int):
        super().__init__(goal=goal)
        self.legal_move_history: list[
            tuple[
                TTFEAction,
                TTFEState,
                TTFEObservation,
            ]
        ] = []
        self.illegal_move_history: list[
            tuple[
                TTFEAction,
                TTFEState,
                TTFEObservation,
            ]
        ] = []

    def similarity_function(
        self,
        action_1: TTFEAction,
        action_2: TTFEAction,
    ) -> float:
        return 1 if action_1.value == action_2.value else 0

    def progress_function(self, state: TTFEState) -> float:
        return round(log2(TTFEUtils.find_max_value(state)) / log2(self.goal), 2)

    def add_to_legal_move(
        self,
        interaction: tuple[
            TTFEAction,
            TTFEState,
            TTFEObservation,
        ],
    ):
        self.legal_move_history.append(interaction)

    def add_to_illegal_move(
        self,
        interaction: tuple[
            TTFEAction,
            TTFEState,
            TTFEObservation,
        ],
    ):
        self.illegal_move_history.append(interaction)

    def get_repetitions_legal_moves(self) -> int:
        return self.repetition_function(
            theta_a=1,
            actions=[act for act, _, _ in self.legal_move_history if act is not None],
        )

    def get_repetitions_illegal_moves(self) -> int:
        return self.repetition_function(
            theta_a=1,
            actions=[act for act, _, _ in self.illegal_move_history if act is not None],
        )


class TTFEDriver(Driver):
    """
    Driver class for 2048 game.
    Attributes:
        goal (int): The target number for the game. Default value: 2048.
        current_state (TTFEState): State of the game, updated every time the game progresses.
        metrics (TTFEMetrics): metrics object which records the interactions
    """

    def __init__(self, goal: int = 2048):
        super().__init__(
            goal=goal,
            metrics_class=TTFEMetrics,
        )

    def place_random_tile(self):
        """Places a new random tile (either 2 or 4) in an empty position on the game board."""
        empty_positions = [
            (r, c)
            for r in range(4)
            for c in range(4)
            if self.current_state.value[r][c] == 0
        ]
        if empty_positions:
            r, c = random.choice(empty_positions)
            self.current_state.value[r][c] = 2 if random.random() < 0.9 else 4

    def move_horizontal(self, direction: str) -> bool:
        """Moves all tiles in the specified horizontal direction (left or right), compressing and merging them."""
        moved = False
        new_matrix = []

        for row in self.current_state.value:
            original_row = row[:]
            if direction == "right":
                row = row[::-1]

            compressed_row = TTFEUtils.compress(row)
            merged_row = TTFEUtils.merge(compressed_row)
            final_row = TTFEUtils.compress(merged_row)

            if direction == "right":
                final_row = final_row[::-1]

            new_matrix.append(final_row)
            if original_row != final_row:
                moved = True

        self.current_state.value = new_matrix
        return moved

    def move_vertical(self, direction: str) -> bool:
        """Moves all tiles in the specified vertical direction (up or down), compressing and merging them."""
        moved = False
        self.current_state.value = TTFEUtils.reorientate(self.current_state.value)

        if direction == "down":
            moved = self.move_horizontal("right")
        else:  # up
            moved = self.move_horizontal("left")

        self.current_state.value = TTFEUtils.reorientate(self.current_state.value)
        return moved

    def movement(self, move: str):
        """Executes a move based on the provided input character ('w', 'a', 's', 'd') and updates the game state."""
        if move == "a":  # Move left
            return self.move_horizontal("left")
        elif move == "d":  # Move right
            return self.move_horizontal("right")
        elif move == "w":  # Move up
            return self.move_vertical("up")
        elif move == "s":  # Move down
            return self.move_vertical("down")
        return False

    def win_check(self) -> bool:
        """Checks whether the game has been won by finding the goal value in any row of the game state."""
        return any(self.goal in row for row in self.current_state.value)

    def lose_check(self) -> bool:
        """Checks whether the game has been lost, which occurs when there are no valid moves left."""
        if any(0 in row for row in self.current_state.value):
            return False

        for row in self.current_state.value:
            if any(row[col] == row[col + 1] for col in range(3)):
                return False

        for col in range(4):
            if any(
                self.current_state.value[row][col]
                == self.current_state.value[row + 1][col]
                for row in range(3)
            ):
                return False
        return True

    def reset(self):
        """
        Resets the game to its initial state, sets current_state attribute, placing two random tiles on the board and providing initial instructions.

        Returns:
            TTFEObservation: An observation object containing the initial instructions and the current game state.
        """
        super().reset()
        self.current_state = TTFEState(value=[[0] * 4 for _ in range(4)])
        self.place_random_tile()
        self.place_random_tile()

        obs = TTFEObservation(
            output=TTFEUtils.get_initial_instructions()
            + TTFEUtils.print_board(self.current_state),
            success=False,
            can_proceed=True,
        )
        return obs

    def step(self, action: TTFEAction):
        """
        Executes a single move based on the provided action and updates the game state accordingly.
        Args:
            action (TTFEAction): The action object containing the move direction (one of 'w', 'a', 's', 'd').
        Returns:
            TTFEObservation: An observation object containing the result of the move, including the updated game state and status.
        """
        super().step(action=action)
        value = action.value
        moved = self.movement(value)

        if not moved:
            # No change
            obs = TTFEObservation(
                output="Move did not change the board. Please enter 'w', 'a', 's', or 'd'.\n\n"
                + TTFEUtils.print_board(self.current_state),
                success=False,
                can_proceed=True,
            )
            self.metrics.add_to_illegal_move((action, self.current_state, obs))
            return obs

        if self.win_check():
            # Game won
            obs = TTFEObservation(
                output="You have won!\n\n" + TTFEUtils.print_board(self.current_state),
                success=True,
                can_proceed=False,
            )
            self.metrics.add_to_legal_move((action, self.current_state, obs))
            return obs

        self.place_random_tile()
        if self.lose_check():
            # Game lost
            obs = TTFEObservation(
                output="You have lost! No more possible moves.\n\n"
                + TTFEUtils.print_board(self.current_state),
                success=False,
                can_proceed=False,
            )
            self.metrics.add_to_legal_move((action, self.current_state, obs))
            return obs
        # Neither won, nor lost
        obs = TTFEObservation(
            output="Valid move, enter your next move:\n\n"
            + TTFEUtils.print_board(self.current_state),
            success=False,
            can_proceed=True,
        )
        self.metrics.add_to_legal_move((action, self.current_state, obs))
        return obs

    def step_raw(
        self, raw_text: str, custom_parser: Callable | None = None
    ) -> TTFEObservation:
        """
        Processes raw text input from the agent, parses it, and performs a move in the game.
        Args:
            raw_text (str): The raw text input from the agent, expected to be in the format `Move: <w|a|s|d>`.
            custom_parser (Callable | None, optional): A custom parsing function to parse the raw text, if provided.
        Returns:
            TTFEObservation: An observation object returned by the `step` method after executing the parsed move.
        """
        try:
            if custom_parser:
                parsed_data = custom_parser(raw_text)
                return self.step(TTFEAction(**parsed_data))
            else:
                parsed_data = TTFEUtils.parse_agent_output(raw_text)
                return self.step(TTFEAction(**parsed_data))
        except (ValueError, ValidationError) as e:
            log_message(
                level="warning",
                message=f"Exception encountered: {str(e)}",
            )
            return TTFEObservation(
                output=str(e) + TTFEUtils.print_board(self.current_state),
                success=False,
                can_proceed=True,
            )
