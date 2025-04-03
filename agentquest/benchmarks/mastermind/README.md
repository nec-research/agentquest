# Mastermind Benchmark

Mastermind is a number game adaptation of Mastermind [board game](<https://en.wikipedia.org/wiki/Mastermind_(board_game)>). A player has to guess the target number of certain length of digits. On every guess, the player is provided feedback if the guess number was correct, how many digits were guessed correct and how many of them are in correct/incorrect position.

## AgentQuest Implementation of Mastermind

AgentQuest provides options for playing Mastermind game with 4,5,6,7,8 digit numbers.

### Summary Table

| **Category**        | **Field**   | **Type** | **Description**                                                                                        |
| ------------------- | ----------- | -------- | ------------------------------------------------------------------------------------------------------ |
| **State**           | value       | str      | Last guess input to the benchmark                                                                      |
| **Action**          | value       | str      | Guess number                                                                                           |
| **Observation**     | output      | str      | Feedback to the agent by the benchmark                                                                 |
|                     | success     | bool     | True if target number is guessed correctly, False otherwise                                            |
|                     | can_proceed | bool     | True if further guesses can be made, False otherwise                                                   |
| **Repetition Rate** | -           | float    | Metric on how guessed numbers (actions) are repeated. Based on Levenshtein ratio of two guess numbers. |
| **Progress Rate**   | -           | float    | Number of digits guessed correctly in correct position divided by number of digits of goal number.     |

## Usage

### Running Mastermind with agentquest

```python
from agentquest.benchmarks.mastermind import (MasterMindDriver, MasterMindUtils, MasterMindAction)
goal = MasterMindUtils.load_data(category="4 digits")[0]

driver = MasterMindDriver(goal=goal)
obs = driver.reset()
print(obs.output)

while not obs.success and obs.can_proceed:
    human_input = input() # Replace with agent call
    obs = driver.step(MasterMindAction(value=human_input))
    print(obs.output)
```

Calling the `reset()` method initializes the Mastermind game and gives the agent instructions about the game. Here is the initial instruction for a Mastermind game instance.

```
You are tasked to play the Mastermind game.
The host chooses a number and gives you the amount of digits. You have to guess the correct number as fast as you can.
The number can contain repetitions and any possible digit between: 0, 1, 2, 3, 4, 5, 6, 7, 8, 9.
At each round, you provide a number as a guess. At each step, the host provides you this information:
1. The number of correct digits in the wrong position.
2. The number of correct digits in the correct position.
The game ends when the host outputs 'You Won!'
Carefully choose your strategy. Avoid brute force.
The guess must be in the following format:
Guess: <number>
Start guessing the 4 digits number.
```

While, the example code above shows human input, an LLM agent is expected to produce an output in the format `Guess: <number>` according to the instruction. This can be parsed by the developer manually and `step` method can be called with `MasterMindAction` object. Another option is to call the `step_raw` method which can take the raw agent output in string format, parse it and call `step` method out of the box.

The `step` method call advances the game forward with agent's input (action) and benchmark provides feedback to the action (observation).

```python
# dummy_agent_output = "Number: 5148" # To replace with actual agent output
obs = driver.step_raw(value=dummy_agent_output)
```

The step_raw method calls a parser with regex that parses the agent's output searching for `Guess: <number>`. The developer can pass their own custom parser to step_raw method. Also, the developers are free to process the initial observation output and send it to their agents as they prefer.

Observation output for a `step` method call with input action value `'5297'`

```
'Wrong! Your guess has 1 correct digit in the correct position and 1 correct digit in the wrong position. Keep guessing.'
```

See `example.ipynb` for the example code to see how to run Mastermind benchmark with AgentQuest.

### Metrics

With AgentQuest, metrics are automatically recorded within the `driver.metrics` object. Once the agent has completed its run for a problem, the metrics can be viewed with method `export()`

```python
driver.metrics.export(repetition_function_kwargs={"theta_a": 1, "num_execution_steps": 10})
```

Metrics output example for an instance of Mastermind game in AgentQuest:

```python
{'goal': '5918',
 'success': True,
 'actions': [{'value': '5297'}, {'value': '5198'}, {'value': '5918'}],
 'states': [{'value': '5297'}, {'value': '5198'}, {'value': '5918'}],
 'observations': [{'output': 'Wrong! Your guess has 1 correct digit in the correct position and 1 correct digit in the wrong position. Keep guessing.',
   'success': False,
   'can_proceed': True},
  {'output': 'Wrong! Your guess has 2 correct digits in the correct positions and 2 correct digits in the wrong positions. Keep guessing.',
   'success': False,
   'can_proceed': True},
  {'output': 'You Won!', 'success': True, 'can_proceed': False}],
 'repetition_rate': 0.0,
 'progress': [0.25, 0.5, 1.0]}
```

#### Progress Rate for Mastermind

Progress rate signifies how far an agent has reached in solving the goal. For Mastermind, it is the number of correctly guessed digits in correct places. Then this count is divided by total number of digits in the goal number to obtain the progress rate.

#### Repetition Rate for Mastermind

Repetition rate quantifies how actions are repeated in solving a task. To calculate repetition rate for Mastermind, similarity scores is calculated between two Mastermind actions using Levenshtein distance. Then, the repetition rate is calculated based on this similarity score as explained in the [AgentQuest](https://arxiv.org/pdf/2404.06411) paper.

The arguments passed as dictionary in export() method are for calculating repetition rates (_theta_a_ threshold and _number of execution steps_).
