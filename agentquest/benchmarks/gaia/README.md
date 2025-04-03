# GAIA

GAIA is a benchmark by Meta with real-world questions that demands a set of fundamental abilities such as reasoning, multi-modality handling, web browsing, and generally tool-use proficiency.

Link to Paper: https://arxiv.org/abs/2311.12983

Link to dataset: https://huggingface.co/gaia-benchmark

## About GAIA Dataset

_Description copied from Huggingface GAIA Dataset Page_

GAIA is a benchmark which aims at evaluating next-generation LLMs (LLMs with augmented capabilities due to added tooling, efficient prompting, access to search, etc).
GAIA is made of more than 450 non-trivial question with an unambiguous answer, requiring different levels of tooling and autonomy to solve. It is therefore divided in 3 levels, where level 1 (146 problems) should be breakable by very good LLMs, level 2 (245 problems) and level 3 (75 problems) indicate a strong jump in model capabilities. Each level is divided into a fully public dev set for validation, and a test set with private answers and metadata.

**Columns**: _task_id, Question, Level, Final answer, file_name, file_path, Annotator Metadata_

## GAIA in AgentQuest

GAIA is a **single-interaction benchmark**. The benchmark does not provide intermediate feedback to the agent how the agent did, so it can correct itself i.e. there is only one interaction between benchmark and the agent (hence single-interaction). The metrics like progress rate and repetition rate which provides insight for one run are not as relevant as in multi-interaction benchmark.

AgentQuest provides an easy way to benchmark your agent with GAIA and calculate success rate over multiple problems in the validation set. It also provides a script showing how to benchmark your agent in the test set and create a submission for GAIA leaderboard.

There is also an interactive mode (custom implementation in AgentQuest). This allows multi-interaction between benchmark and an agent. However, the response is limited where the benchmark tells an agent if the answer is not correct and allows the agent to correct itself. However, any other hints to solve the problem are not provided.

### Splits

The validation split has 165 problems
The test split has 301 problems. GAIA does not provide final answer (ground truth) for test split. So, in AgentQuest we can only benchmark using the validation split. However, we also provide test split for the user which can be used to submit the results to GAIA [leaderboard](https://huggingface.co/spaces/gaia-benchmark/leaderboard).

### Summary Table

| **Category**        | **Field**   | **Type** | **Description**                                                                                           |
| ------------------- | ----------- | -------- | --------------------------------------------------------------------------------------------------------- |
| **State**           | value       | str      | Last answer from the agent to the benchmark                                                               |
| **Action**          | value       | str      | Answer input to the question from agent.                                                                  |
| **Observation**     | output      | str      | Feedback to the agent by the benchmark                                                                    |
|                     | success     | bool     | True if answer matches the ground truth, False otherwise.                                                 |
|                     | can_proceed | bool     | True if further answer guesses is allowed, False otherwise. Only applicable in interaction mode.          |
| **Repetition Rate** | -           | float    | Only applicable in interactive mode. Calculates rate of repetition of actions based on levenshtein ratio. |
| **Progress Rate**   | -           | -        | N/A                                                                                                       |

### Installation

Since GAIA is a gated dataset in Huggingface, developers need to create a huggingface account to download this dataset. To install the GAIA dataset developers need to run the following script. To use the multimodal file data from GAIA, developers will have to explicitly clone the GAIA repo and access the files. For simple questions and their answers, AgentQuest uses huggingface's datasets library to do that. Developers will still need to login to huggingface-cli.

```bash
pip install agentquest
huggingface-cli login #Add the token as git credential
git clone https://huggingface.co/datasets/gaia-benchmark/GAIA #For downloading the multimodal data
```

The script clones the [GAIA repo](https://huggingface.co/datasets/gaia-benchmark/GAIA) in huggingface. Also, make sure the token entered has GIT access and select `"Add the token as git credential"`.

## Usage

### Non Interactive mode

Single-interaction benchmark does not provide feedback to the agent allowing it to correct itself. In non-interactive mode, the step function can only be called once. This is ensured by setting `interactive=False` when instantiating `GaiaDriver` object. Remember, for other multi-interaction benchmarks, there is no argument of interactive in the Driver class since they are always interactive.

```python
from agentquest.benchmarks.gaia import GaiaDriver, GaiaUtils, GaiaAction
# valid_categories = ["2023_all", "2023_level1", "2023_level2", "2023_level3"]
# valid_splits = ["validation", "test", "all"]
dataset = GaiaUtils.load_data(category="2023_all", split="validation")

aggregated_metrics = []
for problem in dataset.to_dict(orient="records"):
    if problem.get("file_name", ""):
        extra_filepath = GaiaUtils.get_filepath(problem.get("file_name", ""))
        print("File path for the problem: ", extra_filepath)
        # It is up to the developers to process the supplementary file or send it to the agent directly.
    driver = GaiaDriver(
        problem=problem["Question"], goal=problem["Final answer"], interactive=False
    )
    obs = driver.reset()
    human_input = input(obs.output)  # Can be replaced by agent input
    obs = driver.step(GaiaAction(value=str(human_input)))
    # obs = driver.step_raw(str(human_input))
    print(obs.output)
    aggregated_metrics.append(driver.metrics.export())
```

Calling the `reset()` method initializes an instance of GAIA problem and provides the problem in observation object's output attribute. Example of an observation output.

```
A paper about AI regulation that was originally submitted to arXiv.org in June 2022 shows a figure with three axes, where each axis has a label word at both ends. Which of these words is used to describe a type of society in a Physics and Society article submitted to arXiv.org on August 11, 2016?
Your response must in the following format
Answer: <answer>
```

AgentQuest adds the response format at the end of the problem, so that the agent's output can be easily parsed using `step_raw` method. Developers are free to cut this part out or even send a custom parser to `step_raw` method.

```python
# dummy_agent_output = "Answer: wonderful" # To replace with actual agent output
obs = driver.step_raw(value=dummy_agent_output)
```

Here is the aggregated metrics (interrupted after 2 problems to keep it short.)

```python
[{'problem': 'A paper about AI regulation that was originally submitted to arXiv.org in June 2022 shows a figure with three axes, where each axis has a label word at both ends. Which of these words is used to describe a type of society in a Physics and Society article submitted to arXiv.org on August 11, 2016?',
  'goal': 'egalitarian',
  'success': True,
  'actions': [{'value': 'egalitarian'}],
  'states': [{'value': 'egalitarian'}],
  'observations': [{'output': 'Correct answer!!!',
    'success': True,
    'can_proceed': False}]},
 {'problem': 'I’m researching species that became invasive after people who kept them as pets released them. There’s a certain species of fish that was popularized as a pet by being the main character of the movie Finding Nemo. According to the USGS, where was this fish found as a nonnative species, before the year 2020? I need the answer formatted as the five-digit zip codes of the places the species was found, separated by commas if there is more than one place.',
  'goal': '34689',
  'success': False,
  'actions': [{'value': 'not sure'}],
  'states': [{'value': 'not sure'}],
  'observations': [{'output': 'Wrong answer!!!',
    'success': False,
    'can_proceed': False}]}]
```

### Interactive Mode

AgentQuest provides an option for interactive mode for GAIA, where the benchmark responds back to an agent with feedback, if the answer is incorrect. The agent can correct itself based on the feedback. To do this, the driver should be initialized with argument `interactive=True`.

Check `example.ipynb` to see the interactive mode implementation and making your results ready for GAIA leaderboard **submission**.
