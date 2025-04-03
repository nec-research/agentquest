import os
import re
import string
from collections.abc import Callable

from datasets import load_dataset
from Levenshtein import ratio as lr
from pydantic import ValidationError

from agentquest.lib import Action, Driver, Metrics, Observation, State
from agentquest.lib.utils import log_message


class GaiaAction(Action):
    """
    Placeholder Action class for GAIA.
    Attributes:
        value (str):
    """

    pass


class GaiaObservation(Observation):
    """
    Placeholder Observation class for GAIA
    Attributes:
        output: str
        success: bool
        can_proceed: bool
    """

    pass


class GaiaState(State):
    """Place holder State class for GAIA.
    This would just be the answer.
    Attributes:
        value: str
    """

    pass


# Login using e.g. `huggingface-cli login` to access this dataset


class GaiaUtils:
    """
    Methods used to check answer (question_scorer) is adapted from huggingface gaia leaderboard scorer.py
    https://huggingface.co/spaces/gaia-benchmark/leaderboard/blob/main/scorer.py
    """

    @staticmethod
    def load_data(category: str = "2023_all", split: str = "test"):
        category = category.lower()
        valid_categories = [
            "2023_all",
            "2023_level1",
            "2023_level2",
            "2023_level3",
        ]
        valid_splits = ["validation", "test", "all"]

        assert (
            category in valid_categories
        ), f"Invalid category of GAIA dataset. Possible categories are {', '.join(valid_categories)}."
        assert (
            split in valid_splits
        ), f"Invalid split. Possible splits are {', '.join(valid_splits)}."

        ds = load_dataset("gaia-benchmark/GAIA", name=category, split=split)
        return ds.to_pandas()

    @staticmethod
    def get_filepath(filename: str, gaia_repo_path: str = "./GAIA"):
        test_directory = f"{gaia_repo_path}/2023/test/"
        validation_directory = f"{gaia_repo_path}/2023/validation/"

        if os.path.exists(test_directory + filename):
            return test_directory + filename
        elif os.path.exists(validation_directory + filename):
            return test_directory + filename
        else:
            raise ValueError(
                f"File: {filename} not found. Make sure you have cloned the GAIA project from huggingface and gaia_repo_path is correct."
            )

    @staticmethod
    def parse_agent_output(raw_text: str) -> dict:
        """Parses player input to extract the guessed letter.
        Args:
            raw_text (str): Raw input text containing the letter guess.
        Returns:
            dict: Dictionary with 'value' key containing the parsed letter.
        Raises:
            ValueError: If input doesn't match expected 'Answer: <answer>\\n' format.
        """
        pattern = r"answer:\s*(.+)"
        match = re.search(pattern, raw_text.lower())
        if match:
            return {"value": str(match.group(1))}
        else:
            raise ValueError(
                "Could not parse agent output. Make sure it is in the format: `Answer: <Answer>\\n`"
            )

    @staticmethod
    def normalize_number_str(number_str: str) -> float:
        """
        Adapted from huggingface, scorer.py
        https://huggingface.co/spaces/gaia-benchmark/leaderboard/blob/main/scorer.py
        """
        # we replace these common units and commas to allow
        # conversion to float
        for char in ["$", "%", ","]:
            number_str = number_str.replace(char, "")
        try:
            return float(number_str)
        except ValueError:
            print(f"String {number_str} cannot be normalized to number str.")
            return float("inf")

    @staticmethod
    def split_string(
        s: str,
        char_list: list[str] = [",", ";"],
    ) -> list[str]:
        pattern = f"[{''.join(char_list)}]"
        return re.split(pattern, s)

    @staticmethod
    def normalize_str(input_str, remove_punct=True) -> str:
        """
        Normalize a string by:
        - Removing all white spaces
        - Optionally removing punctuation (if remove_punct is True)
        - Converting to lowercase
        Parameters:
        - input_str: str, the string to normalize
        - remove_punct: bool, whether to remove punctuation (default: True)
        Returns:
        - str, the normalized string
        """
        # Remove all white spaces. Required e.g for seagull vs. sea gull
        no_spaces = re.sub(r"\s", "", input_str)

        # Remove punctuation, if specified.
        if remove_punct:
            translator = str.maketrans("", "", string.punctuation)
            return no_spaces.lower().translate(translator)
        else:
            return no_spaces.lower()

    @staticmethod
    def question_scorer(
        model_answer: str,
        ground_truth: str,
    ) -> bool:
        """
        Adapted from huggingface, scorer.py
        https://huggingface.co/spaces/gaia-benchmark/leaderboard/blob/main/scorer.py
        """

        def is_float(element: any) -> bool:
            try:
                float(element)
                return True
            except ValueError:
                return False

        # if gt is a number
        if is_float(ground_truth):
            print(f"Evaluating {model_answer} as a number.")
            normalized_answer = GaiaUtils.normalize_number_str(model_answer)
            return normalized_answer == float(ground_truth)

        # if gt is a list
        elif any(char in ground_truth for char in [",", ";"]):
            print(f"Evaluating {model_answer} as a comma separated list.")
            # question with the fish: normalization removes punct

            gt_elems = GaiaUtils.split_string(ground_truth)
            ma_elems = GaiaUtils.split_string(model_answer)

            # check length is the same
            if len(gt_elems) != len(ma_elems):
                log_message(
                    "warning", "Answer lists have different lengths, returning False."
                )
                return False

            # compare each element as float or str
            comparisons = []
            for ma_elem, gt_elem in zip(ma_elems, gt_elems):
                if is_float(gt_elem):
                    normalized_ma_elem = GaiaUtils.normalize_number_str(ma_elem)
                    comparisons.append(normalized_ma_elem == float(gt_elem))
                else:
                    # we do not remove punct since comparisons can include punct
                    comparisons.append(
                        GaiaUtils.normalize_str(ma_elem, remove_punct=False)
                        == GaiaUtils.normalize_str(gt_elem, remove_punct=False)
                    )
            return all(comparisons)

        # if gt is a str
        else:
            print(f"Evaluating {model_answer} as a string.")
            return GaiaUtils.normalize_str(model_answer) == GaiaUtils.normalize_str(
                ground_truth
            )


class GaiaMetrics(Metrics):
    """
    Metrics class to record the interactions.
    For single interaction benchmark like Gaia, the metrics repetition rate and progress rate are not applicable, in non-interactive mode.
    """

    def __init__(self, goal: str, problem: str):
        super().__init__(goal)
        self.problem = problem

    def similarity_function(self, action_1: GaiaAction, action_2: GaiaAction) -> float:
        return lr(action_1.value, action_2.value)

    def export(self, **kwargs):
        base_exports = super().export(**kwargs)
        return {"problem": self.problem, **base_exports}


class GaiaDriver(Driver):
    """Driver class for Gaia
    Attributes:
        goal (str): The answer to the question asked.
        problem (str): The question asked.
        metrics (GaiaMetrics):
        interactive (bool): If True, allows multiple answer inputs.
    """

    def __init__(self, problem: str, goal: str, interactive: bool = False):
        super().__init__(
            str(goal), metrics_class=GaiaMetrics, metrics_args={"problem": str(problem)}
        )
        self.problem = str(problem)
        self.interactive = interactive

    def reset(self) -> GaiaObservation:
        super().reset()
        self.current_state = GaiaState(value="")
        return GaiaObservation(
            output=self.problem
            + "\nYour response must in the following format \nAnswer: <answer>\n",
            success=False,
            can_proceed=True,
        )

    def step(self, action: GaiaAction) -> GaiaObservation:
        super().step(action)
        self.current_state.value = action.value
        if GaiaUtils.question_scorer(action.value, self.goal):
            self.metrics.success = True
            return GaiaObservation(
                output="Correct answer!!!", success=True, can_proceed=False
            )
        elif self.interactive:
            return GaiaObservation(
                output="Wrong answer!!!", success=False, can_proceed=True
            )
        else:
            return GaiaObservation(
                output="Wrong answer!!!", success=False, can_proceed=False
            )

    def step_raw(
        self, raw_text: str, custom_parser: Callable | None = None
    ) -> GaiaObservation:
        """Process raw text input into Gaia action and calls the step function.
        Args:
            raw_text (str): Raw input in 'Answer: <answer>\n' format.
            custom_parser (Callable | None): Optional custom parsing function.
        Returns:
            GaiaObservation: Game state after processing input.
        """
        try:
            if custom_parser:
                parsed_data = custom_parser(raw_text)
                return self.step(GaiaAction(**parsed_data))
            else:
                parsed_data = GaiaUtils.parse_agent_output(raw_text)
                return self.step(GaiaAction(**parsed_data))
        except (ValueError, ValidationError) as e:
            log_message(
                level="warning",
                message=f"Exception encountered: {str(e)}",
            )
            return GaiaObservation(output=str(e), success=False, can_proceed=True)
