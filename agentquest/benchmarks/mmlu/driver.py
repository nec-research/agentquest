import re
from collections.abc import Callable

import pandas as pd
from datasets import load_dataset
from pydantic import ValidationError, field_validator

from agentquest.lib import Action, Driver, Metrics, Observation, State
from agentquest.lib.utils import log_message


class MmluAction(Action):
    """
    Represents an agents guess in MMLU.
    Attributes:
        value (str): A single uppercase alphabetical character A|B|C|D.
    Raises:
        ValueError: If input is not alphabetical or not exactly one character.
    """

    @field_validator("value")
    @classmethod
    def check_mmlu_guess(cls, value: str) -> str:
        if not value.isalpha():
            raise ValueError("Only alphabetical characters allowed.")
        if value.upper() not in ["A", "B", "C", "D"]:
            raise ValueError("For MMLU, allowed guesses are A,B,C,D only.")
        else:
            return value.upper()


class MmluObservation(Observation):
    """
    Placeholder Observation class for MMLU
    Attributes:
        output: str

    """

    pass


class MmluState(State):
    """Place holder State class for MMLU.
    This would just be the answer.
    Attributes:
        value: str
    """

    pass


class MmluUtils:
    @staticmethod
    def load_data(category: str = "main", split: str = "test") -> pd.DataFrame:
        category = category.lower()
        valid_categories = [
            "abstract_algebra",
            "all",
            "anatomy",
            "astronomy",
            "auxiliary_train",
            "business_ethics",
            "clinical_knowledge",
            "college_biology",
            "college_chemistry",
            "college_computer_science",
            "college_mathematics",
            "college_medicine",
            "college_physics",
            "computer_security",
            "conceptual_physics",
            "econometrics",
            "electrical_engineering",
            "elementary_mathematics",
            "formal_logic",
            "global_facts",
            "high_school_biology",
            "high_school_chemistry",
            "high_school_computer_science",
            "high_school_european_history",
            "high_school_geography",
            "high_school_government_and_politics",
            "high_school_macroeconomics",
            "high_school_mathematics",
            "high_school_microeconomics",
            "high_school_physics",
            "high_school_psychology",
            "high_school_statistics",
            "high_school_us_history",
            "high_school_world_history",
            "human_aging",
            "human_sexuality",
            "international_law",
            "jurisprudence",
            "logical_fallacies",
            "machine_learning",
            "management",
            "marketing",
            "medical_genetics",
            "miscellaneous",
            "moral_disputes",
            "moral_scenarios",
            "nutrition",
            "philosophy",
            "prehistory",
            "professional_accounting",
            "professional_law",
            "professional_medicine",
            "professional_psychology",
            "public_relations",
            "security_studies",
            "sociology",
            "us_foreign_policy",
            "virology",
            "world_religions",
        ]
        valid_splits = ["validation", "test", "dev"]

        assert (
            category in valid_categories
        ), f"Invalid category of MMLU dataset. Possible categories are {', '.join(valid_categories)}."
        assert (
            split in valid_splits
        ), f"Invalid split. Possible splits are {', '.join(valid_splits)}."

        # Load datasets
        ds = load_dataset("cais/mmlu", name=category, split=split)

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
        pattern = r"answer:\s*([A-D|a-d])"
        match = re.search(pattern, raw_text.lower())
        if match:
            return {"value": str(match.group(1))}
        else:
            raise ValueError(
                "Could not parse agent output. Make sure it is in the format: `Answer: <A|B|C|D>\\n`"
            )

    @staticmethod
    def question_scorer(
        model_answer: str,
        ground_truth: int,
    ) -> bool:
        return int(ground_truth) == ord(model_answer.upper()) - ord("A")

    @staticmethod
    def formulate_choices_string(choices: list[str]) -> str:
        output_str = "\n"
        for i, choice in enumerate(choices):
            output_str += f"{chr(65 + i)}. {choice}\n"
        return output_str


class MmluMetrics(Metrics):
    """
    Metrics class to record the interactions.
    For single interaction benchmark like Mmlu, the metrics repetition rate and progress rate are not applicable, in non-interactive mode.
    """

    def __init__(self, goal: str, problem: str, choices: str):
        super().__init__(goal)
        self.problem = problem
        self.choices = choices

    def similarity_function(self, action_1: MmluAction, action_2: MmluAction) -> float:
        if action_1.value == action_2.value:
            return 1
        else:
            return 0

    def export(self, **kwargs):
        base_exports = super().export(**kwargs)
        return {"problem": self.problem, "choices": self.choices, **base_exports}


class MmluDriver(Driver):
    """Driver class for Mmlu
    Attributes:
        goal (str): The answer to the question asked.
        problem (str): The question to be answered.
        metrics (MmluMetrics):
        interactive (bool): If True, allows multiple answer inputs.
    """

    def __init__(
        self, problem: str, choices: list[str], goal: str, interactive: bool = False
    ):
        super().__init__(
            str(goal),
            metrics_class=MmluMetrics,
            metrics_args={"problem": str(problem), "choices": list(choices)},
        )
        self.problem = str(problem)
        self.choices = list(choices)
        self.interactive = interactive

    def reset(self) -> MmluObservation:
        super().reset()
        self.current_state = MmluState(value="")
        return MmluObservation(
            output=self.problem
            + MmluUtils.formulate_choices_string(self.choices)
            + "\nSelect the correct choice. Your response must in the following format \nAnswer: <A|B|C|D>\n",
            success=False,
            can_proceed=True,
        )

    def step(self, action: MmluAction) -> MmluObservation:
        super().step(action)
        self.current_state.value = action.value
        if MmluUtils.question_scorer(action.value, self.goal):
            self.metrics.success = True
            return MmluObservation(
                output="Correct answer!!!", success=True, can_proceed=False
            )
        elif self.interactive:
            return MmluObservation(
                output="Wrong answer!!!", success=False, can_proceed=True
            )
        else:
            return MmluObservation(
                output="Wrong answer!!!", success=False, can_proceed=False
            )

    def step_raw(
        self, raw_text: str, custom_parser: Callable | None = None
    ) -> MmluObservation:
        """Process raw text input into Mmlu action and calls the step function.
        Args:
            raw_text (str): Raw input in 'Answer: <answer>\n' format.
            custom_parser (Callable | None): Optional custom parsing function.
        Returns:
            MmluObservation: Game state after processing input.
        """
        try:
            if custom_parser:
                parsed_data = custom_parser(raw_text)
                return self.step(MmluAction(**parsed_data))
            else:
                parsed_data = MmluUtils.parse_agent_output(raw_text)
                return self.step(MmluAction(**parsed_data))
        except (ValueError, ValidationError) as e:
            log_message(
                level="warning",
                message=f"Exception encountered: {str(e)}",
            )
            return MmluObservation(output=str(e), success=False, can_proceed=True)
