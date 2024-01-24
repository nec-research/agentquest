from agentquest.utils import Observation
from collections import Counter

class MasterMindDriver():
    def __init__(self, truth:str):
        self.truth = truth # The game solution
        self.split_truth = [x for x in truth] # Split the solution in digits

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

    def reset(self):
        # Get the length of the solution
        code_len = len(self.split_truth)

        # Instantiate the starting environment status
        obs = Observation(
            output = f'Start guessing the {code_len} digits number.',
            done = False
        )
        
        return obs

    def step(self, action):
        # Retrieve the action value
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