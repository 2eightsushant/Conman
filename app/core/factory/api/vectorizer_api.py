from fastapi import FastAPI, Request, HTTPException, status
from fastapi.responses import JSONResponse
from app.schemas.vectorize_schema import VectorResponse, VectorInput
from contextlib import asynccontextmanager
from tenacity import retry, stop_after_attempt, wait_exponential
from sentence_transformers import SentenceTransformer
# import logging
from app.shared.logger import get_logger

# logging.basicConfig(level=logging.INFO)
logger = get_logger("vectorizer_app")

@retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=4, max=10))
@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Loading embedding model...")
    app.state.model = SentenceTransformer("sentence-transformers/all-MiniLM-L6-v2")
    logger.info("Model loaded successfully.")
    yield

    #cleanup model
    app.state.model = None
    logger.info("Model cleaned up.")

app = FastAPI(
    title="Custom Vectorizer API",
    description="Encodes text into vector representations using SentenceTransformers",
    version="1.0.0",
    lifespan=lifespan
)

@app.post("/vectorize", response_model=VectorResponse)
async def vectorize(input: VectorInput):
    if not input.text:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Input text list is empty")
    try:
        logger.info(f"Received request with {len(input.text)} texts")
        vectors = app.state.model.encode(input.text, convert_to_numpy=True).tolist()
        return VectorResponse(vector=vectors)

    except Exception as e:
        logger.exception("Vectorization failed")
        raise HTTPException(status_code=500, detail=str(e))
    

@retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=4, max=10))
@app.get("/health", status_code=status.HTTP_200_OK)
async def health():
    """Check if the vectorizer model is live or not"""
    try:
        _ = app.state.model.encode(["ping"], convert_to_numpy=True)
        return {
            "status_ok": True,
            "model_name": "sentence-transformers/all-MiniLM-L6-v2"
        }
    except Exception as e:
        logger.error(f"Health check failed: {str(e)}")
        raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail="Model down")
