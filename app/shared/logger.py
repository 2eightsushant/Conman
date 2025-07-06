import os
import logging
import sys
from app.config.settings import settings

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))  # <- goes one level up
LOG_DIR = os.path.join(BASE_DIR, "logs")
os.makedirs(LOG_DIR, exist_ok=True)

LOG_FILE_PATH = os.path.join(LOG_DIR, "logs.log")

logger = logging.getLogger()
logger.setLevel(settings.log_level)

if not logger.handlers:
    stream_handler = logging.StreamHandler(sys.stdout)
    file_handler = logging.FileHandler(LOG_FILE_PATH, encoding="utf-8", mode="a")
    formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(name)s - %(message)s')
    stream_handler.setFormatter(formatter)
    file_handler.setFormatter(formatter)
    logger.addHandler(stream_handler)
    logger.addHandler(file_handler)

def get_logger(name: str) -> logging.Logger:
    return logging.getLogger(name)