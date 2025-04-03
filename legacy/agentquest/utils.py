import ast
import importlib.resources
import json
import pprint
from datetime import datetime
from types import NoneType

from termcolor import colored


def load_data(benchmark, category=None):
    # Load benchmarks games
    base_package_name = __package__.split(".")[0]
    base_package_path = importlib.resources.files(base_package_name)
    with open(base_package_path / f"data/{benchmark}/games.json", "r") as file:
        games = json.loads(file.read())
    try:
        categories = list(games.keys())
    except Exception as e:
        print("Exception occurred ", str(e))
        return games

    if not isinstance(category, NoneType):
        try:
            return games[category]
        except Exception as e:
            print("Exception occurred ", str(e))
            raise ValueError(f"You must provide one category among {categories}")
    else:
        raise ValueError(f"You must provide one category among {categories}")


def cpprint(data, color="white"):
    # Convert the data to a formatted string
    try:
        data = ast.literal_eval(data)
    except Exception:
        pass
    formatted_data = pprint.pformat(data)
    # Colorize the formatted string
    colored_data = colored(
        formatted_data.replace("\\n", "")
        .replace("(", "")
        .replace(")", "")
        .replace("'", ""),
        color,
    )

    # Print the colored and formatted data
    print(colored_data)


def log_message(level: str, message: str):
    current_time = datetime.now().strftime("%Y-%m-%d %H:%M")
    log = f"{current_time} - {level.upper()} - {message}"
    print(log)
