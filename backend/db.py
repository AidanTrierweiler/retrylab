import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

DB_FILENAME = os.getenv("RETRYLAB_DB", "retrylab.db")
DATABASE_URL = f"sqlite:///./{DB_FILENAME}"

engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False},
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()
