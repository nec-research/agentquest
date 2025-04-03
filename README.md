# README

> ⚠️ The previous version of AgentQuest is available in the [v1](https://github.com/nec-research/agentquest/tree/v1) branch.

AgentQuest is a leading benchmarking framework enabling developers to evaluate LLMs and LLM agents effortlessly across multiple industry benchmarks with just a few lines of code. It supports [various benchmarks](#supported-benchmarks) out of the box, testing a range of capabilities of LLM-based systems. Additionally, it provides base classes that can be extended to quickly add new benchmarks and evaluation metrics.

This repository contains the code for the demo paper:

**AgentQuest: A Modular Benchmark Framework to Measure Progress and Improve LLM Agents**

- Paper: [https://aclanthology.org/2024.naacl-demo.19.pdf](https://aclanthology.org/2024.naacl-demo.19.pdf)
- Video: [https://youtu.be/0JNkIfwnoak](https://youtu.be/0JNkIfwnoak)

If you use `AgentQuest` for your research, please cite the following paper:

```
@inproceedings{gioacchini2024agentquest,
  title={AgentQuest: A Modular Benchmark Framework to Measure Progress and Improve LLM Agents},
  author={Gioacchini, Luca and Siracusano, Giuseppe and Sanvito, Davide and Gashteovski, Kiril and Friede, David and Bifulco, Roberto and Lawrence, Carolin},
  booktitle = "Proceedings of the 2024 Conference of the North American Chapter of the Association for Computational Linguistics: Human Language Technologies (Volume 3: System Demonstrations)",
  month = jun,
  year = "2024",
  publisher = "Association for Computational Linguistics",
  pages = "185--193"
}
```

If you are interested in accessing the AgentQuest GUI presented at the NAACL 2024 Demo Session, please contact us.

## Table of Contents

- [Structure of This Repo](#structure-of-this-repo)
- [Supported Benchmarks](#supported-benchmarks)
- [Installation](#installation)
- [How to benchmark your agent with AgentQuest - Sudoku Example](#how-to-benchmark-your-agent-with-agentquest---sudoku-example)
- [AgentQuest Concepts](#agentquest-concepts)
- [How to write a custom benchmark?](#how-to-write-a-custom-benchmark)
- [How to Use an LLM Agent?](#how-to-use-an-llm-agent)

## Structure of This Repo

This repo is organized as follows:

- `agentquest/lib`. Contains base classes and utility functions inherited and used by all benchmarks.
- `agentquest/benchmarks`. Includes documentation (README files), installation scripts, and code for each supported benchmark.
- `agentquest/tutorial`. Tutorial for developers to develop a custom benchmark in Agentquest.
- `agents`. Contains examples on how to implement LLM agents through different frameworks testing one benchmark.

## Supported Benchmarks

AgentQuest supports following benchmarks out of the box.

|                                                                |                         Evaluation of Type                         | Categories |
| -------------------------------------------------------------- | :----------------------------------------------------------------: | :--------: |
| [MasterMind](/agentquest/benchmarks/mastermind/README.md)      |                        Deductive Reasoning                         |     5      |
| [Hangman](/agentquest/benchmarks/hangman/README.md)            |                        Deductive Reasoning                         |     4      |
| [Wordle](/agentquest/benchmarks/wordle/README.md)              |                        Deductive Reasoning                         |     1      |
| [Sudoku](/agentquest/benchmarks/sudoku/README.md)              |                         Spatial Reasoning                          |     3      |
| [2048](/agentquest/benchmarks/twothousandfortyeigth/README.md) |                         Spatial Reasoning                          |     -      |
| [AlfWorld](/agentquest/benchmarks/alfworld/README.md)          |                         Embodied Reasoning                         |     6      |
| [WebShop](/agentquest/benchmarks/webshop/README.md)            |                         Embodied Reasoning                         |     -      |
| [GAIA](/agentquest/benchmarks/gaia/README.md)                  | Tool Use, Advanced Reasoning, Multi-modality understanding, Coding |     3      |
| [MMLU](/agentquest/benchmarks/mmlu/README.md)                  |               Knowledge and Problem Solving ABility                |     58     |
| [GSM8k](/agentquest/benchmarks/gsm8k/README.md)                |          Mathematical problems with multi-step reasoning           |     2      |
| [Cipher](/agentquest/benchmarks/cipher/README.md) |          Deciphering, puzzle solving           |     6      |

## Installation

Clone the repo and use poetry to install `agentquest`.

```bash
pip install agentquest
```

This installation is sufficient for 7 out of 10 benchmarks supported out-of-the-box by AgentQuest.

#### Benchmarks with extra installation steps

- For `GAIA` benchmark: Since the dataset is multimodal, the dataset has to be downloaded from huggingface repo. Follow the instructions [here](agentquest/benchmarks/gaia/README.md#installation).
- For `Alfworld` benchmark: Python package `alfworld` needs to be installed with other supporting packages. Follow the custom installation instructions for alfworld as specified here [here](agentquest/benchmarks/alfworld/README.md#installation).
- For `Webshop` benchmark: A separate virtual environment is recommended than the one where AgentQuest is running. Follow the custom installation instructions specified [here](agentquest/benchmarks/webshop/README.md#installation).

## How to benchmark your agent with AgentQuest - Sudoku Example

Here’s a brief example of how to benchmark an agent using the Sudoku benchmark.

Import the required benchmark specific classes.

```python
from agentquest.lib import cpprint
from agentquest.benchmarks.sudoku import SudokuDriver, SudokuUtils, SudokuAction
```

`cpprint` is a utility function to nicely print the Sudoku board. `SudokuDriver` is the main driver class which allows running the Sudoku game, maintains game state and provides feedback to the agent. `SudokuUtils` consists of utility functions like loading a Sudoku game, parsing agent's outputs and other benchmark specific utility functions. `SudokuAction` is the action class which the benchmark takes as input for any step method call as we will see further.

First we load the data of one Sudoku game and prepare the data format. Then, we instantiate a SudokuDriver object.

```python
game = SudokuUtils.load_data(category="easy")[1]
initial = SudokuUtils.convert_board_to_list_of_lists(game["board"])
goal = SudokuUtils.convert_board_to_list_of_lists(game["answer"])

driver = SudokuDriver(goal, initial)
obs = driver.reset()
cpprint(obs.output)
```

The `reset` method initiates the game environment for Sudoku benchmark, and has similar behavior for other benchmarks as well. It also sets the `current_state` attribute for the driver object.

```python
while not obs.success and obs.can_proceed:
    value = str(input("Enter the value")) # Replace with agent call
    row = int(input("Enter row number:"))
    column = int(input("Enter column number:"))
    obs = driver.step(SudokuAction(value, row, column))
    cpprint(obs.output)
```

Here, value, row and column information is taken from human input. The `step` method runs the game one step further and checks if the value supplied to that row and column is legitimate or not. Based on that, it provides feedback to the agent.

The human input can be replaced with output from agent call as follows:

```python
while not obs.success and obs.can_proceed:
    agent_output = agent.invoke(obs.output) #obs.output consists of string information for an agent
    obs = driver.step_raw(agent_output)
    cpprint(obs.output)
```

The `step_raw` method is a wrapper to `step` method, which parses the agent's string input to the benchmark and extract value, row and column information. Then it forms `SudokuAction` object and calls `step` method from inside. For Sudoku, developers might want to cap the number of steps allowed for an agent to complete a board to prevent large number of agent invokes.

Finally, the metrics can be viewed for one Sudoku problem as follows.

```python
driver.metrics.export(repetition_function_kwargs={"theta_a": 1, "num_execution_steps": 10})
```

The repetition function arguments `theta_a` and `num_execution_steps` are for the repetition rate calculations as discussed in the agentquest [paper](https://aclanthology.org/2024.naacl-demo.19.pdf), section 3.2.

### For other benchmarks

For each benchmark supported in AgentQuest, alongside the README files you can find `example.ipynb` jupyter notebook, where an example is shown how to use the benchmark with human input. The human input can be replaced with an agent call and an agent can be benchmarked with ease. For further information, have a look at the individual README files for the benchmarks.

## AgentQuest Concepts

### Action, State and Observation Classes

These are the three basic classes to represent Agent - Benchmark interactions in AgentQuest. Refer to Figure 1 in [AgentQuest Paper](https://aclanthology.org/2024.naacl-demo.19.pdf).

`Action` is an input to the benchmark. Example: for Hangman game it is a guess letter, for Sudoku game it is a row id, column id and a number.

`State` is the internal state of a benchmark. For some benchmarks, state can be same as last action, Example in Mastermind game where state of the benchmark is last input. But in games like Sudoku or 2048, state of the benchmark is the board configuration.

`Observation` is the feedback from the benchmark to the agent. It usually consists of attributes `output`, `success` and `can_proceed`. Attribute `output` is a textual feedback from the benchmark to the agent based on last action or it can even be initial instructions for an agent. Attribute `success` (bool) indicates if task has been successfully completed. Attribute `can_proceed` (bool) indicates the benchmark/game can be further sent inputs.

Depending upon the benchmarks, the attributes and their data types for these classes might vary. But this concept is central to the design of AgentQuest.

### Driver Class

For every benchmark there is one driver class, conventionally with name `BenchmarkDriver`. The driver class consists of methods to initialize the benchmark and allows agent interaction with benchmark.

For every instance of problem or a task, one driver object needs to be instantiated.

```python
# Example for HangmanDriver
driver = HangmanDriver(goal="TARGET_WORD", ...)
```

#### reset() method

The `reset()` method of a driver object enables explicit initialization of benchmark for a particular instance of a task. It returns an Observation object. Apart from the initialization functions that goes under the hood, `reset()` method returns the initial instructions about the task and benchmark as the first input to the agent.

```python
obs = driver.reset()
```

The `reset()` method is called once for a task in a benchmark. While benchmarking an agent, every time a new task is to be carried out a new driver object is to be initiated and `reset()` method has to be called explicitly.

_Exception: For Webshop benchmark, new driver object instantiation is not required for a new task, just `reset()` method call is enough._

#### step() method

The `step()` method is another important method in a Driver class which forwards the game by one step. It takes in an Action object, carries out the game forwarding logic and returns an Observation object. Usually, the game forwarding logic checks if the action is legitimate or not, if the task is successfully completed or not, changes the state of the game/benchmark and returns a feedback output (Observation) to the agent.

```python
obs = driver.step(HangmanAction("e")) #Guessing letter e
```

There is also step_raw() method in the benchmarks which can take raw string output from agents, parse them in an anticipated format, formulate an Action object and call step() method under the hood to return an Observation object.

**step() vs step_raw() method**: The step_raw() method is only defined in benchmark level in AgentQuest whereas step() method is defined in AgentQuest's base class. For any benchmark step() method is mandatory to implement whereas step_raw() is not mandatory. The benefit of step_raw() is you can immediately plugin the output from an agent without any processing leaving the job of parsing and formulating Action object inside the step_raw() itself. It returns an exception as an Observation output to agent if the agent's output is not parsable allowing it to correct itself. However, if a developer decides to use step() method, the formulation of Action object is left on the discretion of the developer and any validation error caused by improper data type in Pydantic will stop the benchmarking program.

### Metrics Class

Every driver object has a metrics object which keeps track of the interactions between the agent's input (Action), benchmark's state (State) and benchmark's feedback (Observation). This is provided out of the box by AgentQuest for each benchmark and metrics object is instantiated implicitly when a driver object is instantiated as `driver.metrics`.

Each benchmark has a separate `BenchmarkMetrics` class coupled with `BenchmarkDriver` class which inherits the base `Metrics` class.
The metrics object records the interactions as Action, State, Observation tuple and allows calculations of progress rate and repetition rate. Every time the `step()` method in driver is called, a new interaction is recorded in the metrics object.

The `export()` method allows exporting the metrics of a driver object run for a particular task in json. Depending upon the benchmark, some metrics recorded and calculated might vary.

```python
driver.metrics.export(repetition_function_kwargs={"num_execution_steps": 10, "theta_a": 1})
```

#### Aggregating Metrics over multiple driver runs and Visualization
While testing agent for a benchmark, the objective is to provide multiple tasks in the benchmark to the agent and observe the aggregated performance. AgentQuest provides some util functions to aggregate the metrics and visualize the progress and repetition rates in charts.

Follow the [jupyter notebook tutorial](agentquest/tutorial/visualizing_metrics.ipynb) to see how we can aggregate the metrics from Mastermind benchmark and visualize the results.

### Utils Class

Each benchmark might have a BenchmarkUtils class with a bunch of util functions which are either used by its Driver or Metrics class or are used while benchmarking an agent. Usually, it consists of the static methods for parsing agent output and loading data.

## How to write a custom benchmark?

You can write your own benchmarks using AgentQuest's base classes, similar to the benchmarks in AgentQuest and quickly benchmark agents based on your benchmark with custom datasets and metrics.

Follow this tutorial to write a custom benchmark: [NumberGuesser Tutorial](agentquest/tutorial/number_guesser.md)

## How to Use an LLM agent?

We provide a set of [examples](/agents/) showcasing how to implement an LLM agent to solve the MasterMind benchmark. Generalizing to other benchmarks is straightforward.

- `mastermind-openai-chat-model-with-metrics.ipynb`: MasterMind benchmark with OpenAI Simple Chat model and computation of Progress and Repetition Rates metrics
- `mastermind-langchain-chat-model.ipynb`: MasterMind benchmark with LangChain Simple Chat model
- `mastermind-langchain-react.ipynb`: MasterMind benchmark with ReAct agent
- `mastermind-langchain-openai-assistant.ipynb`: MasterMind benchmark with OpenAI Assistant

**Note** All the examples require to configure OpenAI/Azure API keys.
