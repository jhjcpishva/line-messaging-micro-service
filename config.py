import os
from os.path import join, dirname
from dotenv import load_dotenv


dotenv_path = join(dirname(__file__), os.getenv("DOTENV", '.env'))
load_dotenv(dotenv_path)

LINE_CHANNEL_ACCESS_TOKEN = os.getenv("LINE_CHANNEL_ACCESS_TOKEN", "")
LINE_CHANNEL_SECRET = os.getenv("LINE_CHANNEL_SECRET", "")

PORT = int(os.getenv("APP_PORT", "8000"))
CONTEXT_PATH = os.getenv("CONTEXT_PATH", "/")
