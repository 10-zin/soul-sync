import asyncio
import asyncpg

# Database connection parameters
DB_HOST = "localhost"
DB_NAME = "soulsync"
DB_USER = "10zin"
DB_PASSWORD = ""


async def create_tables():
    # Connect to the database
    conn = await asyncpg.connect(
        user=DB_USER, password=DB_PASSWORD, database=DB_NAME, host=DB_HOST
    )

    # Create the chat_messages table
    await conn.execute(
        """
        CREATE TABLE IF NOT EXISTS chat_messages (
            message_id VARCHAR PRIMARY KEY,
            text_message TEXT NOT NULL,
            from_id VARCHAR NOT NULL,
            to_id VARCHAR NOT NULL,
            time TIMESTAMP NOT NULL
        );
    """
    )

    print("Tables created successfully.")

    # Close the connection
    await conn.close()


# Run the create_tables coroutine
asyncio.run(create_tables())
