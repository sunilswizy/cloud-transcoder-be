from dotenv import load_dotenv
import os

load_dotenv()

UPLOAD_FILE_PATH = os.getenv("UPLOAD_FILE_PATH")
DECODE_FILE_PATH = os.getenv("DECODE_FILE_PATH")
SQS_QUEUE_URL = os.getenv("SQS_QUEUE_URL")
REGION = os.getenv("REGION")

os.makedirs(f"{UPLOAD_FILE_PATH}", exist_ok=True)
os.makedirs(f"{DECODE_FILE_PATH}", exist_ok=True)
