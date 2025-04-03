from termcolor import cprint

from agentquest.drivers.alfworld import AlfWorldDriver
from agentquest.utils import Action, load_data

# Select a generic AlfWorld pick_and_place game
game = load_data("alfworld", "pick_and_place")[0]

# Initialize mastermind driver````
driver = AlfWorldDriver(game)
obs = driver.reset()  # Get the first observation
cprint(obs.output, "cyan")

while not obs.done:
    action = input("Provide action:\n")
    obs = driver.step(Action(action_value=action))
    cprint(obs.output, "cyan")
