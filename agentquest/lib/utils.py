import ast
import pprint
from datetime import datetime
from typing import Any

from termcolor import colored


def cpprint(data: Any, color="white"):
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
