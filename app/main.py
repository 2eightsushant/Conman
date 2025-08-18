from fastapi import FastAPI, HTTPException, status
from app.config.settings import settings
from app.conn.clients import post_json, get_json
from app.shared.logger import get_logger

logger = get_logger(__name__)

vectorizer_url = "http://127.0.0.1:8080"
reranker_url = "http://127.0.0.1:8081"
emotion_url = "http://127.0.0.1:8082"

main = FastAPI(title=settings.app_name)

logger.info("Starting app")

@main.get("/health")
async def health_root():
    return {"status": "ok"}

@main.get("/deep-health")
async def deep_health():
    try:
        v = await get_json(f"{vectorizer_url}/health")
        r = await get_json(f"{reranker_url}/health")
        e = await get_json(f"{emotion_url}/health")
        return {"vectorizer":v, "reranker": r, "emotion": e}
    except Exception as e:
        logger.info(f"Exception:{e}")
        raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail=f"dependency_down: {e}")