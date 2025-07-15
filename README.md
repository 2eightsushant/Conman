### A chat app with context management powered by RAG.

1st modification:
- Configured pydantic environment variable resolver

2nd modification:
- Configured Alembic with async support
- Configured database connections/sessions and engine
- Created database models [user, chatmessage, chatsession]
- Tested and migrated on dockerized postgres

3rd modification:
- Added [ingestion_head] db model
- Added helper head to get head, update head and update isVectorized
- Added ingestMessage that will later be integrated with Ray. It is still synchronous module.
- Some alembic migration heads

4th modification:
- Added Dialouge centric windowing: 
    - It preserves speaker roles
    - It slides through the full conversation using a fixed-size window maintaining local context
    - It performs implicitly semantic splitting by:
        1. Formatting with roles
        2. Using overlapping context
        3. Anchoring to dialoug turns
- Added emotions metadata implied from: https://huggingface.co/SamLowe/roberta-base-go_emotions-onnx
    - Use ONNX quantized version served by Huggingface ORTModelForSequenceClassification
- Cached the get_emotions method
- Pydantified ingest message process with db models
- Inserted 50 dummy data

5th modification:
- Added weaviate connection manager
- Added weaviate collection with:
    1. Vectorizer = Null + bm25
    2. Vector index = HNSW (default)
    3. Properties and nested properties with index filterable
- Modified chunker: Nested some metadata to temporal_context

6th modification:
- Configured vectorizer: used sentence-transformers/all-MiniLM-L6-v2
- Added both api (docker) and local (dev) instance for vectorizer(embedding model)
- Chunker: Modified timestamp and added UUID on custom id
- Developed chunks to weaviate ingest process aligned with desinged schema
- Modified main ingestMessage flow [Only good for test, have to make it robust]
- Added Dockerfile.vectorizer and integrated on yaml (not optimized)

7th modification:
- Integrated update_head and update_is_vectorized
- Reconfigured message query, had to use joinedload for orm support of foreign columns
- Fixed minor pg_advisory lock/unlock querying bug with text wrapper