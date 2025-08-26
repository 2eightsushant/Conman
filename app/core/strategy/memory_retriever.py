import numpy as np
from weaviate.classes.query import Filter
from weaviate import WeaviateAsyncClient
from httpx import AsyncClient
from weaviate.classes.query import HybridFusion
from app.core.strategy.congnitive_reranker import cognitive_relevance_rerank
from app.core.strategy.memory_formatter import MemoryFormatter
from app.core.strategy.memory_sim import apply_memory_effects
from app.conn.clients import post_json
from app.shared.logger import get_logger

vectorizer_url = "http://127.0.0.1:8083/vectorize"

logger = get_logger(__name__)

MEMORY_RETENTION_DAYS = 10

async def retrieve(weaviate_client: WeaviateAsyncClient, http_client: AsyncClient, query: str, context: dict, top_k: int = 10) -> dict:
    required_context = ['session_id', 'emotion']
    if any(key not in context for key in required_context):
        logger.error(f"Missing context: {required_context}")
        return {"error": "Insufficient context"}
        
    try:
        async with weaviate_client as client:
            collection = client.collections.get("DialogMemory")
            
            vector_resp = await post_json(http_client, vectorizer_url, {"text": [query]})
            vector = vector_resp["vector"][0]
            filters = (
                Filter.by_property("session_id").equal(context['session_id']) 
                # Filter.by_property("emotions").contains_any([context['emotion']])
                # Filter.by_property("timestamp").greater_than(
                #     datetime.now() - timedelta(days=MEMORY_RETENTION_DAYS)
                # )
            )
            response = await collection.query.hybrid(
                query=query,
                vector=vector,
                alpha=0.65,
                limit=top_k,
                query_properties=["content", "emotions"],
                fusion_type=HybridFusion.RELATIVE_SCORE,
                filters=filters,
            )
            
            chunks = response.objects
            if not chunks:
                return {"top_chunks": [], "emotion_groups": {}, "retrieval_metrics": {},"description": "Memory not found"}
            
            reranked = await cognitive_relevance_rerank(query, chunks, context, http_client)
            if not reranked:
                return {"top_chunks": [], "emotion_groups": {}, "retrieval_metrics": {}, "description": "No cognitively relevant memory found"}
            
            emotion_groups = {}
            
            for score, props, meta in reranked[:10]:
                primary_emotion = props.get('emotions', ['neutral'])[0]
                emotion_groups.setdefault(primary_emotion, []).append({
                    "content": props['content'],
                    "score": score,
                    "timestamp": props['timestamp'],
                    "associative_link": props.get('temporal_context', {}).get('prev_chunk_id')
                })
                
            response = {
                "top_chunks": [{
                    "content": props['content'],
                        "cognitive_score": score,
                        "explanation": {
                            "semantic": getattr(meta, "explain_score", None) if context.get("debug") else None,
                            "emotional": props['emotions'],
                            "temporal": max(props['timestamp']).isoformat()
                        }
                } for score, props, meta in reranked[:5]],
                "emotion_groups": emotion_groups,
                "retrieval_metrics": {
                    "initial_candidates": len(chunks),
                    "mean_cognitive_score": np.mean([s for s, _, _ in reranked[:top_k]]).item(),
                    "retention_period": f"{MEMORY_RETENTION_DAYS} days"
                },
                "description": "Memory found",
                "raw_reranked": reranked
            }
            
            #only to mimic human, don't use in production
            # response = apply_memory_effects(response, context)
            return response

    
    except Exception as e:
        logger.error(f"Retrieval failed: {str(e)}")
        return {"error": str(e), "top_chunks": [], "emotion_groups": {}, "retrieval_metrics": {}, "description": "Memory retention error"}
        
#testing
def main():
    query = "I’ve been thinking about how I used to enjoy things more. Did I talk about that before ?"
    context = {"session_id":"a4a33e50-c3ec-4672-b806-1c8ed51ad6d1", "emotion":"neutral"}
    response = retrieve(query, context, top_k=3)
    formatter = MemoryFormatter(include_metadata=True, readable_time=True)
    formatted = formatter.format(reranked_chunks=response["raw_reranked"], limit=3)
    print(formatted)
    
if __name__== "__main__":
    main()