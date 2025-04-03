# Tutorial for AgentQuest NumberGuesser

AgentQuest enables you to test your agents seamlessly in different benchmarks. You can also measure the performance of an agent in a custom benchmark or with custom metrics. This can be done by extending AgentQuest’s base classes and adapt them to your use cases. In this tutorial, we will demonstrate how AgentQuest’s base classes: **_Observation_**, **_Action_**, **_State_**, **_Driver_** and **_Metrics_** can be extended to new benchmarks.

### Benchmark: NumberGuesser Game

Let’s start implementing NumberGuesser game in AgentQuest. The game is played as follows. There is a target number, which the agent has to guess. Every time a guess is made, the game provides a feedback if the target number was greater or lower than the guess. When the guess is equal to the target number, you win.

### Step 1: Set up folders and basic files.

From the project’s root directory, run the following commands

```bash
mkdir number_guesser
cd number_guesser
touch __init__.py
touch driver.py
```

### Step 2: **Setting up Action, State and Observation** in _driver.py_

First let’s conceptualize what the **_Action_**, **_State_** and **_Observation_** will be for NumberGuesser game.

**_Action_** is the input that is provided by an agent to the benchmark. In this case it will simply be the number. The base class `Action` shall be extended to create `NumberGuesserAction` and the attribute `value` (already present in the base class) shall be used to store the input.

<aside>
🏝️

The base class `value` attribute is by default **_str_** data type, and we can change it to other data type (like **_int_**). However, to keep the code simple, we keep the attribute as it is to **_str_**.

</aside>

**_State_** is the internal state of the benchmark or game in this case. This would be the last guess made by the agent. The base class `State` has default attribute `value` which is **_str_** by default. We shall use the default attribute for this game.

<aside>
🏝️

Here you might wonder, the action value is equal to the state value; so why do we need another class of State. But for many benchmarks, the benchmark state can be very different than action value. Take Sudoku as an example, where game state is 9x9 grid of numbers whereas action is row, column and the number to insert.

</aside>

**_Observation_** is the feedback from the benchmark once an action is carried out and a state is changed. This observation provides the agent information on how the previous action did and allows it to reason on what to do next. In this case, the observation should consist of text message of how if the guess number was greater, lower or equal to the target message.

The base class `Observation` consists of attribute `output: str` to carry textual feedback from the benchmark, `success: bool` to signify if the goal has been reached and `can_proceed: bool` if the game can be further played.

Here is the code for NumberGuesser Action, Observation and State classes.

```python
#driver.py
from agentquest.lib import Action, Observation, State

class NumberGuesserAction(Action):
    """Action class for NumberGuesser game
    Attributes:
        value (str) : New guess from the agent."""

    pass

class NumberGuesserObservation(Observation):
    """Observation class as feedback from game to the agent.
    Attributes:
        output (str) :
        success (bool) :
        can_proceed (bool) :
    """

    pass

class NumberGuesserState(State):
    """State class for NumberGuesser game
    Attributes:
        value (str) : Last guessed number."""

    pass
```

<aside>
🏝️

**Note**

The base classes Action, Observation, State are Pydantic classes. Hence, the extended classes are also Pydantic classes which have strict type checking. This enables AgentQuest to leverage Pydantic’s features and json schema. Developers are encouraged to specify the data types and perform extra validation checks in these extended classes for the benchmark.

</aside>

### Step 3: Setting up the Driver class

The `Driver` class is the class which consists of the logic to run the benchmark. It has two important methods, `reset` and `step` which are called to initialize and run the game step by step respectively. Let’s extend the base class `Driver` to create `NumberGuesserDriver`. We also define a dummy `NumberGuesserMetrics` class for now. We shall come back to Metrics later.

Add the following boilerplate code to your **_driver.py_** file.

```python
#driver.py
from agentquest.lib import Driver, Metrics

class NumberGuesserMetrics(Metrics):
    pass

class NumberGuesserDriver(Driver):
    def __init__(
        self,
        goal: Any | None = None,
    ):
        super().__init__(goal, metrics_class=NumberGuesserMetrics)

    def reset(self) -> NumberGuesserObservation:
        super().reset()
        # TODO: Write RESET logic here.
        pass

    def step(self, action: NumberGuesserAction) -> NumberGuesserObservation:
        super().step(action)
        # TODO: Write STEP logic here
        pass

```

Now, let’s go into each methods of the `NumberGuesserDriver` class.

1. `__init__()` method

   The `__init__` method for the driver class is intended to set up necessary variables for one driver object. It also creates a metrics object `self.metrics` attribute using the passed **_metrics_class_** (which happens in the `super().__init__` call.)

   But, it does not initialize the game. That part we leave to `reset` method. This is done so because a game can be running and we might want to reset the game conditions without having to re-instantiate the object.

   For NumberGuesser, in the `__init__` method we change the expected data type of the goal which would be the target number for that particular instance of `Driver`.

   ```python
   class NumberGuesserDriver(Driver):
       def __init__(
           self,
           goal: str,
       ):
           super().__init__(goal, metrics_class=NumberGuesserMetrics)
   ```

2. `reset()` method

   Let’s go to the `reset` method. A reset method is expected to initialize the game conditions, set the `self.current_state` attribute and return an **_Observation_** object. This observation object will be the first communication from the game to the agent. Hence usually, it consists of the rules of the game and explanation about initial state of the game.

   ```python
   class NumberGuesserDriver(Driver):
       ...

       def reset(self) -> NumberGuesserObservation:
           super().reset()
           self.current_state = NumberGuesserState(value="0")
           return NumberGuesserObservation(
               output=(
                   "Welcome to number guessing game. Your goal is to guess the integer number.\n"
                   "On each guess, you shall be provided the information if the actual number is greater or smaller than the guess.\n"
                   "Based on the feedback, correct your guess.\n"
                   "Make a guess.\n"
               ),
               success=False,
               can_proceed=True,
           )
   ```

3. `step()` method

   The `step` method is used to play the game. Usually, it receives an action object from the agent changes the internal state of the game, checks if the goal is completed or game can no longer proceed and returns an **_Observation_** object with information to the agent about the current state of the game.

   ```python
   class NumberGuesserDriver(Driver):
       ...

       def step(self, action: NumberGuesserAction) -> NumberGuesserObservation:
           super().step(action)
           output_str = ""
           self.current_state.value = action.value
           if int(action.value) == int(self.goal):
               output_str += "You have won!!!\n"
               return NumberGuesserObservation(
                   output=output_str, success=True, can_proceed=False
               )

           if int(action.value) > int(self.goal):
               output_str += (
                   "The target number is smaller than the guessed number. Guess again.\n"
               )

           else:
               output_str += (
                   "The target number is greater than the guessed number. Guess again.\n"
               )
           return NumberGuesserObservation(
               output=output_str, success=False, can_proceed=True
           )

   ```

### Step 4: Setting up the Metrics class

So, we have written the logic on how the NumberGuesser game can be played. The dummy `NumberGuesserMetrics` we implemented earlier inherits from Metrics class and is itself sufficient to record the interactions between agent and the benchmark.

Remember, in the `NumberGuesserDriver` class `__init__()` method, we passed metrics class during the super call. This sets a metrics attribute with metrics object for the driver object. This metrics object takes care of recording the interactions (a tuple of Action, State, Observation objects). It also consists of other methods to calculate progress rate, repetition rate and export the metrics data in dictionary.

Although, Metrics class comes with a lot of out of the box functionalities, to calculate progress rate and repetition rate, two methods `similarity_function` and `progress_function` need to implemented by the benchmarks developer. Here is how we would implement these methods for NumberGuesser.

Replace the previous dummy `NumberGuesserMetrics` class with following code.

```python
# driver.py
...
class NumberGuesserMetrics(Metrics):
    def __init__(self, goal: str):
        super().__init__(goal)

    def similarity_function(
        self, action_1: NumberGuesserAction, action_2: NumberGuesserAction
    ):
        if action_1.value == action_2.value:
            return 1
        else:
            return 0

    def progress_function(self, state: NumberGuesserState) -> float | int:
        guess = int(state.value)
        target = int(self.goal)
        if guess == target:
            return 1.0
        # Calculate the difference and asymptotic progress
        diff = abs(target - guess)
        progress = 1 / (1 + math.log1p(diff))
        return progress

```

The basic philosophy in calculating repetition rate, is we want to compare how many actions were repeated. And to do so, we need to check if two actions are similar or not. And that’s what `similarity_function` is supposed to calculate. Its output usually should be a float value from 0 to 1. For NumberGuesser we keep things simple and just compare the values, if they are equal we return 1 and 0 if not.

For progress rate calculation, the idea is we want to quantify how far the game has progressed. So, the obvious input here will be the game state. For NumberGuesser game, we want to see how close a guess number is to the target number. This is done by calculating the logarithm of the difference between target and guess.

_Disclaimer: This algorithm of progress function may not be the most optimal method, but take this as an illustration._

### Step 5. Running the benchmark

Finally, we have everything setup in our driver.py class and we would like to see how it works. Create a new jupyter notebook, example.ipynb and run the following code.

```python
from agentquest.benchmarks.number_guesser import (
    NumberGuesserAction,
    NumberGuesserDriver,
)
import random

goal = str(random.randint(1000, 2000))
print(goal)
```

```python
driver = NumberGuesserDriver(goal=goal)
obs = driver.reset()
print(obs.output)

while not obs.success and obs.can_proceed:
    human_input = input()
    obs = driver.step(NumberGuesserAction(value=human_input))
    print(obs.output)
```

```python
driver.metrics.export(
    repetition_function_kwargs={"theta_a": 1, "num_execution_steps": 10}
)
```

The arguments to the repetition rate calculating function `theta_a` and `num_execution_steps` are sent in the export method call. Then, the repetition rate is calculated based on the formula as explained in the [AgentQuest](https://arxiv.org/pdf/2404.06411) paper. The function is defined in the lib/base_classes.py in the parent `Metrics` class The similarity function used to calculate repetition rate is the one we defined earlier in `NumberGuesserMetrics` class.

Thanks for reading the tutorial and hope this helps you implementing your benchmark in AgentQuest and testing your agents.

**_Enjoy AgentQuesting :)_**
