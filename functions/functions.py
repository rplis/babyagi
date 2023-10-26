"""Functions for the main script."""
import yaml
from colorama import Fore, Style


def load_config(config_path: str = "config.yaml") -> dict:
    """Load YAML config file."""
    try:
        with open(config_path, "r", encoding="utf-8") as f:
            config = yaml.safe_load(f)
    except FileNotFoundError as exc:
        print(f"The specified YAML file could not be found: {exc}")
    except yaml.YAMLError as exc:
        print(f"Error in YAML file: {exc}")

    return config


def print_in_color(text: str, color: str = "WHITE") -> None:
    """Print text in color."""
    colors = {
        "BLACK": Fore.BLACK,
        "BLUE": Fore.BLUE,
        "CYAN": Fore.CYAN,
        "GREEN": Fore.GREEN,
        "MAGENTA": Fore.MAGENTA,
        "RED": Fore.RED,
        "YELLOW": Fore.YELLOW,
    }
    color = color.upper()

    if color not in colors:
        color = "WHITE"

    color = colors[color]

    print(f"{color}{Style.BRIGHT}\n*****{text}*****\n{Style.RESET_ALL}")
