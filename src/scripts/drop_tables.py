import asyncio
import os
import asyncpg
from dotenv import load_dotenv

load_dotenv()

# Database connection parameters
DB_HOST = os.getenv("DB_HOST")
DB_NAME = os.getenv("DB_NAME")
DB_USER = os.getenv("DB_USER")
DB_PASSWORD = os.getenv("DB_PASSWORD")


async def drop_tables():
    # Connect to the database
    conn = await asyncpg.connect(
        user=DB_USER, password=DB_PASSWORD, database=DB_NAME, host=DB_HOST
    )

    # Drop all tables in the database
    await conn.execute("DROP SCHEMA public CASCADE; CREATE SCHEMA public;")

    print("All tables dropped successfully.")

    # Close the connection
    await conn.close()


# Run the drop_tables coroutine
asyncio.run(drop_tables())
