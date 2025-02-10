import os
from dotenv import load_dotenv

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base


load_dotenv()
DATABASE_URL = os.getenv("URL")

if not DATABASE_URL:
    raise ValueError("❌ DATABASE_URL не знайдено! Перевір змінні середовища.")

DB_USER = "postgres"
DB_HOST = "localhost"
DB_PORT = "5432"
DB_NAME = "mydatabase"



engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()
