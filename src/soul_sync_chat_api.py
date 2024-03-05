from fastapi import FastAPI, HTTPException, Depends
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import sessionmaker
from pydantic import BaseModel
import asyncpg
from datetime import datetime
from openai import OpenAI
import uuid
import os
from src.schemas import UserMessage, ChatMessage
from src.data_models import ChatMessageModel

from dotenv import load_dotenv

load_dotenv()

# Database connection parameters
DB_HOST = os.getenv("DB_HOST")
DB_NAME = os.getenv("DB_NAME")
DB_USER = os.getenv("DB_USER")
DB_PASSWORD = os.getenv("DB_PASSWORD")
USER_AI = "user000"
INIT_AI_PROMPT = "Yo yO this is YouR AiWingMannn! LetS finD people to have fun with. What do you feel like doing today?"
# System prompt to initialize the conversation context
SYSTEM_PROMPT = "The following is a conversation with an AI assistant. The assistant is helpful, creative, clever, and very friendly."

# OpenAI API key
oai_key = os.getenv("OPENAI_API_KEY")

app = FastAPI()

# Initialize database connection pool
db_pool = None
AsyncSessionLocal = None


@app.on_event("startup")
async def startup_event():
    global AsyncSessionLocal

    DATABASE_URL = f"postgresql+asyncpg://{DB_USER}:{DB_PASSWORD}@{DB_HOST}/{DB_NAME}"

    engine = create_async_engine(DATABASE_URL, echo=True)
    AsyncSessionLocal = sessionmaker(
        autocommit=False, autoflush=False, bind=engine, class_=AsyncSession
    )

    app.oai_client = OpenAI(
        # This is the default and can be omitted
        api_key=oai_key,
    )


async def get_session() -> AsyncSession:
    async with AsyncSessionLocal() as session:
        yield session


async def _insert_message_in_db(message_id, text_message, from_id, to_id, time, session):
    db_message = ChatMessageModel(
        message_id=message_id,
        text_message=text_message,
        from_id=from_id,
        to_id=to_id,
        time=datetime.now(),
    )
    session.add(db_message)
    await session.commit()


async def _get_user_conversation_history(message, session):
    result = await session.execute(
        select(ChatMessageModel)
        .filter(
            (ChatMessageModel.from_id == message.from_id)
            & (ChatMessageModel.to_id == message.to_id)
            | (ChatMessageModel.from_id == message.to_id)
            & (ChatMessageModel.to_id == message.from_id)
        )
        .order_by(ChatMessageModel.time.asc())
    )
    messages = result.scalars().all()
    return messages


def _format_history_as_llm_context(messages):
    return (
        [{"role": "system", "content": SYSTEM_PROMPT}]
        + [{"role": "assistant", "content": INIT_AI_PROMPT}]
        + [
            {
                "role": "assistant" if msg.from_id == USER_AI else "user",
                "content": msg.text_message,
            }
            for msg in messages
        ]
    )


def _get_llm_response(llm_context):
    response = app.oai_client.chat.completions.create(
        messages=llm_context, model="gpt-3.5-turbo"
    )
    return response.choices[0].message.content


# Endpoint to receive a chat message
@app.post("/soul_sync/ai_wingman_chat/")
async def chat(message: UserMessage, session: AsyncSession = Depends(get_session)):

    await _insert_message_in_db(
        message_id=str(uuid.uuid4()),
        text_message=message.text_message,
        from_id=message.from_id,
        to_id=message.to_id,
        time=datetime.now(),
        session=session,
    )
    messages = await _get_user_conversation_history(message, session)
    llm_context = _format_history_as_llm_context(messages)
    ai_wingman_message = _get_llm_response(llm_context)
    ai_wingman_message_id=str(uuid.uuid4())
    ai_wingman_message_time=datetime.now()
    await _insert_message_in_db(
        message_id=ai_wingman_message_id,
        text_message=ai_wingman_message,
        from_id=message.to_id,
        to_id=message.from_id,
        time=ai_wingman_message_time,
        session=session,
    )

    return {
        "message_id": ai_wingman_message_id,
        "text_message": ai_wingman_message,
        "from_id": message.from_id,
        "to_id": message.from_id,
        "time": ai_wingman_message_time,
    }
