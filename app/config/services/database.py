from pydantic_settings import BaseSettings
from pathlib import Path

class DatabaseSettings(BaseSettings):
    database_host: str
    database_port: int
    database_user: str
    database_pass: str
    database_db: str
    database_url: str

    model_config = {
        "env_file": str(Path(__file__).resolve().parents[3] / ".env"),
        "env_prefix": "DEV_",
        "env_file_encoding": "utf-8",
        "extra": "ignore"
    }