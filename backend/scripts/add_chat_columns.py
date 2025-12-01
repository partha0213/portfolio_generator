import asyncio
import os
import sys

# Add parent directory to path to import backend modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from database import engine
from sqlalchemy import text

async def add_columns():
    print("🔄 Adding columns to chat_history table...")
    
    async with engine.begin() as conn:
        # Check if columns exist first to avoid errors
        try:
            # Add thought column
            await conn.execute(text("ALTER TABLE chat_history ADD COLUMN IF NOT EXISTS thought TEXT;"))
            print("✅ Added 'thought' column")
            
            # Add file_changes column
            await conn.execute(text("ALTER TABLE chat_history ADD COLUMN IF NOT EXISTS file_changes JSON;"))
            print("✅ Added 'file_changes' column")
            
        except Exception as e:
            print(f"❌ Error adding columns: {e}")

if __name__ == "__main__":
    asyncio.run(add_columns())
