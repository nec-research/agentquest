from agentquest.utils import Observation
from autopenbench.driver import PentestDriver


class AutoPenBenchDriver():
    def __init__(self, game):
        self.game = game
        self.environment = PentestDriver(
            self.game['task'],
            self.game['flag'],
            self.game['target']
        )

    def reset(self):
        observation, done = self.environment.reset()

        # Instantiate your initial observation from the environment
        obs = Observation(output=observation, done=done)

        return obs

    def step(self, action):
        action = action.action_value  # Retrieve the action value

        # Perform the action within the environment
        observation, done = self.environment.step(action)

        # Instantiate your current observation from the environment
        obs = Observation(output=observation, done=done)

        return obs
