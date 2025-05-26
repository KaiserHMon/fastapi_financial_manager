from sqlalchemy import create_engine, MetaData
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import declarative_base
from dotenv import load_dotenv
import os

load_dotenv()

DB_URL = os.getenv("DATABASE_URL")

engine = create_engine(f"{DB_URL}") # this will be the database URL from your .env file

base = declarative_base() # This is the base class for your models

metadata = MetaData() # This is used to hold the metadata of the database schema
