# test_retrieval.py

import pytest
from unittest.mock import MagicMock, patch
from datetime import datetime, timedelta
import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from app.core.strategy.memory_retriever import retrieve, cognitive_relevance_rerank


@pytest.fixture
def fake_context():
    return {
        "session_id": "session123",
        "emotion": "happy",
        "now": datetime.now(),
        "last_chunk_id": "chunk_001"
    }


@pytest.fixture
def fake_chunks():
    class FakeChunk:
        def __init__(self, i):
            self.properties = {
                "content": f"chunk content {i}",
                "emotions": ["happy"] if i % 2 == 0 else ["sad"],
                "timestamp": [datetime.now() - timedelta(hours=i)],
                "temporal_context": {"prev_chunk_id": f"chunk_00{i-1}"} if i > 0 else {},
                "cognitive_weight": 1.0 if i % 2 == 0 else 0.6,
            }
            self.metadata = MagicMock()
            self.metadata.explain_score = f"explanation_{i}"

    return [FakeChunk(i) for i in range(5)]


def test_cognitive_reranking(fake_chunks, fake_context):
    reranker = MagicMock()
    reranker.predict.return_value = [0.8]  # fixed semantic score

    results = cognitive_relevance_rerank("test query", fake_chunks, fake_context, reranker)

    assert len(results) == 5
    assert all(isinstance(score, float) and props for score, props, meta in results)


@patch("app.core.retrieval.memory_retriever.EmbeddingFactory.get_embedding_model")
@patch("app.core.retrieval.memory_retriever.RerankerFactory.get_reranker_model")
@patch("app.core.retrieval.memory_retriever.WeaviateClient")
def test_retrieve_success(mock_weaviate_client, mock_reranker_factory, mock_embed_factory, fake_context, fake_chunks):
    # Setup mocks
    mock_embed_model = MagicMock()
    mock_embed_model.encode.return_value = [0.1] * 768
    mock_embed_factory.return_value = mock_embed_model

    mock_reranker = MagicMock()
    mock_reranker.predict.return_value = [0.9]
    mock_reranker_factory.return_value = mock_reranker

    mock_client = MagicMock()
    mock_collection = MagicMock()
    mock_collection.query.hybrid.return_value.objects = fake_chunks
    mock_client.collections.get.return_value = mock_collection

    mock_wrapper = MagicMock()
    mock_wrapper.get.return_value = mock_client
    mock_weaviate_client.return_value = mock_wrapper

    result = retrieve("what did we talk about yesterday?", fake_context)

    assert "top_chunks" in result
    assert len(result["top_chunks"]) > 0
    assert "emotion_groups" in result
    assert "retrieval_metrics" in result
    assert result["retrieval_metrics"]["retention_period"] == "10 days"


@patch("app.core.retrieval.memory_retriever.WeaviateClient")
def test_retrieve_missing_context(mock_weaviate_client):
    result = retrieve("test query", {"emotion": "happy"})
    assert result["error"] == "Insufficient context"
    mock_weaviate_client.assert_not_called()