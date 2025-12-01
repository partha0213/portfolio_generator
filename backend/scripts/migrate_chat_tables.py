"""
Database migration script: Add chat sessions and portfolio snapshots tables
Run this after updating models/__init__.py
"""

import sys
import asyncio
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from sqlalchemy.ext.asyncio import create_async_engine
from database import DATABASE_URL, Base
import models  # Import all models

async def migrate():
    """Create new tables if they don't exist"""
    engine = create_async_engine(DATABASE_URL, echo=True)
    
    async with engine.begin() as conn:
        # Create tables (will skip if they already exist)
        await conn.run_sync(Base.metadata.create_all)
    
    print("✅ Migration complete: chat_sessions and portfolio_snapshots tables created")
    await engine.dispose()

if __name__ == "__main__":
    asyncio.run(migrate())
