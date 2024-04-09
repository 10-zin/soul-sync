from fastapi import APIRouter, Depends, Header, HTTPException, status
from sqlalchemy.orm import Session

from ..utils import ADMIN_API_TOKEN

from ..database import get_db

from .. import crud, schemas

def admin_api_token_auth(Authorization: str = Header(...)):
    if Authorization != f"token {ADMIN_API_TOKEN}":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or missing API token",
        )

router = APIRouter(
    dependencies=[Depends(admin_api_token_auth)]
)

@router.get("/users", response_model=list[schemas.UserAdminResponse])
async def get_users(db: Session = Depends(get_db)):
    return crud.get_users(db)

@router.get("/users/{user_id}", response_model=schemas.UserAdminResponse)
async def get_users(user_id: str, db: Session = Depends(get_db)):
    return crud.get_user(db, user_id)

@router.delete("/users/{user_id}")
async def remove_user(user_id: str, db: Session = Depends(get_db)):
    return crud.remove_user(db, user_id)

# See the converation users had with thier AI wingman
@router.get("/users/{user_id}/conversations")
async def get_users(user_id: str, db: Session = Depends(get_db)):
    participant = crud.get_participant_by_user_id(db, user_id)
    return participant.conversations

# Get messages from a conversation
@router.get("/conversations/{conversation_id}/messages")
async def get_conversation_messages(conversation_id: str, db: Session = Depends(get_db)):
    return crud.get_messages(db, conversation_id)

# Get a list of questions 
@router.get("/questions")
async def get_questions(db: Session = Depends(get_db)):
    return crud.get_questions(db)

# Add a new question
@router.post("/questions")
async def add_question(question: schemas.QuestionCreate, db: Session = Depends(get_db)):
    return crud.add_question(db, question)

# Delete a question
@router.delete("/questions/{question_id}")
async def remove_question(question_id: str, db: Session = Depends(get_db)):
    return crud.remove_question(db, question_id)

@router.get("/questions/{question_id}/asked")
async def get_question_asked_instances(question_id: str, db: Session = Depends(get_db)):
    return crud.get_question_asked_instances(db, question_id)