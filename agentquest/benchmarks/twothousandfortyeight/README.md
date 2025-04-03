# 2048 Benchmark

2048 is a number puzzle game where players slide tiles on a grid to combine them and reach the 2048 tile. Each move merges tiles with the same number, doubling their value, while new tiles appear to keep the challenge alive. The game requires strategic planning and foresight to prevent the grid from filling up completely. Created by Gabriele Cirulli, 2048 is praised for its simplicity, and mental challenge.

Reference Wikipedia Page: [2048](<https://en.wikipedia.org/wiki/2048_(video_game)>)

## AgentQuest Implementation of 2048

In AgentQuest's implementation of 2048, the goal is to reach 2048 number, and it works exactly as original 2048 providing a text interface for an agent to interact with the game. The inputs "w", "a", "s" and "d" to mimic actions of up, left, bottom and right arrows respectively in a 2048 game.

### Summary Table

| **Category**        | **Field**   | **Type**        | **Description**                                                                               |
| ------------------- | ----------- | --------------- | --------------------------------------------------------------------------------------------- |
| **State**           | value       | list[list[int]] | List of lists of integers representing 4x4 2048 board                                         |
| **Action**          | value       | str             | Action in 2048: 'w','a','s' or 'd' representing up, down, left and right arrows.              |
| **Observation**     | output      | str             | Feedback to the agent by the benchmark                                                        |
|                     | success     | bool            | True if highest number in the board is 2048, False otherwise                                  |
|                     | can_proceed | bool            | True if game can still be played, False otherwise                                             |
| **Repetition Rate** | -           | float           | Rate to quantify the repetitions of actions. Based on simple '==' check on the action values. |
| **Progress Rate**   | -           | float           | Fraction of logarithm of maximum value in the board to the logarithm of goal value (2048)     |

## Usage

### Running 2048 with Agentquest

```python
from agentquest.benchmarks.twothousandfortyeight import TTFEDriver, TTFEAction
driver = TTFEDriver(goal=2048)
obs = driver.reset()
print(obs.output)

while not obs.success and obs.can_proceed:
    human_input = input() # Replace with agent call
    obs = driver.step(TTFEAction(value=human_input))
    print(obs.output)

```

Calling the `reset()` function initializes the 2048 game and gives the agent instructions about the game. Here is the initial instruction for every 2048 game instance. The board state will be random with two blocks of '2' and '4'. The `step` method call advances the game forward with agent's input (action) and benchmark provides feedback to the action (observation).

```
Welcome to 2048!
Use 'w', 'a', 's', 'd' to move the tiles, where each move respectively moves all blocks that can move in the given direction: 'up', 'left', 'down', 'right'.
Your goal is to make the 2048 block, you work towards this by merging tiles of the same value with your movement keys.
The merged block will be the sum of the previous values of the blocks. You lose when no valid moves are possible.
Initially, two blocks appear, after each move following that a block will spawn. There is a 90 percent chance for it to be a '2' and a 10 percent chance for it to be a '4'.
You will receive feedback after you make a move: verbally and with a matrix. Base your moves on the feedback provided.
Your response should be strictly in the following format:
Move: <w|a|s|d>
╔══════╦══════╦══════╦══════╗
║      ║      ║      ║      ║
╠══════╬══════╬══════╬══════╣
║      ║      ║      ║      ║
╠══════╬══════╬══════╬══════╣
║      ║      ║      ║  2   ║
╠══════╬══════╬══════╬══════╣
║      ║  4   ║      ║      ║
╚══════╩══════╩══════╩══════╝
```

An LLM agent is expected to produce an output in the format `Move: <w|a|s|d>`. This can either be parsed by the developer manually and step method can be called with `TTFEAction` object. Another option is to call the step_raw method which can take the raw agent output in string format.

```python
# dummy_agent_output = "Move: w" # To replace with actual agent output
obs = driver.step_raw(value=dummy_agent_output)
```

The step_raw method calls a parser with regex that parses the agent's output searching for `Move: <letter>`. The developer can pass their own custom parser to step_raw method. Also, the developers are free to process the initial observation output and send it to their agents as they prefer.

Observation output for a step method call. The letter input here is `w`.

```
Valid move, enter your next move:

╔══════╦══════╦══════╦══════╗
║      ║  4   ║      ║  2   ║
╠══════╬══════╬══════╬══════╣
║      ║      ║      ║      ║
╠══════╬══════╬══════╬══════╣
║      ║      ║      ║      ║
╠══════╬══════╬══════╬══════╣
║      ║      ║      ║  2   ║
╚══════╩══════╩══════╩══════╝
```

See `example.ipynb` for the example code to see how to run 2048 benchmark with AgentQuest.

### Metrics

With AgentQuest, metrics are automatically recorded within the `driver.metrics` object. Once the agent has completed its run for a problem, the metrics can be viewed with method `export()`

```python
driver.metrics.export(repetition_function_kwargs={"theta_a": 1, "num_execution_steps": 50})
```

Here is the metrics output example for an instance of 2048 game in AgentQuest.

```python
{'goal': 2048,
 'success': False,
 'actions': [{'value': 'w'}, {'value': 'a'}],
 'states': [{'value': [[0, 0, 2, 2],
    [0, 0, 0, 0],
    [0, 0, 0, 0],
    [2, 0, 0, 0]]},
  {'value': [[4, 0, 0, 0], [0, 0, 0, 0], [0, 0, 0, 0], [2, 2, 0, 0]]}],
 'observations': [{'output': 'Valid move, enter your next move:\n\n╔══════╦══════╦══════╦══════╗\n║      ║      ║  2   ║  2   ║\n╠══════╬══════╬══════╬══════╣\n║      ║      ║      ║      ║\n╠══════╬══════╬══════╬══════╣\n║      ║      ║      ║      ║\n╠══════╬══════╬══════╬══════╣\n║  2   ║      ║      ║      ║\n╚══════╩══════╩══════╩══════╝\n',
   'success': False,
   'can_proceed': True},
  {'output': 'Valid move, enter your next move:\n\n╔══════╦══════╦══════╦══════╗\n║  4   ║      ║      ║      ║\n╠══════╬══════╬══════╬══════╣\n║      ║      ║      ║      ║\n╠══════╬══════╬══════╬══════╣\n║      ║      ║      ║      ║\n╠══════╬══════╬══════╬══════╣\n║  2   ║  2   ║      ║      ║\n╚══════╩══════╩══════╩══════╝\n',
   'success': False,
   'can_proceed': True}],
 'repetition_rate': 0.0,
 'progress': [0.09, 0.18]}
```

#### Progress Rate for 2048

Progress rate signifies how far an agent has reached in solving the goal. For 2048, it is how close the highest number in the board is to number 2048. This is measured by dividing log base 2 of the highest number by log base 2 of 2048. This measurement of progress brings the logarithmic scale to linear scale and progress rate can be measured from 0 to 1 scale.

#### Repetition Rate for 2048

For 2048, there are only four possible action inputs. These are the characters 'w', 'a', 's' and 'd'. Hence, to calculate repetition rate, we count how many times the inputs are repeated to solve a game of 2048.

The arguments passed as dictionary in export() method are for calculating repetition rates (_theta_a_ threshold and _number of execution steps_) as explained in the repetition rate formula in the [AgentQuest](https://arxiv.org/pdf/2404.06411) paper.
