from typing import Any

from agentquest.lib import Action, Driver, Metrics, Observation, State


class __Benchmark__Action(Action):
    pass


class __Benchmark__Observation(Observation):
    pass


class __Benchmark__State(State):
    pass


class __Benchmark__Metrics(Metrics):
    def __init__(self, goal: Any | None = None):
        super().__init__(goal)

    def similarity_function(
        self, action_1: __Benchmark__Action, action_2: __Benchmark__Action
    ):
        # TODO: Similarity function logic here
        pass

    def progress_function(self, state: __Benchmark__State) -> float | int:
        # TODO: Progress function logic here
        pass


class __Benchmark__Driver(Driver):
    def __init__(
        self,
        goal: Any | None = None,
    ):
        super().__init__(goal, metrics_class=__Benchmark__Metrics, metrics_args={})

    def reset(self) -> __Benchmark__Observation:
        super().reset()
        # TODO: Write RESET logic here.
        pass

    def step(self, action: __Benchmark__Action) -> __Benchmark__Observation:
        super().step(action)
        # TODO: Write STEP logic here
        pass
