from fastapi import FastAPI, HTTPException, status
from app.config.settings import settings
from app.conn.clients import post_json, get_json
from app.shared.logger import get_logger
from contextlib import asynccontextmanager
from app.conn.weaviate_client import WeaviateClient
from app.core.strategy.memory_retriever import retrieve
from app.schemas.inference_schema import InferenceQuery
from app.core.strategy.memory_formatter import MemoryFormatter
from app.core.factory.tools.recall_memories import recallMemory
from app.core.weaviate.schema import DialogMemorySchema
from app.core.strategy.recall import infer
from app.data_pipeline.insert_to_db import insert_chat
from app.data_pipeline.ingestMessage import ingest_ready_messages
import httpx
import asyncio
import time
import uuid

logger = get_logger(__name__)

vectorizer_url = "http://127.0.0.1:8083"
reranker_url = "http://127.0.0.1:8081"
emotion_url = "http://127.0.0.1:8082"
ollama_url = "http://localhost:11434/api/tags"

@asynccontextmanager
async def lifespan(app: FastAPI):
    app.state.client = httpx.AsyncClient()
    wc = WeaviateClient()
    await wc.init_client()
    app.state.weaviate_client = wc.get()
    await DialogMemorySchema().initialize_schema(app.state.weaviate_client)

    app.state.recall_tool = recallMemory()
    logger.info("Main client initialized")
    
    yield
    
    await app.state.client.aclose()
    await wc.close()
    app.state.recall_tool = None
    logger.info("Main client closed")

main = FastAPI(title=settings.app_name, lifespan=lifespan)

logger.info("Starting app")

@main.get("/health")
async def health_root():
    return {"status": "ok"}

@main.get("/deep-health")
async def deep_health():
    try:
        v, r, e, o = await asyncio.gather(
            get_json(main.state.client, f"{vectorizer_url}/health"),
            get_json(main.state.client, f"{reranker_url}/health"),
            get_json(main.state.client, f"{emotion_url}/health"),
            get_json(main.state.client, f"{ollama_url}")
        )
        models = o.get("models", [])
        if any(model["name"] == "llama3.2:3b" for model in models):
            return {"vectorizer":v, "reranker": r, "emotion": e, "ollama": models}
        else:
            return {"vectorizer":v, "reranker": r, "emotion": e, "ollama": "Ollama server not reachable"}
        
    except Exception as e:
        logger.info(f"Exception:{e}")
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE, 
            detail=f"dependency_down: {e}"
            )
        
@main.post("/inference")
async def inference_endpoint(input: InferenceQuery):
    try:
        session_id = "78774669-bb58-4f76-963b-507e77c82f4e"
        logger.info("Inference started")
        query = input.query
        t1 = time.time()
        response = await infer(
            user_query=query, 
            weaviate_client=main.state.weaviate_client,
            http_client=main.state.client,
            tools=main.state.recall_tool,
            session_id=session_id
        )
        response =response["answer"]
        # query = "What is my name ?"
        # response = "Your name is Sushant Shrestha."
        t2 = time.time()
        logger.info(f"Inference completed in {t2-t1:.2f} seconds")
        
        try:
            await insert_chat(query=query, response=response, session_id=uuid.UUID(session_id))
            await ingest_ready_messages(
                session_id=uuid.UUID(session_id), 
                client=main.state.weaviate_client,
                http_client=main.state.client
            )
            logger.info("Chat ingestion successfull!")
        except Exception as e:
            logger.info(f"Chat ingestion unsucessfull! {e}")
        
        return {
            "query": query,
            "retrieved": response,
            "total time taken (sec)": round(t2-t1)
        }

    except Exception as e:
        logger.exception("Inference pipeline failed")
        raise HTTPException(status_code=500, detail=str(e))