from datetime import datetime, timedelta, timezone
import random
from typing import Annotated, List
from uuid import UUID
from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from pydantic import BaseModel
from sqlalchemy import and_, func, or_
from sqlalchemy.sql.expression import text
from sqlalchemy.orm import Session

from .internal import admin
import base64


from . import models, schemas, crud
from .auth import (
    ACCESS_TOKEN_EXPIRE_MINUTES,
    ALGORITHM,
    SECRET_KEY,
    create_access_token,
    verify_password,
    oauth2_scheme,
)
from .database import engine, get_db
from .llm import get_ai_response, get_ai_match_recommendations

from fastapi import Depends, HTTPException, status
from typing import Annotated
from jose import JWTError, jwt

models.Base.metadata.create_all(bind=engine)

app = FastAPI()
app.include_router(
    admin.router,
    prefix="/admin",
)

# TODO:
# Write automated api test


def authenticate_user(db: Session, username: str, password: str):
    user = crud.get_user_by_username(db, username=username)
    if not user or not verify_password(password, user.hashed_password):
        return False
    return user


def get_current_user(
    token: Annotated[str, Depends(oauth2_scheme)], db: Session = Depends(get_db)
):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
        token_data = schemas.TokenData(username=username)
    except JWTError:
        raise credentials_exception
    user = crud.get_user_by_username(db, username=token_data.username)

    if user is None:
        raise credentials_exception
    return user


# TODO: Use Transactions
def signup_user(db: Session, user_data: schemas.UserCreate):
    db_user = crud.create_user(db=db, user=user_data)
    # Create a Participant for user
    db_user_participant = crud.create_participant(db, user_id=db_user.id)
    # Create a AI Wingman for user
    ai_wingman = crud.create_ai_wingman(
        db, schemas.AIWingmanCreate(level=1, knowledge="")
    )
    # Create a Participant for AI Wingman
    db_ai_wingman_participant = crud.create_participant(db, ai_wingman_id=ai_wingman.id)
    # Update user with AI Wingman ID
    db_user.ai_wingman_id = ai_wingman.id
    db_user = crud.update_user(
        db,
        db_user.id,
        schemas.UserUpdate(
            username=db_user.username,
            email=db_user.email,
            ai_wingman_id=db_user.ai_wingman_id,
            password=user_data.password,
        ),
    )
    # Create a default conversation between user and AI Wingman
    db_conversation = crud.create_conversation(
        db,
        schemas.ConversationCreate(
            participant_ids=[db_user_participant.id, db_ai_wingman_participant.id]
        ),
    )
    crud.update_ai_wingman(
        db,
        ai_wingman.id,
        schemas.AIWingmanCreate(
            level=1, knowledge="", conversation_id_user_default=db_conversation.id
        ),
    )
    return db_user


@app.post("/token")
async def login_for_access_token(
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
    db: Session = Depends(get_db),
) -> schemas.Token:
    user = authenticate_user(
        db, username=form_data.username, password=form_data.password
    )
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.username}, expires_delta=access_token_expires
    )
    return schemas.Token(access_token=access_token, token_type="bearer")


@app.post("/users", response_model=schemas.User)
def create_user(user: schemas.UserCreate, db: Session = Depends(get_db)):
    if crud.get_user_by_email(db, email=user.email):
        raise HTTPException(status_code=400, detail="Email already registered")
    elif crud.get_user_by_username(db, username=user.username):
        raise HTTPException(status_code=400, detail="Username already registered")
    return signup_user(db, user)


@app.post("/user_profiles", response_model=schemas.UserProfile)
def create_user_profile(
    user_profile: schemas.UserProfileCreate,
    db: Session = Depends(get_db),
    current_user: schemas.User = Depends(get_current_user),
):
    db_user_profile = crud.create_user_profile(
        db, user_profile, user_id=current_user.id
    )
    return db_user_profile


@app.get("/user_profiles", response_model=schemas.UserProfile)
def get_user_profile(
    db: Session = Depends(get_db),
    current_user: schemas.User = Depends(get_current_user),
):
    db_user_profile = crud.get_user_profile(db, user_id=current_user.id)
    return db_user_profile


@app.get("/soul_sync/ai_wingman_initiate_conversation")
async def ai_wingman_initiate_conversation(
    db: Session = Depends(get_db),
    current_user: schemas.User = Depends(get_current_user),
):
    if current_user.profile is None:
        raise HTTPException(status_code=400, detail="User profile not found")

    conversation_id = current_user.ai_wingman.conversation_id_user_default
    ai_wingman_participant_id = current_user.ai_wingman.participant.id

    # Find the last question asked to this user
    latest_question_asked_to_user = crud.get_latest_question_asked_to_user(
        db, current_user.id
    )
    if latest_question_asked_to_user:
        latest_question_asked_to_user.messages_count = (
            crud.count_messages_after_timestamp_in_conversation(
                db, conversation_id, latest_question_asked_to_user.asked_at
            )
        )
        crud.update_question_asked_with_message_count(
            db,
            latest_question_asked_to_user.id,
            latest_question_asked_to_user.messages_count,
        )

    # Find all QuestionAsked to the user over the past 60 days
    sixty_days_ago = datetime.now(timezone.utc) - timedelta(days=60)
    recent_questions = (
        db.query(models.QuestionAsked.question_id)
        .filter(
            and_(
                models.QuestionAsked.user_id == current_user.id,
                models.QuestionAsked.asked_at >= sixty_days_ago,
            )
        )
        .subquery()
    )

    # Find all questions that are not in the recently asked list
    available_questions = (
        db.query(models.Question)
        .filter(
            ~models.Question.id.in_(recent_questions),
        )
        .all()
    )

    if not available_questions:
        raise HTTPException(status_code=404, detail="No new questions available")

    # Randomly select a question to ask
    question = random.choice(available_questions)
    formatted_question = f"Hello, {current_user.profile.first_name}! {question.content}"

    # Create a new message with the selected question
    db_message = crud.create_message(
        db,
        schemas.MessageCreate(
            conversation_id=conversation_id,
            sender_id=ai_wingman_participant_id,
            content=formatted_question,
        ),
    )

    # Record the question asked in QuestionAsked
    db_question_asked = models.QuestionAsked(
        user_id=current_user.id,
        question_id=question.id,
        conversation_id=conversation_id,
        asked_at=datetime.now(timezone.utc),
    )
    db.add(db_question_asked)
    db.commit()

    return {
        "conversation_id": conversation_id,
        "message_id": db_message.id,
        "text_message": formatted_question,
        "sender_id": ai_wingman_participant_id,
        "time": db_message.created_at,
    }


class AIWingmanConversationInput(BaseModel):
    conversation_id: str
    content: str


@app.post("/soul_sync/ai_wingman_conversation")
async def ai_wingman_conversation(
    message: AIWingmanConversationInput,
    db: Session = Depends(get_db),
    current_user: schemas.User = Depends(get_current_user),
):
    db_ai_wingman_participant_id = current_user.ai_wingman.participant.id
    crud.create_message(
        db,
        schemas.MessageCreate(
            conversation_id=message.conversation_id,
            sender_id=current_user.participant.id,
            content=message.content,
        ),
    )
    db_messages = crud.get_messages(
        db, conversation_id=message.conversation_id, skip=0, limit=100
    )
    db_messages.sort(key=lambda x: x.created_at)
    ai_message_content = get_ai_response(
        db_messages,
        db_ai_wingman_participant_id,
        current_user,
    )

    db_ai_message = crud.create_message(
        db,
        schemas.MessageCreate(
            conversation_id=message.conversation_id,
            sender_id=db_ai_wingman_participant_id,
            content=ai_message_content,
        ),
    )

    # Return AI message details
    return {
        "conversation_id": message.conversation_id,
        "message_id": db_ai_message.id,
        "text_message": ai_message_content,
        "sender_id": db_ai_wingman_participant_id,
        "time": db_ai_message.created_at,
    }


@app.post("/conversations", response_model=schemas.Conversation)
def create_conversation(
    db: Session = Depends(get_db),
    current_user: schemas.User = Depends(get_current_user),
):
    pass


@app.post("/conversations/{conversation_id}/messages", response_model=schemas.Message)
def create_message(
    conversation_id: int,
    message: schemas.MessageCreate,
    db: Session = Depends(get_db),
    current_user: schemas.User = Depends(get_current_user),
):
    # Get the current user based on the token (not implemented in this example)
    current_user = crud.get_user(db, user_id=1)  # Placeholder user

    # Ensure the current user is part of the conversation
    conversation = crud.get_conversation(db, conversation_id=conversation_id)
    if current_user not in conversation.users:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User not authorized to access this conversation",
        )

    message.user_id = current_user.id
    message.conversation_id = conversation_id
    return crud.create_message(db, message=message)


@app.get("/conversations", response_model=List[UUID])
def read_conversations(
    db: Session = Depends(get_db),
    current_user: schemas.User = Depends(get_current_user),
    skip: int = 0,
    limit: int = 100,
):
    conversations = crud.get_conversations_by_participant_id(
        db, current_user.participant.id, skip=skip, limit=limit
    )
    return [c.id for c in conversations]


@app.get(
    "/conversations/{conversation_id}/messages", response_model=List[schemas.Message]
)
def read_messages(
    conversation_id: UUID,
    db: Session = Depends(get_db),
    current_user: schemas.User = Depends(get_current_user),
    skip: int = 0,
    limit: int = 100,
):
    # Assert that the conversation is accessible by the current user
    conversation: models.Conversation = crud.get_conversation_by_id(
        db, conversation_id=conversation_id
    )
    if current_user.participant.id not in [p.id for p in conversation.participants]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User not authorized to access this conversation",
        )
    messages = crud.get_messages(
        db, conversation_id=conversation_id, skip=skip, limit=limit
    )
    return messages


def _get_conversation_history(db, user_conversations_data):
    user_conversations = []
    for user_conversation in user_conversations_data:
        messages = crud.get_messages(db, conversation_id=user_conversation.id)[::-1]
        user_conversations.append(
            {"conversation_id": user_conversation.id, "messages": messages}
        )
    return user_conversations


@app.get("/ai_wingman_matches", response_model=List[schemas.MatchmakingResult])
def matchmaking(
    current_user: schemas.User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    results = []

    # current user conversation history
    current_user_conversations_data = crud.get_conversations_by_participant_id(
        db, current_user.participant.id
    )
    current_user_conversations = _get_conversation_history(
        db, current_user_conversations_data
    )

    # candidate user conversation history and matching for each with current user
    candidates_profiles = crud.get_all_user_profiles_except_current(
        db, current_user_id=current_user.id
    )
    for candidate_profile in candidates_profiles:

        candidate_conversation_data = crud.get_conversations_by_participant_id(
            db, candidate_profile.user_id
        )
        candidate_conversations = _get_conversation_history(
            db, candidate_conversation_data
        )

        match_result = get_ai_match_recommendations(
            user_conversation=current_user_conversations,
            candidate_profile=candidate_profile,
            candidate_conversation=candidate_conversations,
        )

        results.append(match_result)

    return results


@app.get("/user-profiles/{user_id}", response_model=schemas.UserProfile)
def get_user_profile(user_id: UUID, db: Session = Depends(get_db)):
    user_profile = crud.get_user_profile(db, user_id=user_id)
    if user_profile:
        return user_profile
    else:
        raise HTTPException(status_code=404, detail="User profile not found")


@app.get("/health")
def health_check():
    return {"status": "OK"}
