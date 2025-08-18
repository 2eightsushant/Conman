from sentence_transformers import CrossEncoder
from app.shared.logger import get_logger

logger = get_logger(__name__)

class RerankerFactory:
    _reranker_instance = None

    @classmethod
    def get_reranker_model(cls):
        if cls._reranker_instance is None:
            logger.info("Initializing reranker model")
            cls._reranker_instance = CrossEncoder('cross-encoder/ms-marco-MiniLM-L-6-v2')

        return cls._reranker_instance

    @classmethod
    def clear_reranker_model(cls):
        if cls._reranker_instance is not None:
            logger.info("Clearing reranker model")
            cls._reranker_instance = None