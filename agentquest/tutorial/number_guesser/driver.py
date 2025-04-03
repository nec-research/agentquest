import math

from agentquest.lib import Action, Driver, Metrics, Observation, State


class NumberGuesserAction(Action):
    """Action class for NumberGuesser game
    Attributes:
        value (str) : New guess from the agent."""

    pass


class NumberGuesserObservation(Observation):
    """Observation class as feedback from game to the agent.
    Attributes:
        output (str) :
        success (bool) :
        can_proceed (bool) :
    """

    pass


class NumberGuesserState(State):
    """State class for NumberGuesser game
    Attributes:
        value (str) : Last guessed number."""

    pass


class NumberGuesserMetrics(Metrics):
    def __init__(self, goal: str):
        super().__init__(goal)

    def similarity_function(
        self, action_1: NumberGuesserAction, action_2: NumberGuesserAction
    ):
        if action_1.value == action_2.value:
            return 1
        else:
            return 0

    def progress_function(self, state: NumberGuesserState) -> float | int:
        guess = int(state.value)
        target = int(self.goal)
        if guess == target:
            return 1.0

        # Calculate the difference and asymptotic progress
        diff = abs(target - guess)
        progress = 1 / (1 + math.log1p(diff))
        return progress


class NumberGuesserDriver(Driver):
    def __init__(
        self,
        goal: str,
    ):
        super().__init__(goal, metrics_class=NumberGuesserMetrics)

    def reset(self) -> NumberGuesserObservation:
        super().reset()
        self.current_state = NumberGuesserState(value="0")
        return NumberGuesserObservation(
            output=(
                "Welcome to number guessing game. Your goal is to guess the integer number.\n"
                "On each guess, you shall be provided the information if the actual number is greater or smaller than the guess.\n"
                "Based on the feedback, correct your guess.\n"
                "Make a guess.\n"
            ),
            success=False,
            can_proceed=True,
        )

    def step(self, action: NumberGuesserAction) -> NumberGuesserObservation:
        super().step(action)
        output_str = ""
        self.current_state.value = action.value
        if int(action.value) == int(self.goal):
            output_str += "You have won!!!\n"
            return NumberGuesserObservation(
                output=output_str, success=True, can_proceed=False
            )

        if int(action.value) > int(self.goal):
            output_str += (
                "The target number is smaller than the guessed number. Guess again.\n"
            )

        else:
            output_str += (
                "The target number is greater than the guessed number. Guess again.\n"
            )
        return NumberGuesserObservation(
            output=output_str, success=False, can_proceed=True
        )
