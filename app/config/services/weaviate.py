from pydantic_settings import BaseSettings
from pathlib import Path

class WeaviateSettings(BaseSettings):
    weav_api_key: str
    weav_host: str
    weav_port: int
    weav_grpc: int
    weav_class: str
    weav_collection: str

    model_config = {
        "env_file": str(Path(__file__).resolve().parents[3] / ".env"),
        "env_file_encoding": "utf-8",
        "env_prefix": "DEV_",
        "extra": "ignore"
    }