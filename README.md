# README

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
- [Prerequisites](#prerequisites)
- [How to Install and Test a Benchmark?](#how-to-install-and-test-a-benchmark)
- [How to Write a Custom Driver?](#how-to-write-a-custom-driver)
- [How to Use a Driver?](#how-to-use-a-driver)
- [How to Use an LLM Agent?](#how-to-use-an-llm-agent)


## Structure of This Repo
This repo is organized as follows:
- `agentquest` folder. It contains the main libraries and drivers needed 
to run and evaluate the benchmarks
- `benchmarks` folder. It contains the documentation, the python requirements and
the installation script (`setup.sh`) of each benchmark
- `examples` folder. It contains one instance of each benchmark callable from 
command line or jupyter notebook.
- `agents` folder. It contains examples on how to implement LLM agents through different frameworks testing one benchmark.


## Prerequisites

Install our `agentquest` package through
```bash
$ pip3 install -e .
```
or
```bash
$ python3 -m venv .venv
$ source .venv/bin/activate
$ pip install -e .
```






## How to Install and Test a Benchmark?

By default we provide the following benchmarks:

| | Reasoning Type | Categories |
|---|:---:|:---:|
| [MasterMind](/benchmarks/mastermind/README.md) | Deductive | 5 |
| [AlfWorld](/benchmarks/alfworld/README.md) | Embodied | 6 |
| [Sudoku](/benchmarks/sudoku/README.md) | Spatial | 3 |

### Installing a Benchmark

The first step is to install the requirements of each benchmark through the `Makefile`.
You can both install all the benchmarks or a specific one.

To install all the benchmarks in a row, just open a terminal and run
```bash
$ make installall
```

Otherwise, to install a specific benchmark you can run
```bash
$ make install-BENCHMARK_NAME
```
where `BENCHMARK_NAME` is one among `mastermind`, `alfworld` or `sudoku`.

### Testing a Benchmark
In the `example` folder we provide two ways to test each benchmark. 
1) In the `scripts` folder you can find python scripts to test one instance of the implemented benchmarks from command line.

To test one benchmark, open a terminal and run:
```bash
$ python3 examples/scripts/BENCHMARK_NAME
```

2) In the [`notebooks`](/examples/notebooks/) folder you can find jupyter notebooks providing an 
overview on how to use the benchmarks through python codes.

**Note** The AlfWorld benchmark requires to set a symlink to `alfworld_data` directory. Run the following command from the root of this repository.
```bash
ln -s $PWD/benchmarks/alfworld/alfworld_data /tmp/alfworld_data
```


## How to write a custom driver?

A driver is a wrapper allowing a user (human, LLM agent, generic script, etc.) to interact with an environment (e.g., AlfWorld, Mastermind).
This allows to write a custom plug-and-play interface for an existing benchmark or for a new proposed one. The interaction between the environment occurs through two entities: 
- _Observations_ reporting the current environment state and the information about the game conclusion
- _Actions_, or an external inputs provided by the user changing the environment status.

Here we show how to design a custom driver for any benchmark.

### Prerequisites

Create a folder for your custom driver in the [`benchmarks`](#benchmarks/) folder and create an empty driver file.

```bash
$ make init-CUSTOM_BENCHMARK
```
Replace `CUSTOM_BENCHMARK` according to your new benchmark. This will create: 
- the `agentquest/drivers/CUSTOM_BENCHMARK` folder for the driver to customize.
The folder contains the script `CUSTOM_BENCHMARK_driver.py` and the `__init__.py` file 
- the `benchmarks/CUSTOM_BENCHMARK` folder containing
    - an empty `README.md` file for the benchmark documentation
    - an empty `requirements.txt` file for the python requirements of the benchmark
    - an empty `setup.sh` file as installation script.
- the `agentquest/data/CUSTOM_BENCHMARK` folder for the instances of the benchmark.

After having designed the driver and the benchmark, remember to provide documentation, requirements and setup instructions through the files in `benchmarks/CUSTOM_BENCHMARK`.

**Note** to remove an initialized benchmark, just run
```bash
$ make clean-CUSTOM_BENCHMARK
```

### Observations

Observations inform the users about the current environment status. We provide a template with two mandatory attributes:
- `output`. A string reporting the environment status
- `done`. A boolean variable indicating if the game is ended (True) or still running (False)

```python
class Observation():
    def __init__(self, output:str, done:bool):
        self.output = output # Current environment status
        self.done = done # True if the game ended, False otherwise.
```

### Actions

Actions allows the user to interact with the environment changing its status. We provide a template with one mandatory attribute:
- `action_value`. A string that, once processed by the driver, triggers the environment change.

To customize the interactions, you can define optional attributes. In the following we provide an overview of the `Action` class

```python
class Action():
    def __init__(self, action_value:str, **kwargs):
        self.action_value = action_value # Action to interact with the environment

        # Set additional custom attributes
        for key, value in kwargs.items():
            setattr(self, key, value)
```

### Driver

Finally, we provide an overview of the main driver template. 


```python
from agentquest.utils import Observation

class CustomDriver():
    def __init__(self, environment):
        self.environment = environment
        # Write your driver initialization here.
        # ...
```
The reset method reset the driver and the environment returning the first observation
from the environment.
```python
    def reset(self):
        # Reset your environment status here.
        # ...

        # Instantiate your initial observation from the environment
        obs = Observation(
            output='This is the initial environment status',
            done=False
        )

        return obs
```
The step method processes an action to modify the environment and returns the 
observation from the environment (i.e., the environment status after the actions).
```python
    def step(self, action):
        action = action.action_value # Retrieve the action value
        # Process your action here
        # ...

        # Run one game round. Typically you change/update the game status 
        # according to the provided output

        # Instantiate your current observation from the environment
        obs = Observation(
            output='This is the current game status',
            done=False
        )

        return obs

```

### Example

As a very simple example we explain the driver for the Mastermind game. 

Mastermind is a code-breaking game where one player creates a secret code of a fixed lenght with digits from 0 to 9, and the other player tries to guess the code. The code-maker provides feedbackdigit after each guess, indicating the number of correct colors and their correct positions, allowing the code-breaker to deduce and refine their guesses.

```python
from agentquest.utils import Observation
from collections import Counter

class MasterMindDriver():
    def __init__(self, truth:str):
        self.truth = truth # The game solution
        self.split_truth = [x for x in truth] # Split the solution in digits
```

Define custom methods used by the environment:
- `get_correct_positions`. Custom function retrievig the number of digits in the same position appearing in two lists.
- `count_common_elements`. Custom function retrieving the number of common digits between two lists independently from their positions.

```python
    def get_correct_positions(self, list1:list, list2:list):
        number_and_position = 0
        # Compare the position of the digits in the lists
        for i, j in zip(list1, list2):
            if i == j: number_and_position += 1

        return number_and_position

    def count_common_elements(self, list1:list, list2:list):
        # Get common elements
        common_elements = Counter(list1) & Counter(list2)
        # Get the number of common elements
        count = sum(common_elements.values())
        
        return count
```

Define the mandatory `reset` method initializing the environment.

```python
    def reset(self):
        # Get the length of the solution
        code_len = len(self.split_truth)

        # Instantiate the starting environment status
        obs = Observation(
            output = f'Start guessing the {code_len} digits number.',
            done = False
        )
        
        return obs
```

Define the mandatory `step` method implementing one Mastermind round.

```python
    def step(self, action):
        # Retrieve the action value and trim exceeding digits
        action = action.action_value[:len(self.split_truth)]

        # If the guess is correct, end the game
        if action == self.truth:
            obs = Observation(output='You Won!', done=True)

            return obs

        # Get the guessed number in digits
        split_guess = [x for x in str(action)]

        # Get the number of correct digits in the correct position
        number_and_position = self.get_correct_positions(self.split_truth, split_guess)

        # Get the number correct digits independently from their position
        number_only = self.count_common_elements(self.split_truth, split_guess)
        number_only -= number_and_position
        
        # Instantiate the current observation
        obs = Observation(
            output = (
                f'Your guess has {number_only} correct numbers in the wrong '
                f'position and {number_and_position} correct numbers in the '
                f'correct position. Keep guessing.'
            ),
            done = False
        )

        return obs
```






## How to use a driver?
We provide a simple example from the same Mastermind environment just decribed.
With the following snippet you will be able to run a game of Mastermind.

Fistly import the driver and the action template.

```python
from agentquest.drivers.mastermind import MasterMindDriver
from agentquest.utils import Action
```

Initialize the driver providing the final solution to guess and reset the environment getting the first observation.

```python
driver = MasterMindDriver(truth='7327')
obs = driver.reset()
obs.output, obs.done

>>> ('Start guessing the 4 digits number.', False)
```

Instantiate the action with the current guess and run one Mastermind round.

```python
guess = Action(action_value='1234')
obs = driver.step(guess)
obs.output, obs.done

>>> ('Start guessing the 4 digits number.', False)
>>> ('Your guess has 2 correct numbers in the wrong position and 0 correct '
...  'numbers in the correct position. Keep guessing.', False)
```

Repeat...

```python
guess = Action(action_value='7327')
obs = driver.step(guess)
obs.output, obs.done

>>> ('You Won!', True)
```


## How to Use an LLM agent?
We provide a set of [examples](/agents/) showcasing how to implement an LLM agent to solve the MasterMind benchmark. Generalizing to other benchmarks is straightforward.

- `mastermind-openai-chat-model-with-metrics.ipynb`: MasterMind benchmark with OpenAI Simple Chat model and computation of Progress and Repetition Rates metrics
- `mastermind-langchain-chat-model.ipynb`: MasterMind benchmark with LangChain Simple Chat model
- `mastermind-langchain-react.ipynb`: MasterMind benchmark with ReAct agent
- `mastermind-langchain-openai-assistant.ipynb`: MasterMind benchmark with OpenAI Assistant

**Note** All the examples require to configure OpenAI/Azure API keys.
