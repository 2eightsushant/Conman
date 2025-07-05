from pydantic_settings import BaseSettings
from pathlib import Path

class BaseAppSettings(BaseSettings):
    app_name: str
    log_level: str

    model_config = {
        "env_file": str(Path(__file__).resolve().parents[3] / ".env"),
        "env_file_encoding": "utf-8",
        "extra": "ignore"
    }