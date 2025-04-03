# Wordle Benchmark

Wordle is a simple word-guessing game where players aim to guess a five-letter word within six attempts. Each guess provides feedback in the form of colored tiles: green for correct letters in the right position, yellow for correct letters in the wrong position, and gray for incorrect letters. The game encourages strategic thinking and vocabulary skills as players narrow down possibilities with each clue. Originally created by Josh Wardle, Wordle has gained immense popularity for its straightforward gameplay and daily puzzle format. It's a fun and engaging way to challenge yourself or compete with friends!

Reference Wikipedia Page: [Wordle](https://en.wikipedia.org/wiki/Wordle)

## AgentQuest Implementation of Wordle

In AgentQuest's implementation of wordle, there are 227 five-letter words that can be used to benchmark an agent. It is customizable for a developer to provide their own set of five-letter words.

### Summary Table

| **Category**        | **Field**     | **Type**  | **Description**                                                                                           |
| ------------------- | ------------- | --------- | --------------------------------------------------------------------------------------------------------- |
| **State**           | value         | str       | Last guessed word                                                                                         |
|                     | lives         | int       | Remaining number of guesses, starting at 6                                                                |
|                     | words_guessed | list[str] | Words guessed so far                                                                                      |
| **Action**          | value         | str       | A five-letter word guess.                                                                                 |
| **Observation**     | output        | str       | Feedback to the agent by the benchmark                                                                    |
|                     | success       | bool      | True if guess word matches the target word, False otherwise                                               |
|                     | can_proceed   | bool      | True if game can still be played (lives remaining is not zero), False otherwise                           |
| **Repetition Rate** | -             | float     | Rate to quantify the repetitions of actions. Based on levenshtein ratio between two words.                |
| **Progress Rate**   | -             | float     | Fraction of correct letters in right position guessed so far, to the total number of letters in the word. |

## Usage

### Running Wordle with agentquest

```python
from agentquest.benchmarks.wordle import WordleDriver, WordleUtils, WordleAction

data = WordleUtils.load_game(data_path="./data.json")
driver = WordleDriver(goal=data[0])

obs = driver.reset()
print(obs.output)

while not obs.success and obs.can_proceed:
    human_input = input() # Replace with agent call
    obs = driver.step(WordleAction(value=human_input))
    print(obs.output)
```

Calling the reset() function initializes the Wordle game and gives the agent instructions about the game. Here is the initial instruction for every Wordle game instance.

```
Welcome to Wordle. Your goal is to guess a 5 letter word only containing letters in the English alphabet.
Letters correctly guessed in the correct position will be shown with a '✓' in place.
Letters correctly guessed but in the wrong position will be shown with a '⚠' in place.
Letters incorrectly guessed will be shown with a '✘' in place.You have six lives.
Take a guess by providing a 5 letter word. The response must be in the following format.
Word: <word>
```

An LLM agent is expected to produce an output in the format `Word: <word>`. This can either be parsed by the developer manually and step method can be called with `WordleAction` object. Another option is to call the step_raw method which can take the raw agent output in string format.

```python
obs = driver.step_raw(value=agent_output)
```

The step_raw method calls a parser with regex that parses the agent's output searching for `Word: <word>`. The developer can pass their own custom parser to step_raw method. Also, the developers are free to process the initial observation output and send it to their agents as they prefer.
The `step` method call advances the game forward with agent's input (action) and benchmark provides feedback to the action (observation).

Observation output for a step method call. The word guessed here is `hello`.

```
│ H ││ E ││ L ││ L ││ O │

│ ✘ ││ ⚠ ││ ✘ ││ ✘ ││ ✘ │
Letter h is a wrong letter.
Letter e is a correct letter in wrong position.
Letter l is a wrong letter.
Letter l is a wrong letter.
Letter o is a wrong letter.
You have 5 lives remaining.
```

See `example.ipynb` for the example code to see how to run Wordle benchmark with AgentQuest.

### Metrics

With AgentQuest, metrics are automatically recorded within the `driver.metrics` object. Once the agent has completed its run for a problem, the metrics can be viewed with method `export()`

```python
driver.metrics.export(repetition_function_kwargs={"theta_a": 0.5, "num_execution_steps": 10})
```

Here is the metrics output example for an instance of Wordle game in AgentQuest.

```python
{'goal': 'abide',
 'success': True,
 'actions': [{'value': 'hello'}, {'value': 'aside'}, {'value': 'abide'}],
 'states': [{'value': 'hello', 'lives': 5, 'words_guessed': ['hello']},
  {'value': 'aside', 'lives': 4, 'words_guessed': ['hello', 'aside']},
  {'value': 'abide',
   'lives': 3,
   'words_guessed': ['hello', 'aside', 'abide']}],
 'observations': [{'output': '\n│ H ││ E ││ L ││ L ││ O │\n\n│ ✘ ││ ⚠ ││ ✘ ││ ✘ ││ ✘ │\nLetter h is a wrong letter.\nLetter e is a correct letter in wrong position.\nLetter l is a wrong letter.\nLetter l is a wrong letter.\nLetter o is a wrong letter.\nYou have 5 lives remaining. \n',
   'success': False,
   'can_proceed': True},
  {'output': '\n│ A ││ S ││ I ││ D ││ E │\n\n│ ✓ ││ ✘ ││ ✓ ││ ✓ ││ ✓ │\nLetter a is a correct letter in right position.\nLetter s is a wrong letter.\nLetter i is a correct letter in right position.\nLetter d is a correct letter in right position.\nLetter e is a correct letter in right position.\nYou have 4 lives remaining. \n',
   'success': False,
   'can_proceed': True},
  {'output': '\n│ A ││ B ││ I ││ D ││ E │\n\n│ ✓ ││ ✓ ││ ✓ ││ ✓ ││ ✓ │\nYou have won!!! The word was abide',
   'success': True,
   'can_proceed': False}],
 'repetition_rate': 0.1111111111111111,
 'progress': [0.0, 0.8, 1.0]}
```

#### Progress Rate for Wordle

Progress rate signifies how far an agent has reached in solving the goal. For wordle, it is simply how many correct letters in correct position are guessed so far divided by total number of letters in the word (which is 5). Each correct letter guessed in correct position is one milestone completed. However, it does not take into account the letters guessed correctly but in wrong position.

#### Repetition Rate for Wordle

Repetition rate signifies how many times an agent has repeated certain action. In wordle, an action is a word that is being guessed. We use [Levenshtein distance](https://en.wikipedia.org/wiki/Levenshtein_distance) to calculate the similarity between two words, and then calculate the [repetition rate](https://arxiv.org/pdf/2404.06411).

The arguments passed as dictionary in export() method are for calculating repetition rates (_theta_a_ threshold and _number of execution steps_) as explained in the repetition rate formula in the [AgentQuest](https://arxiv.org/pdf/2404.06411) paper.
