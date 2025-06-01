import asyncio
from sqlalchemy.ext.asyncio import create_async_engine
from .database import DATABASE_URL
from .models import Base

async def init_db():
    """Initialize the database"""
    # Create async engine
    engine = create_async_engine(DATABASE_URL, echo=True)
    
    # Create all tables
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)
    
    # Close engine
    await engine.dispose()

if __name__ == "__main__":
    asyncio.run(init_db()) 