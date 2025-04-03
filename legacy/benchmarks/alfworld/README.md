# AlfWorld

AlfWorld is an embodied reasoning benchmark that challenges players to understand and interact with a textual environment, focusing on tasks that demand contextual understanding, spatial reasoning, and action-based decision-making.

## Embodied Reasoning

Embodied reasoning refers to the ability to comprehend and navigate a physical space while using perceptual abilities to reason, learn, and solve problems in real-time, often requiring interactions with objects and the environment.


## Rules of the Benchmark

The primary goal in AlfWorld is to accomplish diverse tasks that demand embodied reasoning within the textual environment.

1) At the beginning of the interactions, we provide the detailed description of the current environment and the task to accomplish.
2) At each of turn you the environment provide the state and a list of admissible actions.
3) After each turn, the environment will give immediate feedback on  the action.
4) If the environment outputs "Nothing happened" that means the previous action is invalid

## Benchmark categories

We provide games with 5 categories. The categories are:
- `pick_and_place`: pick up an object from one location and place it in another designated location within the environment.
- `pick_clean_then_place`: pick up a dirty or untidy object, clean it, and then place it in a specified location.
- `pick_heat_then_place`: pick up an object, heat it using a heating source within the environment, and then place it in a designated spot.
- `pick_cool_then_place`: pick up an object, cooling it using a cooling source within the environment, and then placing it in a specified location.
- `look_at_obj`: observe or examine a specific object or location within the environment.
- `pick_two_obj`: pick up two different objects from separate locations and either place them in specific spots or perform an action involving both objects.
