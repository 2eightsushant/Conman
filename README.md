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
