# Sudoku Benchmark

Sudoku is a logic-based number puzzle game where players fill a 9x9 grid with digits so that each column, each row, and each of the nine 3x3 subgrids contain all the numbers from 1 to 9. The puzzle starts with some numbers already filled in, and players must deduce the placement of the remaining numbers using logical reasoning.

Reference Wikipedia Page: [Sudoku](https://en.wikipedia.org/wiki/Sudoku)

## AgentQuest Implementation of Sudoku

In AgentQuest's implementation of Sudoku, the input to the game is a number from 1 to 9 in a cell in the 9x9 grid. The cell is identified by row number and column number both ranging from 0 to 8. So, every Sudoku input action is characterized by value, row and column.

There are three categories of Sudoku data in AgentQuest easy, medium and hard. Each consists of 200 initial Sudoku game state.

### Summary Table

| **Category**        | **Field**   | **Type**        | **Description**                                                                                                                                                   |
| ------------------- | ----------- | --------------- | ----------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| **State**           | value       | list[list[str]] | List of lists of numbers in string format representing 9x9 Sudoku board                                                                                           |
| **Action**          | value       | str             | Number (1- 9)                                                                                                                                                     |
|                     | row         | int             | Row index (0-8) where to insert number                                                                                                                            |
|                     | column      | int             | Column index (0-8) where to insert number                                                                                                                         |
| **Observation**     | output      | str             | Feedback to the agent by the benchmark                                                                                                                            |
|                     | success     | bool            | True if Sudoku board is completed correctly, False otherwise                                                                                                      |
|                     | can_proceed | bool            | True if game can still be played, False otherwise                                                                                                                 |
| **Repetition Rate** | -           | float           | Rate quantifying how actions are repeated. Based on Levenshtein ratio of two actions represented in string as concatenation of row_id, column_id and guess digit. |
| **Progress Rate**   | -           | float           | Fraction of cells filled in board divided by total number of cells (81 for 9x9 board)                                                                             |

## Usage

### Running Sudoku with agentquest

```python
from agentquest.lib import cpprint
from agentquest.benchmarks.sudoku import SudokuDriver, SudokuUtils, SudokuAction

game = SudokuUtils.load_data(category="easy")[1]
initial = SudokuUtils.convert_board_to_list_of_lists(game["board"])
goal = SudokuUtils.convert_board_to_list_of_lists(game["answer"])

driver = SudokuDriver(goal, initial)
obs = driver.reset()
cpprint(obs.output)

while not obs.success and obs.can_proceed:
    value = str(input("Enter the value")) # Replace with agent call
    row = int(input("Enter row number:"))
    column = int(input("Enter column number:"))
    obs = driver.step(SudokuAction(value, row, column))
    print(obs.output)
```

Calling the reset() function initializes the Sudoku game and gives the agent instructions about the game. Here is the initial instruction for every Sudoku game instance. The board state is loaded from one of the game data in data.json.
The `step` method call advances the game forward with agent's input (action) and benchmark provides feedback to the action (observation).

```
Welcome to Sudoku.
 Sudoku is a logic-based number puzzle game played on a 9x9 grid, divided
 into nine 3x3 subgrids called "regions."
 The objective is to fill the grid so that each row, each column, and each
 3x3 region contains all digits from 1 to 9 without repetition.
 The puzzle starts with some cells pre-filled with numbers, which serve as
 clues.
 You will be provided the state of the game every time the game progresses.
 Your response should contain what the next number will be and in which row
 and column.
 The rows and columns both range from 0 to 8 zero-based indexing, and the
 value of digits is from 1 to 9.
 The response should be exactly in the following format:
 Row: <row_number>, Column: <column_number>, Value: <value>
 Current game state:
 "[[*, 6, 4, *, *, 3, 8, *, 9], [*, 3, *, 7, *, "
 "9, *, 4, *], [*, 9, 7, 4, 5, *, *, 1, *], [9, "
 "7, *, *, 6, *, *, *, 4], [6, *, 3, *, 1, 4, 9, "
 "8, *], [1, 4, *, 8, 9, *, *, *, 5], [*, *, 6, "
 "5, 3, 1, *, *, 8], [3, *, 5, *, *, 8, 4, 6, "
 "2], [7, *, *, 6, 4, 2, *, 5, 1]]"
```

An LLM agent is expected to produce an output in the format `Row: <row_number>, Column: <column_number>, Value: <value>`. This can either be parsed by the developer manually and step method can be called with `SudokuAction` object. Another option is to call the `step_raw` method which can take the raw agent output in string format.

```python
# dummy_agent_output = "Here is the output. \nRow: 0, Column: 1, Value: 8" # To replace with actual agent output
obs = driver.step_raw(value=dummy_agent_output)
```

The `step_raw` method parses the text with regex searching for `Row: <row_number>, Column: <column_number>, Value: <value>` and calls the step method formulating the SudokuAction object. The developer can pass their own custom parser to `step_raw` method. The developers can also process the initial observation output and send it to their agents as they prefer.

Example of observation output for a valid step method call. It returns the updated board state.

```
[[*, 6, 4, *, *, 3, 8, *, 9],
 [8, 3, *, 7, *, 9, *, 4, *],
 [*, 9, 7, 4, 5, *, *, 1, *],
 [9, 7, *, *, 6, *, *, *, 4],
 [6, *, 3, *, 1, 4, 9, 8, *],
 [1, 4, *, 8, 9, *, *, *, 5],
 [*, *, 6, 5, 3, 1, *, *, 8],
 [3, *, 5, *, *, 8, 4, 6, 2],
 [7, *, *, 6, 4, 2, *, 5, 1]]

```

See `example.ipynb` for the example code to see how to run Sudoku benchmark with AgentQuest.

### Metrics

With AgentQuest, metrics are automatically recorded within the `driver.metrics` object. Once the agent has completed its run for a problem, the metrics can be viewed with method `export()`

```python
driver.metrics.export(repetition_function_kwargs={"theta_a": 1, "num_execution_steps": 50})
```

Here is the metrics output example for an instance of Sudoku game in AgentQuest.

```python
{actions: [{column: 0, row: 1, value: 8},
             {column: 2, row: 0, value: 4}],
 goal: [[5, 6, 4, 1, 2, 3, 8, 7, 9],
          [2, 3, 1, 7, 8, 9, 5, 4, 6],
          [8, 9, 7, 4, 5, 6, 2, 1, 3],
          [9, 7, 8, 3, 6, 5, 1, 2, 4],
          [6, 5, 3, 2, 1, 4, 9, 8, 7],
          [1, 4, 2, 8, 9, 7, 6, 3, 5],
          [4, 2, 6, 5, 3, 1, 7, 9, 8],
          [3, 1, 5, 9, 7, 8, 4, 6, 2],
          [7, 8, 9, 6, 4, 2, 3, 5, 1]],
 observations: [{can_proceed: True,
                   output: "[[*, 6, 4, *, *, 3, 8, *, 9], "
                             "[8, 3, *, 7, *, 9, *, 4, *], "
                             "[*, 9, 7, 4, 5, *, *, 1, *], "
                             "[9, 7, *, *, 6, *, *, *, 4], "
                             "[6, *, 3, *, 1, 4, 9, 8, *], "
                             "[1, 4, *, 8, 9, *, *, *, 5], "
                             "[*, *, 6, 5, 3, 1, *, *, 8], "
                             "[3, *, 5, *, *, 8, 4, 6, 2], "
                             "[7, *, *, 6, 4, 2, *, 5, 1]]",
                   success: False},
                  {can_proceed: True,
                   output: Inadmissible action. There is already a 4 in the
                             provided quadrant.,
                   success: False}],
 progress: [0.5802469135802469, 0.5802469135802469],
 repetition_rate: 0.0,
 states: [{value: [[*, 6, 4, *, *, 3, 8, *, 9],
                       [8, 3, *, 7, *, 9, *, 4, *],
                       [*, 9, 7, 4, 5, *, *, 1, *],
                       [9, 7, *, *, 6, *, *, *, 4],
                       [6, *, 3, *, 1, 4, 9, 8, *],
                       [1, 4, *, 8, 9, *, *, *, 5],
                       [*, *, 6, 5, 3, 1, *, *, 8],
                       [3, *, 5, *, *, 8, 4, 6, 2],
                       [7, *, *, 6, 4, 2, *, 5, 1]]},
            {value: [[*, 6, 4, *, *, 3, 8, *, 9],
                       [8, 3, *, 7, *, 9, *, 4, *],
                       [*, 9, 7, 4, 5, *, *, 1, *],
                       [9, 7, *, *, 6, *, *, *, 4],
                       [6, *, 3, *, 1, 4, 9, 8, *],
                       [1, 4, *, 8, 9, *, *, *, 5],
                       [*, *, 6, 5, 3, 1, *, *, 8],
                       [3, *, 5, *, *, 8, 4, 6, 2],
                       [7, *, *, 6, 4, 2, *, 5, 1]]}],
 success: False}
```

#### Progress Rate for Sudoku

Progress rate signifies how far an agent has reached in solving the goal. For Sudoku, it is how many cells in the board are filled. This is calculated by counting the cells with non-empty values and this is normalized by dividing with total number of cells to get the value between 0 and 1.

#### Repetition Rate for Sudoku

For Sudoku, an action is a combination of cell value to enter, row and column of the cell. To calculate similarity between two actions, we have to take into account these three values. To do this, we create a string of row, column and cell value, and calculate Levenshtein distance between two actions.

The arguments passed as dictionary in export() method are for calculating repetition rates (_theta_a_ threshold and _number of execution steps_) as explained in the repetition rate formula in the [AgentQuest](https://arxiv.org/pdf/2404.06411) paper.
