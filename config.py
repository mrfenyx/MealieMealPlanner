import os
from dotenv import load_dotenv

load_dotenv()

MEALIE_URL = os.getenv("MEALIE_URL")
MEALIE_API_TOKEN = os.getenv("MEALIE_API_TOKEN")
