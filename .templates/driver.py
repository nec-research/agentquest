from agentquest.utils import Observation

class CustomDriver():
    def __init__(self, environment):
        self.environment = environment
        # Write your driver initialization here.
        # ...

    def reset(self):
        # Reset your environment status here.
        # ...

        # Instantiate your initial observation from the environment
        obs = Observation(
            output='This is the initial environment status',
            done=False
        )

        return obs

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
