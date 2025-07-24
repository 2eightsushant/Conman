import numpy as np
from weaviate.classes.query import Filter
from app.conn.weaviate_client import WeaviateClient
from weaviate.classes.query import HybridFusion
from app.core.factory.vectorizer_local import EmbeddingFactory
from app.core.factory.reranker_local import RerankerFactory
from app.core.strategy.congnitive_reranker import cognitive_relevance_rerank
from app.core.strategy.memory_formatter import MemoryFormatter
from app.core.strategy.memory_sim import apply_memory_effects
from app.shared.logger import get_logger

logger = get_logger(__name__)

MEMORY_RETENTION_DAYS = 10

def retrieve(query: str, context: dict, top_k: int = 10) -> dict:
    required_context = ['session_id', 'emotion']
    if any(key not in context for key in required_context):
        logger.error(f"Missing context: {required_context}")
        return {"error": "Insufficient context"}
    
    weaviate_wrapper = WeaviateClient()
    weaviate_wrapper.init_client()
    
    try:
        with weaviate_wrapper.get() as client:
            collection = client.collections.get("DialogMemory")
            embed_model = EmbeddingFactory.get_embedding_model()
            reranker = RerankerFactory.get_reranker_model()
            
            vector = embed_model.encode(query)
            filters = (
                Filter.by_property("session_id").equal(context['session_id']) &
                Filter.by_property("emotions").contains_any([context['emotion']])
                # Filter.by_property("timestamp").greater_than(
                #     datetime.now() - timedelta(days=MEMORY_RETENTION_DAYS)
                # )
            )
            
            response = collection.query.hybrid(
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
            
            reranked = cognitive_relevance_rerank(query, chunks, context, reranker)
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
    finally:
        weaviate_wrapper.close()
        
#testing
def main():
    query = "Are you aware about AI ?"
    context = {"session_id":"7b859f3f-2882-4394-97f9-0482f14a40c1", "emotion":"neutral"}
    response = retrieve(query, context, top_k=3)
    formatter = MemoryFormatter(include_metadata=True, readable_time=True)
    formatted = formatter.format(reranked_chunks=response["raw_reranked"], limit=3)
    print(formatted)
    
if __name__== "__main__":
    main()