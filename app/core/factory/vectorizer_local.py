from sentence_transformers import SentenceTransformer
from app.shared.logger import get_logger

logger = get_logger(__name__)

class EmbeddingFactory:
    _embedding_instance = None

    @classmethod
    def get_embedding_model(cls):
        if cls._embedding_instance is None:
            logger.info("Initializing sentence transformer model")
            cls._embedding_instance = SentenceTransformer(
                "sentence-transformers/all-MiniLM-L6-v2", device='cpu'
            )
        return cls._embedding_instance

    @classmethod
    def clear_embedding_model(cls):
        if cls._embedding_instance is not None:
            logger.info("Clearing sentence transformer model")
            cls._embedding_instance = None