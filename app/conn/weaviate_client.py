import weaviate
from weaviate.classes.init import Auth
from app.config.settings import settings
from app.shared.logger import get_logger

logger = get_logger(__name__)

class WeaviateClient:
    def __init__(self):
        self.client = None

    def init_client(self):
        try:
            self.client = weaviate.connect_to_local(
                host=settings.weaviate.weav_host,
                port=settings.weaviate.weav_port,
                grpc_port=settings.weaviate.weav_grpc,
                auth_credentials=Auth.api_key(settings.weaviate.weav_api_key)
            )
            logger.info(f"Weaviate client initialized: {self.client.is_ready()}")
        except Exception as e:
            logger.error(f"Weaviate client initialization failed: {str(e)}")
            raise

    def get(self) -> weaviate.Client:
        if not self.client:
            logger.info("Weaviate client not initialized")
            raise RuntimeError("Weaviate client not initialized")
        return self.client

    def close(self):
        self.client.close()
        logger.info("Weaviate Client closed")
        self.client = None
