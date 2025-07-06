import os
from fastapi import FastAPI
from config.settings import settings
import logging
logging.basicConfig(
        level=settings.log_level,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    )

# Load .env file from project root

app = FastAPI(title=settings.app_name)
print(settings.database.database_pass, settings.database.database_url)

@app.get("/")
async def root():
    return {
        "app_name": settings.app_name,
        "database": {
            "host": settings.database.database_host,
            "port": settings.database.database_port,
            "user": settings.database.database_user,
        }
    }