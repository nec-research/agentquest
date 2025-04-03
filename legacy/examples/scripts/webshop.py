from pprint import pprint
from termcolor import cprint

from agentquest.drivers.webshop import WebshopDriver
from agentquest.drivers.webshop import webshop_load_data as load_data
from agentquest.utils import Action

# Select a generic webshop goal
goal = load_data()[100]
pprint(goal)

# Initialize webshop driver
driver = WebshopDriver(goal)
obs = driver.reset()  # Get the first observation
cprint(obs.output, "cyan")

while not obs.done and obs.can_proceed:
    action = input("Provide action:\n")
    obs = driver.step(Action(action_value=action))
    cprint(obs.output, "cyan")
