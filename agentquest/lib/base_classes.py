"""The following classes are recommended to be extended for each benchmark as required."""

import copy
import functools
from abc import ABC, abstractmethod
from collections.abc import Callable
from typing import Any, Optional

from pydantic import BaseModel

from agentquest.lib.utils import log_message


class Observation(BaseModel):
    """Base class for an observation returned by the benchmark or environment.
    Attributes:
        output (str): The textual or formatted output representing the current observation.
        success (bool): Indicates whether the last action or step was successful.
        can_proceed (bool): Indicates whether the benchmark or environment can proceed to the next step.
    Notes:
        - Attributes and data types can vary with each benchmarks.
    """

    output: str
    success: bool
    can_proceed: bool


class Action(BaseModel):
    """
    Base class for an action input by the agent to the benchmark or environment.
    Attributes:
        value (str): The action value provided by the agent.
    Notes:
        - Attributes and data types can vary with each benchmarks.
    """

    value: str


class State(BaseModel):
    """
    Base class representing the environment or benchmark state.
    Attributes:
        value (str): The current state of the benchmark or environment.
    Notes:
        - Attributes and data types can vary with each benchmarks.
    """

    value: str


class Metrics(ABC):
    """
    Base class for metrics. This class should be implemented for each benchmark to evaluate agent performance.
    Attributes:
        goal (Optional[Any]): The target goal of the benchmark, used to calculate progress and success.
        success (bool): A flag indicating whether the benchmark's goal has been achieved. Default is `False`.
        interactions (list[tuple[Action, State, Observation]]): A record of all interactions comprising actions, states, and observations.
    """

    def __init__(self, goal: Optional[Any] = None):
        """
        Initializes the Metrics object.
        Args:
            goal (Optional[Any]): The target goal for the benchmark.
        """
        self.goal = goal
        self.success: bool = False
        self.interactions: list[tuple[Action, State, Observation]] = []

    def add_interaction(self, interaction: tuple[Action, State, Observation]):
        """
        Records an interaction consisting of an action, state, and observation.
        Args:
            interaction (tuple[Action, State, Observation]): The agent-environment interaction to record.
        """
        self.interactions.append(copy.deepcopy(interaction))

    def set_success(self, value: bool = True):
        """
        Sets the success flag to indicate whether the benchmark's goal is achieved.
        Args:
            value (bool): A boolean value to set the success flag. Default is `True`.
        Returns:
            bool: The updated success flag.
        """
        self.success = value
        return self.success

    def reset(self):
        """
        Resets the metrics by clearing interactions and setting the success flag to `False`.
        """
        self.success = False
        self.interactions.clear()

    def similarity_function(self, action_1: Action, action_2: Action):
        """
        Calculates similarity between two actions.
        Args:
            action_1 (Action): The first action to compare.
            action_2 (Action): The second action to compare.
        Returns:
            int | float: A similarity score between the two actions.
        Raises:
            NotImplementedError: This method must be implemented in a subclass.
        Notes:
            - This method is called by repetition_function method and it must be implemented in the derived class by benchmark developer, to call the repetition function.
        """
        raise NotImplementedError

    def repetition_function(
        self, theta_a: float, actions: Optional[list[Action]] = None, **kwargs
    ) -> int:
        """
        Counts the number of repeated actions based on a similarity threshold.
        Args:
            theta_a (float): The similarity threshold for determining repetition.
            actions (Optional[list[Action]]): A list of actions to analyze. If `None`, defaults to actions in interactions.
            kwargs: Additional arguments for similarity_function method
        Returns:
            int: The number of repeated actions.
        """
        unique_actions = list()
        if not actions:
            actions = [act for act, _, _ in self.interactions]
        for i, act in enumerate(actions):
            # Check for repetitions
            if all(
                [
                    self.similarity_function(act, actions[x], **kwargs) < theta_a
                    for x in range(i)
                ]
            ):
                unique_actions.append(act)
        return len(actions) - len(unique_actions)

    def get_repetition_rate(self, num_execution_steps: int, **kwargs) -> float:
        """
        Calculates the repetition rate for a list of actions.
        Args:
            num_execution_steps (int): The total number of execution steps in the benchmark.
            kwargs: Additional arguments for the repetition function.
        Returns:
            float: The repetition rate as a ratio of repetitions to total steps.
        """
        num_repetitions = self.repetition_function(**kwargs)
        return num_repetitions / (num_execution_steps - 1)

    def progress_function(self, state: State) -> float | int:
        """Calculates the progress of the current state toward the goal.
        Args:
            state (State): The current state of the benchmark.
        Returns:
            int | float: A progress metric representing the agent's progress.
        Raises:
            NotImplementedError: This method must be implemented in a subclass.
        Notes:
            - This method is called by get_progresses method and it must be implemented in the derived class by benchmark developer, to call the repetition function.
        """
        raise NotImplementedError

    def get_progresses(self, **kwargs) -> list[int | float]:
        """
        Computes a list of progress metrics for the recorded interactions.
        Args:
            kwargs: Additional arguments for the progress function.
        Returns:
            list[int | float]: A list of progress values calculated for each interaction.
        """
        return [
            self.progress_function(state=state, **kwargs)
            for _, state, _ in self.interactions
        ]

    def export(
        self, repetition_function_kwargs: dict = {}, progress_function_kwargs: dict = {}
    ) -> dict:
        """
        Exports metrics data, including goal, success, repetition rate, progress, and recorded interactions.
        Args:
            repetition_function_kwargs (dict): Additional arguments for the repetition function. E.g. {"theta_a": 1, "num_execution_steps": 10}
            progress_function_kwargs (dict): Additional arguments for the progress function.
        Returns:
            dict: A dictionary containing the exported metrics data.
        """
        output_dict = {
            "goal": self.goal,
            "success": self.success,
            "actions": [act.model_dump() for act, _, _ in self.interactions],
            "states": [state.model_dump() for _, state, _ in self.interactions],
            "observations": [obs.model_dump() for _, _, obs in self.interactions],
        }

        try:
            repetition_rate = self.get_repetition_rate(**repetition_function_kwargs)
            output_dict["repetition_rate"] = repetition_rate
        except Exception as e:
            log_message(
                level="warning",
                message=f"Exception encountered: {str(e)}. Unable to calculate repetition rate.",
            )

        try:
            progress = self.get_progresses(**progress_function_kwargs)
            output_dict["progress"] = progress
        except Exception as e:
            log_message(
                level="warning",
                message=f"Exception encountered: {str(e)}. Unable to calculate progress rate.",
            )

        return output_dict


class Driver(ABC):
    """
    The base driver class which should be implemented for each benchmark.
    Attributes:
        goal (Any, optional): Goal of the task. Can be used to calculate milestones, progress,
            and ultimately check if the task is completed. Data type depends on the benchmark.
        metrics (Metrics): Metrics object instantiated through the metrics_class passed in the object instantiation.
        current_state (Any): State of the benchmark/game, to be updated by `reset` and `step` functions.
    """

    def __init__(
        self,
        goal: Optional[Any] = None,
        metrics_class: type[Metrics] = Metrics,
        metrics_args: dict = {},
    ):
        """
        Initializes the Driver class.
        Args:
            goal (Any, optional): The goal of the task, used to measure progress and determine completion.
            metrics_class (type[Metrics]): The metrics class to instantiate and use for tracking progress.
            metrics_args (dict): A dictionary of arguments to initialize the metrics class.
        """
        self.metrics = metrics_class(goal=goal, **metrics_args)
        self.goal = goal
        # To ensure every step makes an add_interaction method call.
        self.step = self.record(self.step)

    def record(self, func: Callable):
        """
        Decorator that records an interaction every time a function is called. Records the action from the argument,
        state from the object's current_state attribute after the wrapped function is called and
        observation from the return value. Intended to be used by `step` method.
        Args:
            func (Callable): The function to be wrapped by the recording decorator.
        Returns:
            Callable: The wrapped function with recording capabilities.
        """

        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            obs = func(*args, **kwargs)
            r_action = next((item for item in args if isinstance(item, Action)), None)
            r_action = kwargs.get("action", r_action)
            self.metrics.add_interaction((r_action, self.current_state, obs))
            return obs

        return wrapper

    @abstractmethod
    def reset(self) -> Observation:
        """
        Resets the driver and metrics to the initial state. The reset method should define the current_state attribute for the driver object.
        Returns:
            Observation: The initial observation to feed into the agent.
        """
        self.metrics.reset()
        pass

    @abstractmethod
    def step(self, action: Action) -> Observation:
        """
        Args:
            action (Action): The action to be applied in the current state.
        Returns:
            Observation: The observation resulting from the applied action.
        Raises:
            Exception: If the `current_state` attribute is not defined or if no action is provided.
        """
        if not hasattr(self, "current_state"):
            raise Exception("State is not defined. Run the reset method first.")
        if not action:
            raise Exception("Cannot run step method without an action.")
        pass
