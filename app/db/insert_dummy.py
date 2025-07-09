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

def insert_dummy_data2():
    db: Session = SessionLocal()

    try:
        sessionid = uuid.UUID('d025e2b3-8f51-452f-b152-105084c664b2')

        # Example message content (extendable)
        user_prompts = [
            "Explain Python.",
            "How does AI work?",
            "What's the weather today?",
            "Recommend a book.",
            "How to learn fast?",
            "Tell me about deep learning.",
            "What is ChatGPT?",
            "What is machine learning?",
            "How do transformers work?",
            "Best way to start coding?",
            "Tell me a joke.",
            "What's OpenAI?",
            "How does neural networks function?",
            "What's the capital of France?",
            "Give me a productivity tip.",
            "How to stay focused?",
            "Tell me about recursion.",
            "Explain natural language processing.",
            "What are embeddings?",
            "What's the use of vector databases?",
            "How do LLMs use context?",
            "What’s the difference between AI and ML?",
            "Summarize quantum computing."
        ]

        assistant_replies = [
            "Python is a popular programming language for many domains.",
            "AI mimics human intelligence using algorithms and data.",
            "I can't access real-time data, but you can check a weather site.",
            "'Atomic Habits' by James Clear is a great read!",
            "Spaced repetition and active recall help a lot.",
            "Deep learning uses neural networks to model complex patterns.",
            "ChatGPT is a conversational AI developed by OpenAI.",
            "Machine learning lets systems learn from data.",
            "Transformers use self-attention to process sequences.",
            "Start with Python and build small projects!",
            "Why don't scientists trust atoms? Because they make up everything!",
            "OpenAI is an AI research and deployment company.",
            "Neural networks are composed of layers of nodes mimicking neurons.",
            "The capital of France is Paris.",
            "Use the Pomodoro technique: 25 min work, 5 min break.",
            "Eliminate distractions and set clear goals.",
            "Recursion is when a function calls itself.",
            "NLP is how machines understand human language.",
            "Embeddings turn words into vectors that capture meaning.",
            "Vector databases store and search embeddings efficiently.",
            "LLMs use tokens and attention to handle long contexts.",
            "AI is the broader field, ML is a subset of it.",
            "Quantum computing uses quantum bits for processing."
        ]

        messages = []
        for i in range(len(user_prompts)):
            messages.append(ChatMessage(
                id=uuid.uuid4(),
                session_id=sessionid,
                role=MessageRole.USER,
                content=user_prompts[i],
                position=i + 3
            ))
            messages.append(ChatMessage(
                id=uuid.uuid4(),
                session_id=sessionid,
                role=MessageRole.ASSISTANT,
                content=assistant_replies[i],
                position=i + 3
            ))

        db.add_all(messages)
        db.commit()
        print("50 dummy chat messages inserted.")

    except Exception as e:
        db.rollback()
        print("Error:", e)

    finally:
        db.close()

if __name__ == "__main__":
    # insert_dummy_data()
    insert_dummy_data2()