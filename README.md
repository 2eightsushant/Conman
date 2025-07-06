### A chat app with context management powered by RAG.

1st modification:
- Configured pydantic environment variable resolver

2nd modification:
- Configured Alembic with async support
- Configured database connections/sessions and engine
- Created database models [user, chatmessage, chatsession]
- Tested and migrated on dockerized postgres