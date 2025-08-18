from fastapi import FastAPI, Request, HTTPException, status
from fastapi.responses import JSONResponse
from app.schemas.emotion_schema import EmotionInput, EmotionResponse
from contextlib import asynccontextmanager
from tenacity import retry, stop_after_attempt, wait_exponential
from optimum.onnxruntime import ORTModelForSequenceClassification
from app.data_pipeline.helper.helperOnnx import OnnxPipeline
from functools import lru_cache
from typing import List
# import logging
from app.shared.logger import get_logger

# logging.basicConfig(level=logging.INFO)
logger = get_logger("emotion_app")

@retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=4, max=10))
@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Loading emotion model...")
    app.state.model = ORTModelForSequenceClassification.from_pretrained(
            "SamLowe/roberta-base-go_emotions-onnx",
            subfolder="onnx",
            file_name="model_quantized.onnx"
        )
    pipe = OnnxPipeline()
    pipe.init_pipeline(model=app.state.model)
    app.state.pipeline = pipe.get()
    
    logger.info("Model loaded successfully.")
    yield

    #cleanup model
    app.state.model = None
    logger.info("Model cleaned up.")

app = FastAPI(
    title="Custom emotions model API",
    description="Scores the emotions of the query",
    version="1.0.0",
    lifespan=lifespan
)

@lru_cache(maxsize=1024)
def get_emotions(text: str, k: int = 2) -> List[str]:
    """
    Predicts the top-k emotions from a given string using ONNX-optimized RoBERTa.
    Caches results for repeated text inputs.
    """
    onnx_classifier = app.state.pipeline
    result = onnx_classifier(text)
    top_k = sorted(result[0], key=lambda x: x["score"], reverse=True)[:k]
    return [label["label"] for label in top_k]

@app.post("/emotion-score", response_model=EmotionResponse)
async def emotion_score(input: EmotionInput):
    if not input.text:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Input text is empty")
    try:
        logger.info(f"Received request with {len(input.text)} chars")
        emotions = get_emotions(text=input.text)
        return EmotionResponse(emotions=emotions)

    except Exception as e:
        logger.exception("Vectorization failed")
        raise HTTPException(status_code=500, detail=str(e))
    

@retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=4, max=10))
@app.get("/health", status_code=status.HTTP_200_OK)
async def health(request: Request):
    model = request.app.state.model
    try:
        onnx_classifier = app.state.pipeline
        _ = onnx_classifier("ping")
        return {
            "status_ok": True,
            "model_name": "SamLowe/roberta-base-go_emotions-onnx"
        }
    except Exception as e:
        logger.error(f"Emotion health check failed: {e}")
        raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail=e)

@app.get("/health/liveness")
async def liveness():
    return {"alive": True}
