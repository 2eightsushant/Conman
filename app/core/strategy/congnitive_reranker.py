import numpy as np
from typing import Any
from datetime import datetime, timezone
from app.config.settings import settings
from app.shared.logger import get_logger

logger = get_logger(__name__)

COGNITIVE_WEIGHTS = {
    "semantic": settings.cognitive.semantic,
    "emotional": settings.cognitive.emotional,
    "temporal": settings.cognitive.temporal,
    "associative": settings.cognitive.associative
}

def cognitive_relevance_rerank(query: str, chunks: list, current_context: dict, reranker: Any) -> list:
    """Rerank based on human like memory priorities"""
    reranked = []
    for chunk in chunks:
        content = chunk.properties.get('content', '')
        props = getattr(chunk, 'properties', {}) or {}
        meta = getattr(chunk, 'metadata', {}) or {}
        semantic_score = float(reranker.predict([[query, content]])[0]) if reranker else 0.0
        
        emotions = chunk.properties.get('emotions',[])
        emotion_score = settings.cognitive.em_score if current_context['emotion'] in emotions else 1.0
        
        now = datetime.now(timezone.utc)
        timestamp_list = chunk.properties.get('timestamp', [])
        if not isinstance(timestamp_list, list):
            timestamp_list = [timestamp_list] if timestamp_list else []
        latest_timestamp = max(timestamp_list) if timestamp_list else now
        recency = (now - latest_timestamp).total_seconds() / 3600  # hours ago
        recency_score = np.exp(-recency / 24)
        
        temporal_ctx = chunk.properties.get('temporal_context', {})
        continuity_score = settings.cognitive.cont_score if temporal_ctx.get('prev_chunk_id') == current_context.get('last_chunk_id') else 1.0
        
        cognitive_weight = chunk.properties.get('cognitive_weight', 1.0)
        if cognitive_weight > settings.cognitive.weight_thres:
            cognitive_boost = min(1.2, 1.0 + (cognitive_weight - 0.8) * 2)
        else:
            cognitive_boost = 1.0
        
        cognitive_score = (
            COGNITIVE_WEIGHTS["semantic"] * semantic_score +
            COGNITIVE_WEIGHTS["emotional"] * emotion_score +
            COGNITIVE_WEIGHTS["temporal"] * recency_score +
            COGNITIVE_WEIGHTS["associative"] * continuity_score
        ) * cognitive_boost
        
        reranked.append((cognitive_score, props, meta))
    
    return sorted(reranked, key=lambda x: x[0], reverse=True)