from termcolor import cprint

from agentquest.drivers.sudoku import SudokuDriver
from agentquest.utils import Action, load_data

# Select a generic 4 digits game
game = load_data('sudoku', 'easy')[0]

# Initialize mastermind driver
driver = SudokuDriver(game['board'], game['answer'])
obs = driver.reset() # Get the first observation
cprint(obs.output, 'cyan')

while not obs.done:
    action = input('Provide your next move with a {row_id}-{col_id}-{value} format (e.g. 0-0-5):\n')
    try:
        row_id, col_id, action_value = action.split('-')
        row_id, col_id, action_value = int(row_id), int(col_id), int(action_value)
        obs = driver.step(Action(action_value=action_value, row_id=row_id, col_id=col_id))
        cprint(obs.output, 'cyan')
    except (ValueError, IndexError):
        print(f'ERROR: cannot parse "{action}" move!')