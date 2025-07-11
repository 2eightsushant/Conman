import weaviate.classes as wvc
from weaviate import WeaviateClient
from app.config.settings import settings
from app.shared.logger import get_logger

logger = get_logger(__name__)

class DialogMemorySchema:
    def __init__(self, bm25b=0.7, bm25k1=1.25):
        self.bm25b = bm25b
        self.bm25k1 = bm25k1
        self.collection_object = None
        self.collection_name = settings.weaviate.weav_collection

    def initialize_schema(self, client: WeaviateClient)->None:
            try:
                if client.collections.exists(self.collection_name):
                    logger.info(f"Collection already initialized: {self.collection_name}")
                
                else:
                    self.collection_object = client.collections.create(
                        name=self.collection_name,
                        description="Dialog-centric episodic memory chunks with turn-taking, emotions, and temporal structure.",
                        vectorizer_config=wvc.config.Configure.Vectorizer.none(),
                        vector_index_config=wvc.config.Configure.VectorIndex.hnsw(),
                        properties=[
                            wvc.config.Property(
                                name="chunk_id",
                                data_type=wvc.config.DataType.TEXT,
                                description="Unique chunk ID in session_position format"
                            ),
                            wvc.config.Property(
                                name="session_id",
                                data_type=wvc.config.DataType.UUID,
                                description="Session UUID grouping dialog chunks",
                                index_filterable=True
                            ),
                            wvc.config.Property(
                                name="username",
                                data_type=wvc.config.DataType.TEXT_ARRAY,
                                description="Names of users in this chunk",
                                index_filterable=True
                            ),
                            wvc.config.Property(
                                name="speakers",
                                data_type=wvc.config.DataType.TEXT_ARRAY,
                                description="Set of speaker roles in this chunk",
                                index_filterable=True
                            ),
                            wvc.config.Property(
                                name="content",
                                data_type=wvc.config.DataType.TEXT,
                                description="Concatenated dialog between user and assistant",
                                tokenization=wvc.config.Tokenization.WORD,
                                index_searchable=True
                            ),
                            wvc.config.Property(
                                name="emotions",
                                data_type=wvc.config.DataType.TEXT_ARRAY,
                                description="Top-k detected emotion labels",
                                index_filterable=True
                            ),
                            wvc.config.Property(
                                name="timestamp",
                                data_type=wvc.config.DataType.DATE_ARRAY,
                                description="Timestamps for each message in the chunk",
                                index_filterable=True
                            ),
                            wvc.config.Property(
                                name="temporal_context",
                                data_type=wvc.config.DataType.OBJECT,
                                description="Conversation flow metadata",
                                nested_properties=[
                                    wvc.config.Property(
                                        name="start_index",
                                        data_type=wvc.config.DataType.INT,
                                        description="Start message index of the chunk"
                                    ),
                                    wvc.config.Property(
                                        name="end_index",
                                        data_type=wvc.config.DataType.INT,
                                        description="End message index of the chunk"
                                    ),
                                    wvc.config.Property(
                                        name="session_position",
                                        data_type=wvc.config.DataType.INT_ARRAY,
                                        description="List of message positions in the session",
                                        index_filterable=True
                                    ),
                                    wvc.config.Property(
                                        name="message_indices",
                                        data_type=wvc.config.DataType.INT_ARRAY,
                                        description="List of message positions in the chunk"
                                    ),
                                    wvc.config.Property(
                                        name="prev_chunk_id",
                                        data_type=wvc.config.DataType.TEXT,
                                        description="ID of previous memory chunk (for sequential traversal)"
                                    ),
                                    wvc.config.Property(
                                        name="time_span_seconds",
                                        data_type=wvc.config.DataType.NUMBER_ARRAY,
                                        description="Total time span between the messages",
                                        index_filterable=True
                                    )
                                ],
                                index_filterable=True
                            ),
                        ],
                        inverted_index_config=wvc.config.Configure.inverted_index(
                            bm25_b=self.bm25b,
                            bm25_k1=self.bm25k1,
                            index_null_state=True,
                            index_property_length=True,
                            index_timestamps=True,
                            stopwords_preset=wvc.config.StopwordsPreset.EN
                        )
                    )
                    logger.info(f"Collection successfully created: {self.collection_name}")

            except Exception as e:
                logger.error(f"Collection initialization failed for : {self.collection_name}, error: {str(e)}")
                raise