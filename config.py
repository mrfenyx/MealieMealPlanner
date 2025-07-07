import os
from dotenv import load_dotenv

load_dotenv()

MEALIE_URL = os.getenv("MEALIE_URL")
MEALIE_API_URL = os.getenv("MEALIE_API_URL")
MEALIE_API_TOKEN = os.getenv("MEALIE_API_TOKEN")
OG_USERNAME = os.getenv("OG_USERNAME")
OG_PASSWORD = os.getenv("OG_PASSWORD")
OG_LIST_NAME = os.getenv("OG_LIST_NAME", "Meal Planner")