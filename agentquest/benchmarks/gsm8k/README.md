# GSM8k

GSM8K (Grade School Math 8K) is a dataset by OpenAI with 8.5K high quality linguistically diverse grade school math word problems. The dataset was created to support the task of question answering on basic mathematical problems that require multi-step reasoning.

Link to Paper: https://arxiv.org/pdf/2110.14168v2

Link to Dataset: https://huggingface.co/datasets/openai/gsm8k

## About GSM8k Dataset

**Description from Huggingface GSM8k Dataset page**

These problems take between 2 and 8 steps to solve.
Solutions primarily involve performing a sequence of elementary calculations using basic arithmetic operations (+ − ×÷) to reach the final answer.
A bright middle school student should be able to solve every problem: from the paper, "Problems require no concepts beyond the level of early Algebra, and the vast majority of problems can be solved without explicitly defining a variable."
Solutions are provided in natural language, as opposed to pure math expressions. From the paper: "We believe this is the most generally useful data format, and we expect it to shed light on the properties of large language models’ internal monologues"

### Subset

There are two subsets of the dataset: main and socratic. Both consists of same question, but the answers are differently presented. For main, it's straightforward, but for socratic it is broken down in the further questions.

Examples:
_Main_

    Natalia sold clips to 48 of her friends in April, and then she sold half as many clips in May. How many clips did Natalia sell altogether in April and May?

    Natalia sold 48/2 = <<48/2=24>>24 clips in May. Natalia sold 48+24 = <<48+24=72>>72 clips altogether in April and May. #### 72

_Socratic_

    Natalia sold clips to 48 of her friends in April, and then she sold half as many clips in May. How many clips did Natalia sell altogether in April and May?

    How many clips did Natalia sell in May? ** Natalia sold 48/2 = <<48/2=24>>24 clips in May. How many clips did Natalia sell altogether in April and May? ** Natalia sold 48+24 = <<48+24=72>>72 clips altogether in April and May. #### 72

### Data Fields

The data fields are the same among main and socratic configurations and their individual splits.

    question: The question string to a grade school math problem.

    answer: The full solution string to the question. It contains multiple steps of reasoning with calculator annotations and the final numeric solution.

### Splits

There are in total 8.79k entries with split of 7473 train and 1319 test.

## GSM8k in AgentQuest

GSM8k is a **single-interaction benchmark**. This means the benchmark does not provide intermediate feedback to the agent how the agent did, so it can correct itself. In other words there is only one interaction between benchmark and the agent (hence single-interaction). The metrics like progress rate and repetition rate which provides insight for a single run are not as relevant as in multi-interaction benchmark.

### Summary Table

| **Category**        | **Field**   | **Type** | **Description**                                                                                                            |
| ------------------- | ----------- | -------- | -------------------------------------------------------------------------------------------------------------------------- |
| **State**           | value       | str      | Last answer from the agent to the benchmark                                                                                |
| **Action**          | value       | str      | Answer input to the question from agent.                                                                                   |
| **Observation**     | output      | str      | Feedback to the agent by the benchmark                                                                                     |
|                     | success     | bool     | True if answer matches the ground truth, False otherwise.                                                                  |
|                     | can_proceed | bool     | True if further answer guesses is allowed, False otherwise. Only applicable in interaction mode.                           |
| **Repetition Rate** | -           | float    | Only applicable in interactive mode. Calculates rate of repetition of actions based on simple '==' check on action values. |
| **Progress Rate**   | -           | -        | N/A                                                                                                                        |

### Installation

AgentQuest uses huggingface's `datasets` library to use gsm8k benchmark. This library is already installed when you perform `pip install agentquest`.

## Usage

### Non-Interactive mode

Single-interaction benchmark does not provide feedback to the agent allowing it to correct itself. In non-interactive mode, the step function can only be called once. Non-interactive mode is selected by setting `interactive=False` when instantiating `Gsm8kDriver` object. Remember, for other multi-interaction benchmarks, there is no argument of interactive in the Driver class since they are always interactive.

```python
from agentquest.benchmarks.gsm8k import Gsm8kDriver, Gsm8kUtils, Gsm8kAction
# valid_categories = ["main", "socratic"]
# valid_splits = ["train", "test"]
dataset = Gsm8kUtils.load_data(category="main", split="train")
accumulated_metrics = []

for problem in dataset.to_dict(orient="records"):
    driver = Gsm8kDriver(
        problem=problem["question"], goal=problem["answer"], interactive=False
    )
    obs = driver.reset()
    human_input = input(obs.output)  # Can be replaced by agent input
    obs = driver.step(Gsm8kAction(value=str(human_input)))
    # obs = driver.step_raw(str(human_input))
    print(obs.output)
    accumulated_metrics.append(driver.metrics.export())
```

Calling the `reset()` method initializes an instance of Gsm8k problem and provides the problem in observation object's output
attribute to be used as input to agent. Example of an obsevation output.

```
Natalia sold clips to 48 of her friends in April, and then she sold half as many clips in May. How many clips did Natalia sell altogether in April and May?
Your response must in the following format
Answer: <answer>
```

AgentQuest adds the response format at the end of the problem, so that the agent's output can be easily parsed using `step_raw` method. Developers are free to cut this part out or even send a custom parser to `step_raw` method.

```python
# dummy_agent_output = "Answer: 31415" # To replace with actual agent output
obs = driver.step_raw(value=dummy_agent_output)
```

Here is the aggregated metrics (interrupted after 3 problems to keep it short.)

```python
[{'problem': 'Natalia sold clips to 48 of her friends in April, and then she sold half as many clips in May. How many clips did Natalia sell altogether in April and May?',
  'goal': 'Natalia sold 48/2 = <<48/2=24>>24 clips in May.\nNatalia sold 48+24 = <<48+24=72>>72 clips altogether in April and May.\n#### 72',
  'success': True,
  'actions': [{'value': '72'}],
  'states': [{'value': '72'}],
  'observations': [{'output': 'Correct answer!!!',
    'success': True,
    'can_proceed': False}]},
 {'problem': 'Weng earns $12 an hour for babysitting. Yesterday, she just did 50 minutes of babysitting. How much did she earn?',
  'goal': 'Weng earns 12/60 = $<<12/60=0.2>>0.2 per minute.\nWorking 50 minutes, she earned 0.2 x 50 = $<<0.2*50=10>>10.\n#### 10',
  'success': True,
  'actions': [{'value': '10'}],
  'states': [{'value': '10'}],
  'observations': [{'output': 'Correct answer!!!',
    'success': True,
    'can_proceed': False}]},
 {'problem': 'Betty is saving money for a new wallet which costs $100. Betty has only half of the money she needs. Her parents decided to give her $15 for that purpose, and her grandparents twice as much as her parents. How much more money does Betty need to buy the wallet?',
  'goal': "In the beginning, Betty has only 100 / 2 = $<<100/2=50>>50.\nBetty's grandparents gave her 15 * 2 = $<<15*2=30>>30.\nThis means, Betty needs 100 - 50 - 30 - 15 = $<<100-50-30-15=5>>5 more.\n#### 5",
  'success': False,
  'actions': [{'value': '112'}],
  'states': [{'value': '112'}],
  'observations': [{'output': 'Wrong answer!!!',
    'success': False,
    'can_proceed': False}]}]
```

The `step()` method parses the goal text to check only the number after four hashtag (#) characters for the agent's input.

### Interactive Mode

AgentQuest provides an option for interactive mode for GSM8k, where the benchmark responds back to an agent with feedback, if the answer is incorrect. The agent can correct itself based on the feedback. To do this, the driver should be initialized with argument `interactive=True`.

Check `example.ipynb` to see the interactive mode implementation.
