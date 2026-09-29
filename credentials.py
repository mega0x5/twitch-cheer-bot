import os
from typing import Optional, List
from dotenv import load_dotenv

load_dotenv()

API_HOST: Optional[str] = os.getenv("API_HOST")
TOKEN: Optional[str] = os.getenv("TOKEN")
PORT: Optional[str] = os.getenv("PORT")
CHROME_PATH: Optional[str] = os.getenv("CHROME_PATH")
DEBUG_USERS: Optional[str] = os.getenv("DEBUG_USERS")

if DEBUG_USERS:
    DEBUG_USERS_LIST: List[str] = DEBUG_USERS.split(",")
else:
    DEBUG_USERS_LIST: List[str] = []

DEBUG_MODE: bool = os.getenv("DEBUG_MODE") == "True"
