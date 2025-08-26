import weaviate
from weaviate.classes.init import Auth
from app.config.settings import settings
from app.shared.logger import get_logger

logger = get_logger(__name__)

class WeaviateClient:
    def __init__(self):
        self.client: weaviate.WeaviateAsyncClient | None = None

    async def init_client(self):
        try:
            self.client = weaviate.WeaviateAsyncClient(
                connection_params=weaviate.connect.ConnectionParams.from_params(
                    http_host=settings.weaviate.weav_host,
                    http_secure=False,
                    http_port=settings.weaviate.weav_port,
                    grpc_host=settings.weaviate.weav_host,
                    grpc_port=settings.weaviate.weav_grpc,
                    grpc_secure=False,
                ),
                auth_client_secret=Auth.api_key(settings.weaviate.weav_api_key),
            )
            await self.client.connect()
            ready = await self.client.is_ready()
            logger.info(f"Weaviate client initialized: {ready}")
        except Exception as e:
            logger.error(f"Weaviate client initialization failed: {str(e)}")
            raise

    def get(self) -> weaviate.WeaviateAsyncClient:
        if not self.client:
            raise RuntimeError("Weaviate client not initialized")
        return self.client

    async def close(self):
        if self.client:
            await self.client.close()
            logger.info("Weaviate Client closed")
            self.client = None