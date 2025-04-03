import re
from collections.abc import Callable

import pandas as pd
from datasets import load_dataset
from pydantic import ValidationError

from agentquest.lib import Action, Driver, Metrics, Observation, State
from agentquest.lib.utils import log_message


class Gsm8kAction(Action):
    """
    Placeholder Action class for GSM8k.
    Attributes:
        value (str):
    """

    pass


class Gsm8kObservation(Observation):
    """
    Placeholder Observation class for GSM8k
    Attributes:
        output: str

    """

    pass


class Gsm8kState(State):
    """Place holder State class for GSM8k.
    This would just be the answer.
    Attributes:
        value: str
    """

    pass


class Gsm8kUtils:
    @staticmethod
    def load_data(category: str = "main", split: str = "test") -> pd.DataFrame:
        category = category.lower()
        valid_categories = ["main", "socratic"]
        valid_splits = ["train", "test", "all"]

        assert (
            category in valid_categories
        ), f"Invalid category of GSM8k dataset. Possible categories are {', '.join(valid_categories)}."
        assert (
            split in valid_splits
        ), f"Invalid split. Possible splits are {', '.join(valid_splits)}."

        # Load datasets
        ds = load_dataset("openai/gsm8k", name=category, split=split)

        return ds.to_pandas()

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
    def question_scorer(
        model_answer: str,
        ground_truth: str,
    ) -> bool:
        """
        Implemented with the logic in functions extract_answer and is_correct from source:
        https://github.com/openai/grade-school-math/blob/master/grade_school_math/dataset.py
        """
        answer_re = re.compile(r"#### (\-?[0-9\.\,]+)")
        match = answer_re.search(ground_truth)
        if match:
            gt_stripped = match.group(1).strip()
            gt_stripped = gt_stripped.replace(",", "")
        else:
            gt_stripped = "[Invalid]"

        return gt_stripped.lower() == model_answer.lower()


class Gsm8kMetrics(Metrics):
    """
    Metrics class to record the interactions.
    For single interaction benchmark like Gsm8k, the metrics repetition rate and progress rate are not applicable, in non-interactive mode.
    """

    def __init__(self, goal: str, problem: str):
        super().__init__(goal)
        self.problem = problem

    def export(self, **kwargs):
        base_exports = super().export(**kwargs)
        return {"problem": self.problem, **base_exports}

    def similarity_function(
        self, action_1: Gsm8kAction, action_2: Gsm8kAction
    ) -> float:
        if action_1.value == action_2.value:
            return 1
        else:
            return 0


class Gsm8kDriver(Driver):
    """Driver class for Gsm8k
    Attributes:
        goal (str): The answer to the question asked.
        problem (str): The question to be answered.
        metrics (Gsm8kMetrics):
        interactive (bool): If True, allows multiple answer inputs.
    """

    def __init__(self, problem: str, goal: str, interactive: bool = False):
        super().__init__(
            str(goal),
            metrics_class=Gsm8kMetrics,
            metrics_args={"problem": str(problem)},
        )
        self.problem = str(problem)
        self.interactive = interactive

    def reset(self) -> Gsm8kObservation:
        super().reset()
        self.current_state = Gsm8kState(value="")
        return Gsm8kObservation(
            output=self.problem
            + "\nYour response must in the following format \nAnswer: <answer>\n",
            success=False,
            can_proceed=True,
        )

    def step(self, action: Gsm8kAction) -> Gsm8kObservation:
        super().step(action)
        self.current_state.value = action.value
        if Gsm8kUtils.question_scorer(action.value, self.goal):
            self.metrics.success = True
            return Gsm8kObservation(
                output="Correct answer!!!", success=True, can_proceed=False
            )
        elif self.interactive:
            return Gsm8kObservation(
                output="Wrong answer!!!", success=False, can_proceed=True
            )
        else:
            return Gsm8kObservation(
                output="Wrong answer!!!", success=False, can_proceed=False
            )

    def step_raw(
        self, raw_text: str, custom_parser: Callable | None = None
    ) -> Gsm8kObservation:
        """Process raw text input into Gsm8k action and calls the step function.
        Args:
            raw_text (str): Raw input in 'Answer: <answer>\n' format.
            custom_parser (Callable | None): Optional custom parsing function.
        Returns:
            Gsm8kObservation: Game state after processing input.
        """
        try:
            if custom_parser:
                parsed_data = custom_parser(raw_text)
                return self.step(Gsm8kAction(**parsed_data))
            else:
                parsed_data = Gsm8kUtils.parse_agent_output(raw_text)
                return self.step(Gsm8kAction(**parsed_data))
        except (ValueError, ValidationError) as e:
            log_message(
                level="warning",
                message=f"Exception encountered: {str(e)}",
            )
            return Gsm8kObservation(output=str(e), success=False, can_proceed=True)
