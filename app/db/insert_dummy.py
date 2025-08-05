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
        sessionid = uuid.UUID('7b859f3f-2882-4394-97f9-0482f14a40c1')

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
        
def insert_dummy_data4():
    db = SessionLocal()
    sessionid = uuid.uuid4()
    session = ChatSession(
            id=sessionid,
            user_id=uuid.UUID("de23ec99-0b13-4eed-9910-a80b2c65d8c8")
        )
    db.add(session)
    db.flush()

    user_messages = [
        "Hey, I’ve been feeling kind of off lately. Just... overwhelmed, I guess.",
        "Work’s been piling up and I feel like I can’t catch a break.",
        "I tried taking a day off last weekend, but I just ended up worrying about Monday.",
        "Do you ever get that feeling where everything feels like too much, even the small stuff?",
        "Honestly, I’ve been questioning if I’m even in the right job. It’s draining me.",
        "I used to enjoy writing and journaling, but I haven’t touched my notebook in months.",
        "My sleep schedule is a mess. I keep staying up late, doomscrolling or watching random videos.",
        "I don’t really talk about this stuff with my friends. I don’t want to seem like a burden.",
        "Do you think therapy would help someone like me?",
        "I just want to feel like myself again, you know?",
        "Yeah, maybe I should try journaling again. Even if it’s just a few lines before bed.",
        "I’ve been thinking a lot about when I used to feel excited about things... like new projects or even weekend plans.",
        "Lately, everything just feels kind of grey, you know?",
        "I miss being curious, getting lost in ideas or books. Now it’s just deadlines and emails.",
        "I told myself I’d go for a walk this morning, but I snoozed through all my alarms.",
        "I guess I’m scared I’m wasting my life doing something I don’t even care about.",
        "My chest feels tight all the time, like I’m bracing for something bad even when nothing’s wrong.",
        "Some nights I cry and I don’t even know why. Then I wake up and pretend like it didn’t happen.",
        "I hate how fake I feel around people lately, like I’m smiling just so no one asks questions.",
        "I want to make changes… I really do. But I don’t know where to start."
    ]

    assistant_messages = [
        "I’m really sorry to hear that you’re feeling this way. It’s okay to feel overwhelmed sometimes. You’re not alone.",
        "It sounds like you’re under a lot of pressure. Have you been able to set any boundaries around your work time?",
        "That’s a very common experience—taking time off but not truly resting. Your mind is still in work mode.",
        "Yes, I understand. When stress accumulates, even simple tasks can feel like huge mountains.",
        "It’s brave of you to admit that. It might be time to reassess what brings you fulfillment.",
        "Writing and journaling can be powerful tools for clarity. Do you want help setting a simple habit to get back into it?",
        "Sleep plays a huge role in how we process emotion and stress. Want to explore a gentle routine to wind down before bed?",
        "You’re never a burden for expressing your truth. Real friends will want to know how you're doing.",
        "Absolutely. Therapy can be a great space to unpack feelings like these in a supportive environment.",
        "You deserve to feel like yourself again—and taking steps to care for your mental health is a big part of that journey.",
        "That’s a gentle, thoughtful step. Even a few lines can reconnect you with yourself in small but meaningful ways.",
        "Reconnecting with joy is powerful. Maybe reflect on those past moments—what energized you? What mattered to you then?",
        "Yes, emotional numbness can come from prolonged stress. Let’s work on bringing some color back into your days, one small moment at a time.",
        "That spark is still within you. It may just be buried under exhaustion. Curiosity isn’t gone—it’s waiting.",
        "It’s okay to miss a goal. Try again tomorrow, without judgment. Change comes from compassion, not shame.",
        "That’s a real and important realization. You’re not alone in that fear. Let’s explore what ‘meaningful work’ might look like for you.",
        "That tightness is your body holding the weight of your thoughts. Breathing exercises or grounding practices might help—want to try one together?",
        "Those feelings are valid, even if they seem to come from nowhere. Your emotions are speaking—let’s listen, gently.",
        "Masking pain is exhausting. You deserve spaces where you can be authentic and supported.",
        "The desire to change is already a sign of strength. Let’s start small—what’s one thing you could do today that feels kind to yourself?"
    ]

    try:
        messages = []
        for i, (user_msg, assistant_msg) in enumerate(zip(user_messages, assistant_messages)):
            messages.append(ChatMessage(
                id=uuid.uuid4(),
                session_id=sessionid,
                role=MessageRole.USER,
                content=user_msg,
                position=i
            ))
            messages.append(ChatMessage(
                id=uuid.uuid4(),
                session_id=sessionid,
                role=MessageRole.ASSISTANT,
                content=assistant_msg,
                position=i
            ))

        db.add_all(messages)
        db.commit()
        print("Realistic long-form conversation inserted.")
    except Exception as e:
        db.rollback()
        print("Error:", e)
    finally:
        db.close()

if __name__ == "__main__":
    # insert_dummy_data()
    # insert_dummy_data2()
    insert_dummy_data4()