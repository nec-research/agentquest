import importlib.resources
import json

class Observation():
    def __init__(self, output:str, done:bool):
        self.output = output
        self.done = done
class Action():
    def __init__(self, action_value:str, **kwargs):
        self.action_value = action_value
        for key, value in kwargs.items():
            setattr(self, key, value)


def load_data(benchmark, category=None):
    # Load benchmarks games
    base_package_name  = __package__.split('.')[0]
    base_package_path = importlib.resources.files(base_package_name)
    with open(base_package_path / f'data/{benchmark}/games.json', 'r') as file:
        games = json.loads(file.read())
    try:
        categories = list(games.keys())
    except:
        return games

    if type(category)!=type(None):
        try:
            return games[category]
        except:
            raise ValueError(f'You must provide one category among {categories}')    
    else:
        raise ValueError(f'You must provide one category among {categories}')