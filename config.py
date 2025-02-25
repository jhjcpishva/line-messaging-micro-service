import os
from os.path import join, dirname
from dotenv import load_dotenv


dotenv_path = join(dirname(__file__), os.getenv("DOTENV", '.env'))
load_dotenv(dotenv_path)

S3_STORAGE_HOST = os.getenv("S3_STORAGE_HOST").strip()
S3_STORAGE_ACCESS_KEY = os.getenv("S3_STORAGE_ACCESS_KEY").strip()
S3_STORAGE_SECRET_KEY = os.getenv("S3_STORAGE_SECRET_KEY").strip()
S3_STORAGE_SECURE = os.getenv("S3_STORAGE_SECURE", "false").strip().lower() == 'true'
S3_STORAGE_BUCKET_NAME = os.getenv("S3_STORAGE_BUCKET_NAME").strip()
S3_STORAGE_PUBLIC_URL = os.getenv("S3_STORAGE_PUBLIC_URL", "").rstrip('/')

AIVIS_SPEECH_FAST_API_URL = os.getenv("AIVIS_SPEECH_FAST_API_URL").rstrip('/')

LINE_CHANNEL_ACCESS_TOKEN = os.getenv("LINE_CHANNEL_ACCESS_TOKEN", "")
LINE_CHANNEL_SECRET = os.getenv("LINE_CHANNEL_SECRET", "")

PORT = int(os.getenv("APP_PORT", "8000"))
CONTEXT_PATH = os.getenv("CONTEXT_PATH", "/")
