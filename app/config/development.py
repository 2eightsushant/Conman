from pydantic_settings import BaseSettings
from config.services.base import BaseAppSettings
from config.services.database import DatabaseSettings
from pathlib import Path
from pydantic import Field

class DevelopmentSettings(BaseAppSettings):
    app: BaseAppSettings = Field(default_factory=BaseAppSettings)
    database: DatabaseSettings = Field(default_factory=DatabaseSettings)
