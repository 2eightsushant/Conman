from fastapi import FastAPI, Request, HTTPException, status
from fastapi.responses import JSONResponse
from app.schemas.rerank_schema import RerankInput, RerankResponse
from contextlib import asynccontextmanager
from tenacity import retry, stop_after_attempt, wait_exponential
from sentence_transformers import CrossEncoder
# import logging
from app.shared.logger import get_logger

# logging.basicConfig(level=logging.INFO)
logger = get_logger("reranker_app")

@retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=4, max=10))
@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Loading reranker model...")
    app.state.model = CrossEncoder('cross-encoder/ms-marco-MiniLM-L-6-v2')
    logger.info("Model loaded successfully.")
    yield

    #cleanup model
    app.state.model = None
    logger.info("Model cleaned up.")

app = FastAPI(
    title="Custom Reranker API",
    description="Reranks using Cross encoder",
    version="1.0.0",
    lifespan=lifespan
)

@app.post("/rerank", response_model=RerankResponse)
async def rerank(input: RerankInput):
    if not input.text_list:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Input text list is empty")
    try:
        logger.info(f"Received request with {len(input.text_list)} texts")
        score = float(app.state.model.predict(input.text_list)[0]) if app.state.model else 0.0
        return RerankResponse(score=score)

    except Exception as e:
        logger.exception("Reranikng failed")
        raise HTTPException(status_code=500, detail=str(e))
    

@retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=4, max=10))
@app.get("/health", status_code=status.HTTP_200_OK)
async def health():
    """Check if the reranker model is live or not"""
    try:
        _ = app.state.model.predict(["ping","ping"])
        return {
            "status_ok": True,
            "model_name": "cross-encoder/ms-marco-MiniLM-L-6-v2"
        }
    except Exception as e:
        logger.error(f"Health check failed: {str(e)}")
        raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail="Model down")
