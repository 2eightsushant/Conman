from sqlalchemy.orm import Session
from app.conn.localsession import SessionLocal
from app.db.models import User, ChatSession, ChatMessage
from app.db.models.chatmessage import MessageRole
import uuid

def insert_dummy_data():
    db: Session = SessionLocal()

    try:
        # Create a user
        user = User(
            id=uuid.uuid4(),
            name="John Doe",
            email="john@example.com",
            username="johndoe",
            api_key="test-api-key"
        )
        db.add(user)
        db.flush()

        # Create a session
        session = ChatSession(
            id=uuid.uuid4(),
            user_id=user.id
        )
        db.add(session)
        db.flush()

        # Add messages
        messages = [
            ChatMessage(
                id=uuid.uuid4(),
                session_id=session.id,
                role=MessageRole.USER,
                content="Hello, who are you?",
                position=1
            ),
            ChatMessage(
                id=uuid.uuid4(),
                session_id=session.id,
                role=MessageRole.ASSISTANT,
                content="I'm a helpful assistant!",
                position=1
            ),
            ChatMessage(
                id=uuid.uuid4(),
                session_id=session.id,
                role=MessageRole.USER,
                content="Tell me about RAG.",
                position=2
            ),
            ChatMessage(
                id=uuid.uuid4(),
                session_id=session.id,
                role=MessageRole.ASSISTANT,
                content="RAG stands for Retrieval-Augmented Generation...",
                position=2
            ),
        ]
        db.add_all(messages)
        db.commit()
        print("Dummy data inserted.")

    except Exception as e:
        db.rollback()
        print("Error:", e)

    finally:
        db.close()

if __name__ == "__main__":
    insert_dummy_data()