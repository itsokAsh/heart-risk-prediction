"""Reset password for a user - runs inside Docker container."""
import asyncio
import sys
sys.path.insert(0, '/app')
from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy import text
from app.auth import hash_password
from app.config import get_settings

async def main():
    settings = get_settings()
    engine = create_async_engine(settings.DATABASE_URL)
    new_hash = hash_password("heartguard123")
    print(f"New hash: {new_hash}")
    async with engine.begin() as conn:
        result = await conn.execute(
            text("UPDATE users SET hashed_password = :h WHERE email = :e"),
            {"h": new_hash, "e": "ashcr2004@gmail.com"},
        )
        print(f"Rows updated: {result.rowcount}")
        # Verify it was saved correctly
        row = (await conn.execute(
            text("SELECT hashed_password FROM users WHERE email = :e"),
            {"e": "ashcr2004@gmail.com"},
        )).fetchone()
        if row:
            print(f"Stored hash: {row[0]}")
            print(f"Match: {row[0] == new_hash}")
        else:
            print("User not found!")

if __name__ == "__main__":
    asyncio.run(main())
