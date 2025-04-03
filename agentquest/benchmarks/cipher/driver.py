import importlib.resources
import json
import re
from collections.abc import Callable

from Levenshtein import ratio as lr
from pydantic import ValidationError

from agentquest.benchmarks.cipher.algorithms import (
    ADFGVX,
    Affine,
    Atbash,
    Caesar,
    RailFence,
    Vigenere,
)
from agentquest.lib import Action, Driver, Metrics, Observation, State
from agentquest.lib.utils import log_message


class CipherUtils:
    ALGORITHMS = ["caesar", "atbash", "affine", "vigenere", "railfence", "adfgvx"]

    @staticmethod
    def load_data(data_path: str = "__default__"):
        """
        Loads the data from a JSON file and returns the list of plain texts.
        Args:
            data_path (str, optional): The file path to the JSON data file. If __default__, it defaults to 'agentquest/benchmarks/cipher/data.json'. Consists of list of plain texts.
        Returns:
            list[str]: A list of plain texts corresponding to the specified category.
        """
        if data_path == "__default__":
            with importlib.resources.open_text(
                "agentquest.benchmarks.cipher", "data.json"
            ) as fp:
                data = json.loads(fp.read())
        else:
            with open(data_path, "r") as fp:
                data = json.load(fp)
        return data

    @staticmethod
    def get_cipher_class(algorithm: str):
        assert (
            algorithm in CipherUtils.ALGORITHMS
        ), f"Cipher algorithm {algorithm} is not supported."
        if algorithm == "caesar":
            return Caesar
        elif algorithm == "atbash":
            return Atbash
        elif algorithm == "affine":
            return Affine
        elif algorithm == "vigenere":
            return Vigenere
        elif algorithm == "railfence":
            return RailFence
        elif algorithm == "adfgvx":
            return ADFGVX

    @staticmethod
    def parse_agent_output(raw_text: str) -> dict:
        """
        Parses the agent's output to extract the guessed number in the expected format.
        Args:
            raw_text (str): The raw output text from the agent, which should contain a guess in the format "Plain Text: <decrypted_text>".
        Returns:
            dict: A dictionary containing the parsed guess, e.g., {"value": "decrypted plain text"}.
        Raises:
            ValueError: If the raw text is not in the expected format.
        """
        pattern = r"plain text:\s*(.+)"
        match = re.search(pattern, raw_text.lower())
        if match:
            return {"value": str(match.group(1))}
        else:
            raise ValueError(
                "Could not parse agent output. Make sure it is in the format: Plain Text: <decrypted_text>"
            )


class CipherAction(Action):
    """Placeholder CipherAction class for Cipher benchmark.
    Attributes:
        value (str): agent's guess
    """

    pass


class CipherState(State):
    """
    Placeholder class for CipherState inherited from base class State.
    Attributes:
        value (str): last guessed value
    """

    pass


class CipherObservation(Observation):
    """
    Placeholder class for CipherObservation inherited from base class Observation.
    Attributes:
        output (str):
        success (bool):
        can_proceed (bool):
    """

    pass


class CipherDriver(Driver):
    """
    Driver class for Cipher benchmark.

    Attributes:
        goal (str): plaintext which is the goal for an agent
        cipher_text (str): ciphertext that an agent shall decode
        cipher_algorithm (class): Algorithm class from one of the supported algorithms in cipher/algorithms.
        match_threshold (float): Between 0 to 1, default 0.95, Levenshtein ratio threshold for comparison between goal plaintext and agent's deciphered text. If the calculated ratio is higher than the threshold, the task is completed i.e. Observation returns success=True.
        current_state (CipherState): current state of the game, i.e. agent's last guess
        metrics (CipherMetrics): metrics object to keep record of the progress
    """

    def __init__(
        self, goal=None, algorithm: str = "caesar", match_threshold: float = 0.95
    ):
        assert (
            algorithm in CipherUtils.ALGORITHMS
        ), f"Algorithm: {algorithm} not supported. Make sure you select one of the following: {', '.join(CipherUtils.ALGORITHMS)}"
        super().__init__(
            goal,
            metrics_class=CipherMetrics,
            metrics_args={"algorithm": algorithm, "match_threshold": match_threshold},
        )
        self.algorithm = algorithm
        self.cipher_class = CipherUtils.get_cipher_class(algorithm)
        self.match_threshold = match_threshold

    def reset(self):
        """
        Resets the game state and provides initial instructions, based on the cipher.
        Returns:
            CipherObservation: An observation containing the initial instructions and the start message.
        """
        super().reset()
        algorithm_parameters = self.cipher_class.generate_random_parameters()
        self.metrics.set_algorithm_parameters(algorithm_parameters)
        self.cipher_text = self.cipher_class.encrypt(
            **algorithm_parameters, plain_text=self.goal
        )
        self.metrics.set_cipher_text(self.cipher_text)
        self.current_state = CipherState(value="")

        return CipherObservation(
            output=self.cipher_class.get_initial_instructions()
            + f"\nHere is the cipher text to decrypt:\n{self.cipher_text}\n"
            + "Your response must be in the following format: \nPlain Text: <decrypted_text>\n",
            success=False,
            can_proceed=True,
        )

    def step(self, action):
        super().step(action)
        self.current_state.value = action.value

        if lr(action.value, self.goal) >= self.match_threshold:
            return CipherObservation(
                output="You've won !!!. Cipher text successfully decrypted.",
                success=True,
                can_proceed=False,
            )
        else:
            return CipherObservation(
                output="Wrong answer!!! The text does not match with the original plain text. Try again.",
                success=False,
                can_proceed=True,
            )

    def step_raw(
        self, raw_text: str, custom_parser: Callable | None = None
    ) -> CipherObservation:
        """
        Args
            raw_text (str): The raw output from the agent, expected to contain a guess in the format `Plain Text: <decrypted_text>`
            custom_parser (Callable, optional): A custom parser function to process the raw text. If None, the default parser is used.
        Returns
            CipherObservation: An observation object returned by step function.
        """
        try:
            if custom_parser:
                parsed_data = custom_parser(raw_text)
                return self.step(CipherAction(**parsed_data))
            else:
                parsed_data = CipherUtils.parse_agent_output(raw_text)
                return self.step(CipherAction(**parsed_data))
        except (ValueError, ValidationError) as e:
            log_message(
                level="warning",
                message=f"Exception encountered: {str(e)}",
            )
            return CipherObservation(output=str(e), success=False, can_proceed=True)


class CipherMetrics(Metrics):
    def __init__(self, goal: str, algorithm: str, match_threshold: float):
        super().__init__(goal)
        self.algorithm = algorithm
        self.match_threshold = match_threshold

    def set_cipher_text(self, cipher_text: str):
        self.cipher_text = cipher_text

    def set_algorithm_parameters(self, algorithm_parameters: dict):
        self.algorithm_parameters = algorithm_parameters

    def progress_function(self, state: CipherState):
        """Calculate progress towards the goal. This is done by calculating Levenshtein ratio between agent's last guess and goal plaintext."""
        return round(lr(state.value, self.goal), 3)

    def similarity_function(self, action_1: CipherAction, action_2: CipherAction):
        """Compute similarity between two Cipher actions."""
        return lr(action_1.value, action_2.value)

    def export(
        self, repetition_function_kwargs: dict = {}, progress_function_kwargs: dict = {}
    ):
        data = super().export(repetition_function_kwargs, progress_function_kwargs)
        return {
            "algorithm": self.algorithm,
            "cipher_text": self.cipher_text,
            "algorithm_parameters": self.algorithm_parameters,
            "match_threshold": self.match_threshold,
            **data,
        }
