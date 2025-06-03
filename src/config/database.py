from sqlalchemy import create_engine, MetaData
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import declarative_base, Session, sessionmaker
from dotenv import load_dotenv
import os

load_dotenv()

DB_URL = os.getenv("DATABASE_URL")
ASYNC_DB_URL = os.getenv("ASYNC_DATABASE_URL")

engine = create_engine(f"{DB_URL}")
async_engine = create_async_engine(f"{ASYNC_DB_URL}", echo=True)

base = declarative_base() # This is the base class for your models

metadata = MetaData() # This is used to hold the metadata of the database schema

# Session factories for synchronous and asynchronous sessions
SessionLocal = sessionmaker(bind=engine, autocommit=False, autoflush=False, class_=Session) 
AsyncSessionLocal = sessionmaker(bind=async_engine, expire_on_commit=False, class_=AsyncSession)
