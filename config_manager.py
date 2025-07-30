import json
import os

CONFIG_PATH = os.path.join(os.path.dirname(__file__), "config.json")

def save_config_var(key, value, config_path=CONFIG_PATH):
    try:
        with open(config_path, "r") as f:
            config = json.load(f)
    except FileNotFoundError:
        config = {}

    config[key] = int(value)

    with open(config_path, "w") as f:
        json.dump(config, f, indent=2)
