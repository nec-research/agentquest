# Case Study: Progress Rate in AlfWorld

AlfWorld consists problem tasks in six categories. A player has to navigate through the embodied environment and carry out the assigned task. A progress rate in AlfWorld will naturally be how close an agent is to finishing the task. To quantify this, we show two ways of doing so. This is an example on how developers can build their own metrics and adapt AgentQuest metrics based on their requirement.

## 1. Progress Rate using Oracle Solution

AlfWorld’s text gym environment provides Oracle solution - set of commands to solve the task in least possible steps. This information is provided after every step command and is updated dynamically i.e. if you take any action which is not useful for the provided task, the Oracle solution also takes that into account. We leverage this information, to calculate progress rate.

The idea is we compare the number of commands in the Oracle solution when an agent has just started (initial) to the number of commands in the Oracle solution after certain step (any arbitrary state). This difference can be used to quantify the progress rate.

The following is the progress function in AlfWorldMetrics class. Note that in the function `self.milestones` is the initial Oracle solution when the agent starts and `state.policy_commands` is the Oracle solution after any arbitrary state.

```python
def progress_function(self, state: AlfWorldState) -> float:
    diff = len(self.milestones) - len(state.policy_commands)
    if diff <= 0:
        return 0.0
    else:
        return diff / len(self.milestones)
```

This is the default way of calculating progress rate in Agentquest’s implementation of AlfWorld. Example progress rate output.

```python
'progress': [0.16666666666666666,
  0.3333333333333333,
  0.5,
  0.5,
  0.5,
  0.6666666666666666,
  0.8333333333333334,
  1.0]
```

## 2. Progress Rate using Finite State Machine

The progress rate earlier gives quantitative figure of how close an agent is to completion of the task. However, if a developer wants to understand qualitatively how an agent is doing, earlier method does not work well. Since, AlfWorld does not give visibility to it’s internal states of a task we propose a Finite State Machine to track an agent progress based on a problem type, agent’s action and observation received from AlfWorld.

File [extras.py](extras.py) shows the implementation of the FSM for task category `pick_heat_then_place` . The FSM is created by passing the interactions recorded in the `driver.metrics` object.

```python
# Only works for task category "pick_heat_then_place"
from agentquest.benchmarks.alfworld.extras import get_progress_pick_heat_then_place

qualitative, quantitative = get_progress_pick_heat_then_place(driver.metrics)

print("Actions:", [act.value for act, _, _ in driver.metrics.interactions])
print("Qualitative: ", qualitative)
print("Quantitative: ", quantitative)
```

Example output for problem: `put a hot potato in fridge`

```python
Actions: ['go to fridge 1', 'open fridge 1', 'take potato 2 from fridge 1', 'go to microwave 1', 'heat potato 2 with microwave 1', 'look', 'go to fridge 1', 'go to countertop 1', 'put potato 2 in/on countertop 1', 'take potato 2 from countertop 1', 'go to fridge 1', 'put potato 2 in/on fridge 1']

Qualitative: ['initial', 'initial', 'object picked up', 'object picked up', 'object heated and picked up', 'object heated and picked up', 'object heated and picked up', 'object heated and picked up', 'object heated and not picked up', 'object heated and picked up', 'object heated and picked up', 'object placed correctly']
Quantitative: [0.0, 0.0, 0.25, 0.25, 0.75, 0.75, 0.75, 0.75, 0.5, 0.75, 0.75, 1.0]
```

The qualitiative progress gives indication in which of the state agent is at a particular step. This quantitative progress is just quantizing the four states.

```python
"""
State 0, initial: Object not picked up and not heated. (Start)
State 1, object picked up: Correct object picked up and not heated
State 2, object heated and picked up: Correct object heated and in hand
State 3, object heated and not picked up: Correct object heated and not in hand
State 4, object placed correctly: Hot object placed in correct position. (End)
"""
```