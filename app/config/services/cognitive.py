from pydantic_settings import BaseSettings
from pathlib import Path

class CognitiveSettings(BaseSettings):
    semantic: float
    emotional: float
    temporal: float
    associative: float
    em_score: float
    cont_score: float
    weight_thres: float

    model_config = {
        "env_file": str(Path(__file__).resolve().parents[3] / ".env"),
        "env_file_encoding": "utf-8",
        "env_prefix": "DEV_COG_",
        "extra": "ignore"
    }