# Hangman Benchmark

Hangman is a classic word-guessing game where players try to uncover a hidden word one letter at a time. With each incorrect guess, a part of a stick figure is drawn, and the goal is to guess the word before the figure is fully completed. The game combines vocabulary knowledge with strategic thinking as players balance risk and reward in their guesses.

Reference Wikipedia Page: [Hangman](<https://en.wikipedia.org/wiki/Hangman_(game)>)

## AgentQuest Implementation of Hangman

In AgentQuest's implementation of Hangman, the goal for an agent is to correctly guess the target word in an instance, by guessing one character at a time. After each guess letter, the game provides feedback if the guessed letter exists in the word or not. If yes, it shows at which position the letter fits. Agentquest supports 3,4,5,6 lettered words (total 61 words) to benchmark your agents.
You can add your own words and run the benchmark for larger set of words. There are six lives for the game, and every incorrect guess letter would take one life. If there are 0 lives remaining, no more guesses are allowed and game is over.

### Summary Table

| **Category**        | **Field**       | **Type**  | **Description**                                                                                |
| ------------------- | --------------- | --------- | ---------------------------------------------------------------------------------------------- |
| **State**           | value           | str       | Current word state with unguessed letters masked                                               |
|                     | lives           | int       | Remaining number of guesses, starting at 6                                                     |
|                     | letters_guessed | list[str] | All letters guessed so far                                                                     |
| **Action**          | value           | str       | A single letter guess.                                                                         |
| **Observation**     | output          | str       | Feedback to the agent by the benchmark                                                         |
|                     | success         | bool      | True if all letters in the target word are guessed correctly, False otherwise                  |
|                     | can_proceed     | bool      | True if game can still be played (lives remaining is not zero), False otherwise                |
| **Repetition Rate** | -               | float     | Rate to quantify the repetitions of actions. Based on simple '==' check between action values. |
| **Progress Rate**   | -               | float     | Fraction of correct letters guessed so far, to the total number of letters in the word.        |

## Usage

### Running Hangman with agentquest

```python
from agentquest.benchmarks.hangman import HangmanDriver, HangmanUtils

word = HangmanUtils.load_data(data_path="./data.json", category="5 letters")[0]
driver = HangmanDriver(goal=word)

obs = driver.reset()
print(obs.output)

while not obs.success and obs.can_proceed:
    human_input = input() # Replace this with agent's output
    obs = driver.step(HangmanAction(value=human_input))
    print(obs.output)
```

Calling the reset() function initializes the Hangman game and gives the agent instructions about the game. Here is the initial instruction for every Hangman game instance.

```
Let's play Hangman! Your objective is to guess the target word one letter at a time.
The question marks represent letters in the word yet to be guessed.
As you guess letters correctly, they will be revealed in their correct positions.
You start with 6 lives. For each incorrect guess, one life will be deducted.
Take a guess by providing a letter. The response must be in the following format:
Letter: <letter>
Your target word is 6 characters long.
Game current state.
Word: ??????
You have 6 guesses left.
You have already guessed following letters:
-------------------------

  +---+
  |   |
      |
      |
      |
      |
=========

```

The `reset` method initializes the hangman game and provides description for the agent to start guessing characters. The `step` method forwards the game with every letter guesses until the number of lives run out, or the word is guessed successfully.

An LLM agent is expected to produce an output in the format `Letter: <letter>`. This can either be parsed by the developer manually and `step` method can be called with `HangmanAction` object. Another option is to call the `step_raw` method which can take the raw agent output in string format.

```python
# dummy_agent_output = "Letter: e" # To replace with actual agent output
obs = driver.step_raw(value=dummy_agent_output)
```

The step_raw method calls a parser with regex that parses the agent's output searching for `Letter: <letter>`. The developer can pass their own custom parser to step_raw method. Also, the developers are free to process the initial observation output and send it to their agents as they prefer.

Observation output example for a `step` method call. The letter input here is `b`.

```
The guessed letter b was correct.
Game current state.
Word: b?????
You have 6 guesses left.
You have already guessed following letters: b
-------------------------

  +---+
  |   |
      |
      |
      |
      |
=========
```

See `example.ipynb` for the example code to see how to run Hangman benchmark with AgentQuest.

### Metrics

With AgentQuest, metrics are automatically recorded within the `driver.metrics` object. Once the agent has completed it's run for a problem, the metrics can be viewed with method `export()`

```python
driver.metrics.export(repetition_function_kwargs={"theta_a": 1, "num_execution_steps": 10})
```

Here is the metrics output example for an instance of Hangman game in AgentQuest. The following game was manually interrupted after 3 rounds to keep the metrics output small.

```python
{'goal': 'beaver',
 'success': False,
 'actions': [{'value': 'b'}, {'value': 'i'}, {'value': 'q'}],
 'states': [{'value': 'b?????', 'lives': 6, 'letters_guessed': ['b']},
  {'value': 'b?????', 'lives': 5, 'letters_guessed': ['b', 'i']},
  {'value': 'b?????', 'lives': 4, 'letters_guessed': ['b', 'i', 'q']}],
 'observations': [{'output': 'The guessed letter b was correct. \nGame current state.\nWord: b?????\nYou have 6 guesses left.\nYou have already guessed following letters: b \n-------------------------\n\n  +---+\n  |   |\n      |\n      |\n      |\n      |\n=========\n\n',
   'success': False,
   'can_proceed': True},
  {'output': 'The guessed letter i was incorrect. \nGame current state.\nWord: b?????\nYou have 5 guesses left.\nYou have already guessed following letters: b, i \n-------------------------\n\n  +---+\n  |   |\n  O   |\n      |\n      |\n      |\n=========\n\n',
   'success': False,
   'can_proceed': True},
  {'output': 'The guessed letter q was incorrect. \nGame current state.\nWord: b?????\nYou have 4 guesses left.\nYou have already guessed following letters: b, i, q \n-------------------------\n\n  +---+\n  |   |\n  O   |\n  |   |\n      |\n      |\n=========\n\n',
   'success': False,
   'can_proceed': True}],
 'repetition_rate': 0.0,
 'progress': [0.16666666666666666, 0.16666666666666666, 0.16666666666666666]}

```

#### Progress Rate for Hangman

Progress rate signifies how far an agent has reached in solving the goal. For Hangman, it is simply how many letters in the target word is correctly guessed. So, this count of correctly guessed letters is divided by number of letters in the target word to calculate the progress rate.

#### Repetition Rate for Hangman

For Hangman, there are 26 possible characters as inputs. Hence, to calculate repetition rate, we count how many times the letter inputs are repeated by the agent to solve a game of Hangman.

The arguments passed as dictionary in export() method are for calculating repetition rates (_theta_a_ threshold and _number of execution steps_) as explained in the repetition rate formula in the [AgentQuest](https://arxiv.org/pdf/2404.06411) paper.
