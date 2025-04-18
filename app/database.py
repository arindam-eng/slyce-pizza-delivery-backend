from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from contextlib import asynccontextmanager

from app.config import settings

# Create the SQLAlchemy engine
engine = create_async_engine(settings.DATABASE_URL)
SessionLocal = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
Base = declarative_base()

@asynccontextmanager
async def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        await db.close()