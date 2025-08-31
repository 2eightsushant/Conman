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

8th modification:
- Developed memory retriever with cognitive reranker, they retrieves and reranks chat memory chunks from Weaviate based on cognitive relevance (semantic, emotional, temporal, associative signals). Optional: memory retention is also integrated
- Uses cross-encoder/ms-marco-MiniLM-L-6-v2 [https://huggingface.co/cross-encoder/ms-marco-MiniLM-L6-v2] reranker served by sentence transformer
- Weights of congitive relevance and score are provided with pydantic env variable settings
- Modified the emotion model to local serve for now

9th modification:
- Developed memory formatter, a way to:
	1.	Use score meaningfully (e.g., as importance or clarity)
	2.	Preserve continuity using prev_chunk_id
	3.	Enhance emotional reasoning by naming emotion + intensity (if available)
	4.	Use structured formatting that LLMs parse well
	5.	Keep output readable, compact, and semantically dense
- Implemented optional human memory like simualation with 
    1.  Primacy / Recency Bias
    2.  Emotional bias amplification
    3.  Fading memories in emotion groups
    4.  Memory characteristics [vividness, coherence, emotional_valence]
 
10th modification:
- Added ollama server of  model llama3.2:3b with docker
- did a tool checking capability
- developed rough recall functionality with initial testing
- inserted little complicated conversation of dummy data


11th modification:
- Moved local loading to local directory
- Developed API with pydantic model for reranker, emotion and vectorizer
- API have lifespan with health and [rerank, get-emotion, vectorize] endpoints
- Created helper function for onnx pipeline of emotion model
- Developed deep health check via main app for all three servers with custom post_json and get_json

12th modification:
- Added inference endpoint that will call recall -> ollama_chat, recall_memories -> retrieve -> vectorizer, reranker
- Modified httpx clients, weaviate_clients, congitive_reranker, memory_retriever to async framework
- Clients have singleton design

13th modification(major change):
- Async db connection
- Modified recall_memories, chunker, formatter, schema, recall, ingestmessage, push to weaviate, helperhead to asynchronous model
- Added insert to db, that will push the conversation to db with each query
- Now instead of one call there will be two calls per chat round, main llm -> tools -> reflector/judge
- Reflector main purpose is to filter irrelevant memories
- Maintained prompts with versioning and yaml registry
- Now weaviate schema initialization have singleton pattern
- Handeled session_id at the endpoint
