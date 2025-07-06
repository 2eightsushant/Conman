from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import os

# Replace with your actual database URL
DATABASE_URL = os.getenv("DATABASE_URL", "postgresql+psycopg2://conman:conman123@localhost:5432/conman_db")

engine = create_engine(DATABASE_URL)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)