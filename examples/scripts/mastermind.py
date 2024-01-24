from termcolor import cprint

from agentquest.drivers.mastermind import MasterMindDriver
from agentquest.utils import Action, load_data

# Select a generic 4 digits game
game = load_data('mastermind', '4 digits')[0]

# Initialize mastermind driver
driver = MasterMindDriver(game)
obs = driver.reset() # Get the first observation
cprint(obs.output, 'cyan')

while not obs.done:
    action = input('Provide your 4 digit guess:\n')
    obs = driver.step(Action(action_value=action))
    cprint(obs.output, 'cyan')
