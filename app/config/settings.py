from .development import DevelopmentSettings
from pathlib import Path
from typing import Dict, Type, Union, Literal
from pydantic_settings import BaseSettings

class EnvSettings(BaseSettings):
    env: Literal["development", "production"] = "development"

    model_config = {
        "env_file": str(Path(__file__).resolve().parents[2] / ".env"),
        "env_file_encoding": "utf-8",
        "extra": "ignore"
    }

# Registry of environment configurations
CONFIG_REGISTRY: Dict[str, Type[DevelopmentSettings]] = {
    "development": DevelopmentSettings,
}

def get_settings() -> DevelopmentSettings:
    env_settings = EnvSettings(env='development')
    env = env_settings.env.lower()

    config_class = CONFIG_REGISTRY.get(env)
    if not config_class:
        raise ValueError(f"Invalid environment: {env}. Supported: {list(CONFIG_REGISTRY.keys())}")
    
    return config_class()

settings = get_settings()