import os
import json
from dotenv import load_dotenv

load_dotenv(override=True)

# Read token/secrets from env
MEALIE_URL = os.getenv("MEALIE_URL")
MEALIE_API_URL = os.getenv("MEALIE_API_URL")
MEALIE_API_TOKEN = os.getenv("MEALIE_API_TOKEN")
OG_USERNAME = os.getenv("OG_USERNAME")
OG_PASSWORD = os.getenv("OG_PASSWORD")
OG_LIST_NAME = os.getenv("OG_LIST_NAME", "Meal Planner")

# Load days from config.json
CONFIG_PATH = os.path.join(os.path.dirname(__file__), "config.json")

try:
    with open(CONFIG_PATH) as f:
        json_config  = json.load(f)
        
except FileNotFoundError:
    json_config  = {}


DAYS_BEFORE = int(json_config.get("DAYS_BEFORE", 0))
DAYS_AFTER = int(json_config.get("DAYS_AFTER", 0))
