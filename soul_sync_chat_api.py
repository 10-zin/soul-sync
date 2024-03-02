from fastapi import FastAPI, HTTPException, Depends
from pydantic import BaseModel
import asyncpg
from datetime import datetime
from openai import OpenAI
import uuid
import os

from dotenv import load_dotenv

load_dotenv()

# Database connection parameters
DB_HOST = os.getenv("DB_HOST")
DB_NAME = os.getenv("DB_NAME")
DB_USER = os.getenv("DB_USER")
DB_PASSWORD = os.getenv("DB_PASSWORD")
USER_AI="user000"
INIT_AI_PROMPT="Yo yO this is YouR AiWinMannn! LetS finD people to have fun with. What do you feel like doing today?"
# System prompt to initialize the conversation context
SYSTEM_PROMPT = "The following is a conversation with an AI assistant. The assistant is helpful, creative, clever, and very friendly."

# OpenAI API key
oai_key = os.getenv("OPENAI_API_KEY")

app = FastAPI()

# Initialize database connection pool
db_pool = None

@app.on_event("startup")
async def startup_event():
    global db_pool
    db_pool = await asyncpg.create_pool(
        user=DB_USER, password=DB_PASSWORD, database=DB_NAME, host=DB_HOST
    )

    app.oai_client = OpenAI(
        # This is the default and can be omitted
        api_key=oai_key,
    )


# Dependency to get the database pool
async def get_db_pool():
    return db_pool

# Pydantic model for chat message
class ChatMessage(BaseModel):
    text_message: str
    from_id: str
    to_id: str

# Endpoint to receive a chat message
@app.post("/soul_sync/ai_wingman_chat/")
async def chat(message: ChatMessage, pool: asyncpg.Pool = Depends(get_db_pool)):
    # Create a unique message ID and get the current time
    message_id = str(uuid.uuid4())
    current_time = datetime.now()

    # Insert the new message into the database
    async with pool.acquire() as conn:
        async with conn.transaction():
            await conn.execute(
                """INSERT INTO chat_messages (message_id, text_message, from_id, to_id, time)
                  VALUES ($1, $2, $3, $4, $5)""",
                message_id,
                message.text_message,
                message.from_id,
                message.to_id,
                current_time,
            )

            # Retrieve all previous messages between the two IDs
            messages = await conn.fetch(
                """
                SELECT text_message, from_id FROM chat_messages
                WHERE (from_id = $1 AND to_id = $2) OR (from_id = $3 AND to_id = $4)
                ORDER BY time ASC""",
                message.from_id,
                message.to_id,
                message.to_id,
                message.from_id,
            )

    oai_conv_history =  [{"role": "system", "content": SYSTEM_PROMPT}] + \
                        [{"role": "assistant", "content": INIT_AI_PROMPT}] + \
                        [
                            {
                                "role": "assistant" if msg["from_id"] == USER_AI else "user",
                                "content": msg["text_message"],
                            }
                            for msg in messages
                        ]

    # print(oai_conv_history)

    # Send the prompt to the ChatGPT API
    response = app.oai_client.chat.completions.create(
        messages=oai_conv_history, model="gpt-3.5-turbo"
    )

    # Extract the text from the response
    gpt_response = response.choices[0].message.content

    # Insert the AI response into the database
    ai_message_id = str(uuid.uuid4())
    async with pool.acquire() as conn:
        async with conn.transaction():
            await conn.execute(
                """INSERT INTO chat_messages (message_id, text_message, from_id, to_id, time)
                  VALUES ($1, $2, $3, $4, $5)""",
                ai_message_id,
                gpt_response,
                message.to_id,
                message.from_id,
                datetime.now(),
            )

    # Return the AI response
    return {
        "message_id": ai_message_id,
        "text_message": gpt_response,
        "from_id": "AI",
        "to_id": message.from_id,
        "time": datetime.now(),
    }
