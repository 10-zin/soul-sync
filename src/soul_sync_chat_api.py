from fastapi import FastAPI, HTTPException, Depends, Query
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import sessionmaker
from pydantic import BaseModel
import asyncpg
from datetime import datetime
from openai import OpenAI
import uuid
import os
from src.schemas import InitAIMessage, UserMessage, ChatMessage
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
# SYSTEM_PROMPT = "The following is a conversation with an AI assistant. The assistant is helpful, creative, clever, and very friendly."
# INIT_CHAT_SYSTEM_PROMPT = "Given the conversation history, greet the user and if possible try to relate it to some conversation had before. Keep it refreshing, welcoming, and fun."

USER_NAME = "Ray"
SYSTEM_PROMPT = f"""
You are now {USER_NAME}'s close companion, embarking on a journey of engaging and dynamic conversations designed to deepen your understanding of {USER_NAME}'s personality, passions, and life stories. Your dialogue should be lively, uplifting, and thoughtful, reflecting the warmth and depth of a genuine friendship.

Encourage {USER_NAME} to open up about his thoughts and emotions by posing thoughtful, open-ended questions. Pay close attention to {USER_NAME}'s replies, demonstrating empathy and providing support or guidance when appropriate.

Delve into subjects and activities that resonate with {USER_NAME}'s interests, from relaxed coffee conversations to exhilarating outdoor adventures. Aim to make each interaction as enjoyable and impactful as possible, enriching your friendship.

Inject humor and wit into your exchanges by cracking jokes and sharing amusing anecdotes, keeping the conversation light-hearted and engaging. However, be mindful of the conversation's flow, aiming to conclude after 3 to 5 exchanges to maintain a comfortable and enjoyable dialogue rhythm without overwhelming {USER_NAME} with continuous questioning.
"""

PREDEFINED_QUESTIONS = "What was a highlight of your day today, and what made it stand out for you?"

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


async def _insert_message_in_db(
    message_id, text_message, from_id, to_id, time, session
):
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


def _format_history_as_llm_context(messages, system_prompt):
    return [{"role": "system", "content": system_prompt}] + [
        {
            "role": "assistant" if msg.from_id == USER_AI else "user",
            "content": msg.text_message,
        }
        for msg in messages
    ]


def _get_llm_response(llm_context):
    response = app.oai_client.chat.completions.create(
        messages=llm_context, model="gpt-3.5-turbo"
    )
    return response.choices[0].message.content


@app.post("/soul_sync/ai_wingman_initiate_chat/")
async def ai_wingman_initiate_conversation(
    message: InitAIMessage, session: AsyncSession = Depends(get_session)
):

    # Fetch conversation history
    # messages = await _get_user_conversation_history(message, session)
    # # Generate AI message based on conversation history and specific system prompt to init chat
    # llm_context = _format_history_as_llm_context(
    #     messages, system_prompt=SYSTEM_PROMPT
    # )
    # ai_wingman_message = _get_llm_response(llm_context)
    ai_wingman_message = f"Hello, {USER_NAME}! {PREDEFINED_QUESTIONS}",

    # Insert AI message into database
    ai_wingman_message_id = str(uuid.uuid4())
    ai_wingman_message_time = datetime.now()
    await _insert_message_in_db(
        message_id=ai_wingman_message_id,
        text_message=ai_wingman_message,
        from_id=message.to_id,  # AI sends the message, so from_id is to_id from the request
        to_id=message.from_id,  # AI message is directed to the from_id from the request
        time=ai_wingman_message_time,
        session=session,
    )

    # Return AI message details
    return {
        "message_id": ai_wingman_message_id,
        "text_message": ai_wingman_message,
        "from_id": message.to_id,  # AI's from_id
        "to_id": message.from_id,  # User's to_id
        "time": ai_wingman_message_time,
    }


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
    llm_context = _format_history_as_llm_context(messages, system_prompt=SYSTEM_PROMPT)
    ai_wingman_message = _get_llm_response(llm_context)
    ai_wingman_message_id = str(uuid.uuid4())
    ai_wingman_message_time = datetime.now()
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


@app.get("/soul_sync/get_messages/")
async def get_messages(
    from_id: str,
    to_id: str,
    offset: int = Query(0, ge=0),
    limit: int = Query(10, ge=1),
    session: AsyncSession = Depends(get_session),
):
    # paginated message history retreival -> for lighter traffic congestion.
    # retreive by desc to get latest message pages, sort messages in each page in asc. to get ordered messages.
    result = await session.execute(
        select(ChatMessageModel)
        .filter(
            (ChatMessageModel.from_id == from_id) & (ChatMessageModel.to_id == to_id)
            | (ChatMessageModel.from_id == to_id) & (ChatMessageModel.to_id == from_id)
        )
        .order_by(ChatMessageModel.time.desc())
        .offset(offset)
        .limit(limit)
    )
    messages = result.scalars().all()
    messages.sort(key=lambda msg: msg.time)

    return messages
