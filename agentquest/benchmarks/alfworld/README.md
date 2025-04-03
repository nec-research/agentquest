# ALFWorld

ALFWorld: Aligning Text and Embodied Environments for Interactive Learning (Shridhar et al.)

Link to ALFWorld Paper: https://arxiv.org/pdf/2010.03768

Link to ALFWorld Website: https://alfworld.github.io/

**Description (copied from ALFWorld Website)**: ALFWorld contains interactive TextWorld environments (Côté et. al) that parallel embodied worlds in the ALFRED dataset (Shridhar et. al). The aligned environments allow agents to reason and learn high-level policies in an abstract space before solving embodied tasks through low-level actuation.

### About ALFWorld Dataset

ALFWorld consists of tasks among six categories. The categories are `pick_and_place`, `look_at_obj_in_light`, `pick_clean_then_place`, `pick_heat_then_place`, `pick_cool_then_place` and `pick_two_obj_and_place`. There are four splits: train, valid_seen, valid_unseen and valid_train.

## ALFWorld in AgentQuest

AgentQuest wraps the text interface of ALFWorld and provides an easy method to benchmark your agent with ALFWorld. ALFWorld [version 0.3.5](https://github.com/alfworld/alfworld/tree/0.3.5) is used in this version of AgentQuest installed via pip. The data is stored by default in the `~/.cache/alfworld/json_2.1.1` directory.

Splits: Considering all categories, there are 5386 tasks in train, 217 tasks in valid_seen, 222 tasks in valid_unseen and 200 tasks in valid_train.

In the ALFWorld paper, Table 1 shows there are 3827 tasks in the ALFRED dataset. The amount of tasks in the data directory of alfworld is more than the figures in the paper. This is because [not all games might load](https://github.com/alfworld/alfworld/tree/master/scripts), if either the game is unsolvable or the PDDL problem is ill-defined (Also look at this [issue](https://github.com/alfworld/alfworld/issues/89)).
Note that we do not consider movable receptor tasks in our evaluation set.

Developers can use the entire ALFWorld data to evaluate their agents or randomly select a subset of of ALFWorld benchmark.

### Summary Table

| **Category**        | **Field**   | **Type** | **Description**                                                                                                            |
| ------------------- | ----------- | -------- | -------------------------------------------------------------------------------------------------------------------------- |
| **State**           | value       | str      | Last valid action value. If the last action was reset it is an empty string.                                               |
| **Action**          | value       | str      | Agent action to Alfworld environment to move forward the game or carry out the task.                                       |
| **Observation**     | output      | str      | Feedback to the agent by Alfworld's environment. Includes a list of available actions.                                     |
|                     | success     | bool     | True if task has been completed successfully.                                                                              |
|                     | can_proceed | bool     | True if game can still be played, False otherwise. In Alfworld, it is always opposite to success.                          |
| **Repetition Rate** | -           | float    | Rate to quantify the repetitions of actions. Based on levenshtein ratio between action values.                             |
| **Progress Rate**   | -           | float    | A count of how many actions are completed in order, that are in the Oracle solution (ground truth solution) for a problem. |

### Installation

We recommend using poetry to avoid dependency conflicts. Add the following list of dependencies for alfworld in your `pyproject.toml` file. These dependencies can also be installed separately with `pip`.

```yaml
[tool.poetry.group.alfworld.dependencies]
alfworld = "^0.3.5"
h5py = "^3.12.1"
pycocotools = "^2.0.8"
transformers = "^4.46.2"
visdom = "^0.2.4"
gym = "^0.26.2"
```

```bash
poetry add agentquest
poetry install --with alfworld
alfworld-download
```

This should install Alfworld in your virtual environment and download Alfworld data in `~/.cache/alfworld` directory. This path can be accessed by default through `ALFWORLD_DATA` variable available in `alfworld.info` module. This is the default directory that is expected to contain ALFWORLD data. This version of Agentquest is tested with Alfworld version 0.3.5.

### Usage

```python
# Check example.ipynb for complete code

from agentquest.benchmarks.alfworld import AlfWorldDriver, AlfWorldUtils, AlfWorldAction

data = AlfWorldUtils.load_data(category="all", source="valid_unseen")

driver = AlfWorldDriver(problem=data[0])
obs = driver.reset()
print(obs.output)

while not obs.success and obs.can_proceed:
    human_input = input()
    obs = driver.step(AlfWorldAction(value=human_input))
    # obs = driver.step_raw(human_input)
    print(obs.output)
```

Calling the `reset()` method initializes an instance of ALFWorld problem in the gym environment, and provides the description about the problem and possible set of admissible commands.

```
-= Welcome to TextWorld, ALFRED! =-

You are in the middle of a room. Looking quickly around you, you see a cabinet 15, a cabinet 14, a cabinet 13, a cabinet 12, a cabinet 11, a cabinet 10, a cabinet 9, a cabinet 8, a cabinet 7, a cabinet 6, a cabinet 5, a cabinet 4, a cabinet 3, a cabinet 2, a cabinet 1, a coffeemachine 1, a countertop 4, a countertop 3, a countertop 2, a countertop 1, a drawer 4, a drawer 3, a drawer 2, a drawer 1, a fridge 1, a garbagecan 1, a microwave 1, a sinkbasin 1, a stoveburner 4, a stoveburner 3, a stoveburner 2, a stoveburner 1, and a toaster 1.

Your task is to: cool some tomato and put it in garbagecan.
Admissible commands:
['go to cabinet 1', 'go to cabinet 10', 'go to cabinet 11', 'go to cabinet 12', 'go to cabinet 13', 'go to cabinet 14', 'go to cabinet 15', 'go to cabinet 2', 'go to cabinet 3', 'go to cabinet 4', 'go to cabinet 5', 'go to cabinet 6', 'go to cabinet 7', 'go to cabinet 8', 'go to cabinet 9', 'go to coffeemachine 1', 'go to countertop 1', 'go to countertop 2', 'go to countertop 3', 'go to countertop 4', 'go to drawer 1', 'go to drawer 2', 'go to drawer 3', 'go to drawer 4', 'go to fridge 1', 'go to garbagecan 1', 'go to microwave 1', 'go to sinkbasin 1', 'go to stoveburner 1', 'go to stoveburner 2', 'go to stoveburner 3', 'go to stoveburner 4', 'go to toaster 1', 'inventory', 'look']
Your response should be in format: 'Action: <action_command>'
```

The `step()` method call, progresses the game one step further with a command. The AlfWorld environment provides a feedback for a command. An example of a `step()` method's observation for command `"go to garbagecan 1"` is as follows:

```
You arrive at loc 34. On the garbagecan 1, you see a tomato 1.
Admissible commands:
['examine garbagecan 1', 'go to cabinet 1', 'go to cabinet 10', 'go to cabinet 11', 'go to cabinet 12', 'go to cabinet 13', 'go to cabinet 14', 'go to cabinet 15', 'go to cabinet 2', 'go to cabinet 3', 'go to cabinet 4', 'go to cabinet 5', 'go to cabinet 6', 'go to cabinet 7', 'go to cabinet 8', 'go to cabinet 9', 'go to coffeemachine 1', 'go to countertop 1', 'go to countertop 2', 'go to countertop 3', 'go to countertop 4', 'go to drawer 1', 'go to drawer 2', 'go to drawer 3', 'go to drawer 4', 'go to fridge 1', 'go to microwave 1', 'go to sinkbasin 1', 'go to stoveburner 1', 'go to stoveburner 2', 'go to stoveburner 3', 'go to stoveburner 4', 'go to toaster 1', 'inventory', 'look', 'take tomato 1 from garbagecan 1']
Your response should be in format: 'Action: <action_command>
```

AgentQuest adds the response format at the end of the problem, so that the agent's output can be easily parsed using `step_raw` method. Developers are free to cut this part out or even send a custom parser to `step_raw` method.

```python
# dummy_agent_output = "Here is the action. Action: go to cabinet 1" # To replace with actual agent output
obs = driver.step_raw(value=dummy_agent_output)
```

### Metrics

With AgentQuest, metrics are automatically recorded in the `driver.metrics` object. Once the agent has completed its run for a problem, the metrics can be viewed with method `export()`

```python
driver.metrics.export(repetition_function_kwargs={"theta_a": 1, "num_execution_steps": 10})
```

Metrics output example for an instance of Alfworld game in AgentQuest. The following game was manually interrupted after 3 rounds to keep the output small.

```python
{'goal': 'cool some tomato and put it in garbagecan',
 'success': False,
 'actions': [{'value': 'go to garbagecan 1'},
  {'value': 'take tomato 1 from garbagecan 1'},
  {'value': 'go to fridge 3'}],
 'states': [{'value': 'go to garbagecan 1'},
  {'value': 'take tomato 1 from garbagecan 1'},
  {'value': 'take tomato 1 from garbagecan 1'}],
 'observations': [{'output': "You arrive at loc 34. On the garbagecan 1, you see a tomato 1.\nAdmissible commands:\n['examine garbagecan 1', 'go to cabinet 1', 'go to cabinet 10', 'go to cabinet 11', 'go to cabinet 12', 'go to cabinet 13', 'go to cabinet 14', 'go to cabinet 15', 'go to cabinet 2', 'go to cabinet 3', 'go to cabinet 4', 'go to cabinet 5', 'go to cabinet 6', 'go to cabinet 7', 'go to cabinet 8', 'go to cabinet 9', 'go to coffeemachine 1', 'go to countertop 1', 'go to countertop 2', 'go to countertop 3', 'go to countertop 4', 'go to drawer 1', 'go to drawer 2', 'go to drawer 3', 'go to drawer 4', 'go to fridge 1', 'go to microwave 1', 'go to sinkbasin 1', 'go to stoveburner 1', 'go to stoveburner 2', 'go to stoveburner 3', 'go to stoveburner 4', 'go to toaster 1', 'inventory', 'look', 'take tomato 1 from garbagecan 1']\nYour response should be in format: 'Action: <action_command>'",
   'success': False,
   'can_proceed': True},
  {'output': "You pick up the tomato 1 from the garbagecan 1.\nAdmissible commands:\n['examine garbagecan 1', 'examine tomato 1', 'go to cabinet 1', 'go to cabinet 10', 'go to cabinet 11', 'go to cabinet 12', 'go to cabinet 13', 'go to cabinet 14', 'go to cabinet 15', 'go to cabinet 2', 'go to cabinet 3', 'go to cabinet 4', 'go to cabinet 5', 'go to cabinet 6', 'go to cabinet 7', 'go to cabinet 8', 'go to cabinet 9', 'go to coffeemachine 1', 'go to countertop 1', 'go to countertop 2', 'go to countertop 3', 'go to countertop 4', 'go to drawer 1', 'go to drawer 2', 'go to drawer 3', 'go to drawer 4', 'go to fridge 1', 'go to microwave 1', 'go to sinkbasin 1', 'go to stoveburner 1', 'go to stoveburner 2', 'go to stoveburner 3', 'go to stoveburner 4', 'go to toaster 1', 'inventory', 'look', 'put tomato 1 in/on garbagecan 1']\nYour response should be in format: 'Action: <action_command>'",
   'success': False,
   'can_proceed': True},
  {'output': "Nothing happens.\nAdmissible commands:\n['examine garbagecan 1', 'examine tomato 1', 'go to cabinet 1', 'go to cabinet 10', 'go to cabinet 11', 'go to cabinet 12', 'go to cabinet 13', 'go to cabinet 14', 'go to cabinet 15', 'go to cabinet 2', 'go to cabinet 3', 'go to cabinet 4', 'go to cabinet 5', 'go to cabinet 6', 'go to cabinet 7', 'go to cabinet 8', 'go to cabinet 9', 'go to coffeemachine 1', 'go to countertop 1', 'go to countertop 2', 'go to countertop 3', 'go to countertop 4', 'go to drawer 1', 'go to drawer 2', 'go to drawer 3', 'go to drawer 4', 'go to fridge 1', 'go to microwave 1', 'go to sinkbasin 1', 'go to stoveburner 1', 'go to stoveburner 2', 'go to stoveburner 3', 'go to stoveburner 4', 'go to toaster 1', 'inventory', 'look', 'put tomato 1 in/on garbagecan 1']\nYour response should be in format: 'Action: <action_command>'",
   'success': False,
   'can_proceed': True}],
 'repetition_rate': 0.0,
 'progress': 0.16666666666666666,
 'milestones': ['go to garbagecan 1',
  'take tomato 1 from garbagecan 1',
  'go to fridge 1',
  'cool tomato 1 with fridge 1',
  'go to garbagecan 1',
  'put tomato 1 in/on garbagecan 1'],
 'problem': '/home/bgautam/.cache/alfworld/json_2.1.1/valid_seen/pick_cool_then_place_in_recep-Tomato-None-GarbageCan-6/trial_T20190909_082934_483899'}

```

#### Progress Rate for AlfWorld

Progress rate signifies how far an agent has reached in solving the goal. ALFWorld's environment provides set of Oracle solution commands to complete a task at every state of the game. We use this to calculate progress of an agent at a particular ALFWorld game state by comparing how many more steps are needed to complete the task. At a step k, it's progress would be defined as `(number of commands to solve the task at reset - number of commands to solve the task after state k)/number of commands to solve the task at reset`.

Here is the progress_function method for ALFWorldMetrics for this. Remember `self.milestones` is Oracle solution at the beginning of the game and `state.policy_commands` is Oracle solution at a particular state.

```python
def progress_function(self, state: AlfWorldState) -> float:
    diff = len(self.milestones) - len(state.policy_commands)
    if diff <= 0:
        return 0.0
    else:
        return diff / len(self.milestones)
```

We also propose a different way to show qualitative progress in ALFWorld. This is discussed in detail in the **Case Study: Progress Rate in AlfWorld** [document](case_study.md).

#### Repetition Rate for AlfWorld

For AlfWorld, the commands are the action inputs. To calculate repetition rate, we count how many times a command has been repeated, using Levenshtein distance.

The arguments passed as dictionary in `export()` method are for calculating repetition rates (_theta_a_ threshold and _number of execution steps_) as explained in the repetition rate formula in the [AgentQuest](https://arxiv.org/pdf/2404.06411) paper.
