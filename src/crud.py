from sqlalchemy.orm import Session
from uuid import UUID

from src.auth import hash_password
from . import models, schemas
from datetime import datetime, timezone


def commit_changes(db: Session, db_item):
    db.add(db_item)
    db.commit()
    db.refresh(db_item)
    return db_item


def get_item_by_id(db: Session, model, item_id):
    return db.query(model).filter(model.id == item_id).first()


def get_user(db: Session, user_id: UUID):
    return db.query(models.User).filter(models.User.id == user_id).first()

def remove_user(db: Session, user_id: UUID):
    db_user = get_user(db, user_id)
    if db_user:
        db.delete(db_user)
        db.commit()
    return db_user

def get_user_by_username(db: Session, username: str):
    return db.query(models.User).filter(models.User.username == username).first()


def get_user_by_email(db: Session, email: str):
    return db.query(models.User).filter(models.User.email == email).first()


def get_users(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.User).offset(skip).limit(limit).all()


def create_user(db: Session, user: schemas.UserCreate):
    hashed_password = hash_password(user.password)
    db_user = models.User(
        username=user.username, email=user.email, hashed_password=hashed_password
    )
    return commit_changes(db, db_user)


def update_user(db: Session, user_id: UUID, user: schemas.UserUpdate):
    db_user = get_user(db, user_id)
    if db_user:
        db_user.username = user.username
        db_user.email = user.email
        if user.password:
            db_user.hashed_password = hash_password(user.password)
        if user.ai_wingman_id:
            db_user.ai_wingman_id = user.ai_wingman_id
        db.commit()
        db.refresh(db_user)
    return db_user


def delete_user(db: Session, user_id: UUID):
    db_user = get_user(db, user_id)
    if db_user:
        db.delete(db_user)
        db.commit()
    return db_user


def create_user_profile(db: Session, profile: schemas.UserProfileCreate, user_id: UUID):
    db_profile = models.UserProfile(**profile.model_dump(), user_id=user_id)
    return commit_changes(db, db_profile)


def get_user_profile(db: Session, user_id: UUID):
    return (
        db.query(models.UserProfile)
        .filter(models.UserProfile.user_id == user_id)
        .first()
    )


def get_all_users_except_current(db: Session, current_user_id: int):
    return (
        db.query(models.User)
        .filter(models.User.id != current_user_id)
        .all()
    )


def create_ai_wingman(db: Session, ai_wingman: schemas.AIWingmanCreate):
    db_ai_wingman = models.AIWingman(**ai_wingman.model_dump())
    return commit_changes(db, db_ai_wingman)


def update_ai_wingman(
    db: Session, ai_wingman_id: UUID, ai_wingman: schemas.AIWingmanCreate
):
    db_ai_wingman = get_ai_wingman(db, ai_wingman_id)
    if db_ai_wingman:
        db_ai_wingman.level = ai_wingman.level
        db_ai_wingman.knowledge = ai_wingman.knowledge
        db_ai_wingman.conversation_id_user_default = (
            ai_wingman.conversation_id_user_default
        )
        db.commit()
        db.refresh(db_ai_wingman)
    return db_ai_wingman


def get_ai_wingman(db: Session, ai_wingman_id: UUID):
    return get_item_by_id(db, models.AIWingman, ai_wingman_id)


def get_conversation_by_id(db: Session, conversation_id: UUID):
    return get_item_by_id(db, models.Conversation, conversation_id)


def get_conversations_by_participant_id(
    db: Session, participant_id: UUID, skip: int = 0, limit: int = 100
):
    return (
        db.query(models.Conversation)
        .join(models.Participant, models.Conversation.participants)
        .filter(models.Participant.id == participant_id)
        .offset(skip)
        .limit(limit)
        .all()
    )


def create_conversation(db: Session, conversation: schemas.ConversationCreate):
    db_conversation = models.Conversation(created_at=datetime.now(timezone.utc))
    db.add(db_conversation)
    db.commit()
    db.refresh(db_conversation)

    for participant_id in conversation.participant_ids:
        db_participant = get_participant(db, participant_id)
        if db_participant:
            db_conversation.participants.append(db_participant)

    db.commit()
    return db_conversation


def get_messages(db: Session, conversation_id: UUID, skip: int = 0, limit: int = 100):
    return (
        db.query(models.Message)
        .filter(models.Message.conversation_id == conversation_id)
        .order_by(models.Message.created_at.desc())
        .offset(skip)
        .limit(limit)
        .all()
    )


def count_messages_after_timestamp_in_conversation(
    db: Session, conversation_id: UUID, timestamp: datetime
):
    return (
        db.query(models.Message)
        .filter(models.Message.conversation_id == conversation_id)
        .filter(models.Message.created_at >= timestamp)
        .count()
    )


def create_message(db: Session, message: schemas.MessageCreate):
    db_message = models.Message(
        **message.model_dump(), created_at=datetime.now(timezone.utc)
    )
    return commit_changes(db, db_message)


def create_participant(db: Session, user_id: UUID = None, ai_wingman_id: UUID = None):
    if not user_id and not ai_wingman_id:
        raise ValueError("Either user_id or ai_wingman_id must be provided")
    db_participant = models.Participant(
        type=models.ParticipantType.human if user_id else models.ParticipantType.ai,
        user_id=user_id,
        ai_wingman_id=ai_wingman_id,
    )
    return commit_changes(db, db_participant)


def get_participant(db: Session, participant_id: UUID):
    return get_item_by_id(db, models.Participant, participant_id)


def get_participant_by_user_id(db: Session, user_id: UUID):
    return (
        db.query(models.Participant)
        .filter(models.Participant.user_id == user_id)
        .first()
    )


def get_participant_by_ai_wingman_id(db: Session, ai_wingman_id: UUID):
    return (
        db.query(models.Participant)
        .filter(models.Participant.ai_wingman_id == ai_wingman_id)
        .first()
    )


def get_question_asked_instances(db: Session, question_id: UUID):
    return (
        db.query(models.QuestionAsked)
        .filter(models.QuestionAsked.question_id == question_id)
        .all()
    )


def get_latest_question_asked_to_user(db: Session, user_id: UUID):
    return (
        db.query(models.QuestionAsked)
        .filter(models.QuestionAsked.user_id == user_id)
        .order_by(models.QuestionAsked.asked_at.desc())
        .first()
    )


def update_question_asked_with_message_count(
    db: Session, question_asked_id: UUID, messages_count: int
):
    db_question_asked: models.QuestionAsked = get_item_by_id(
        db, models.QuestionAsked, question_asked_id
    )
    if db_question_asked:
        db_question_asked.messages_count = messages_count
        db.commit()
        db.refresh(db_question_asked)
    return db_question_asked


def get_questions(db: Session):
    return db.query(models.Question).all()


def add_question(db: Session, question: schemas.QuestionCreate):
    db_question = models.Question(**question.model_dump())
    return commit_changes(db, db_question)


def remove_question(db: Session, question_id: UUID):
    db_question = get_item_by_id(db, models.Question, question_id)
    if db_question:
        db.delete(db_question)
        db.commit()
    return db_question

def get_existing_counter(db, user_id) -> models.MatchMakingCounter:
    return db.query(models.MatchMakingCounter).filter(models.MatchMakingCounter.user_id == user_id).first()

def create_matchmaking_counter(db, user_id):
    counter = models.MatchMakingCounter(user_id=user_id, counter=0)
    db.add(counter)
    db.commit()
    db.refresh(counter)


def increment_counter_by_id(db_session: Session, user_id: UUID) -> None:
    matchmaking_counter = db_session.query(models.MatchMakingCounter).filter(models.MatchMakingCounter.user_id == user_id).first()
    
    if matchmaking_counter:
        # Increment the counter if the entry is found
        matchmaking_counter.counter += 1
        db_session.commit()

def create_matchmaking_result(db, user_id, candidate_user_id, match_result: schemas.MatchmakingResult, counter):
    
    result = models.MatchMakingResult(
        user_id=user_id,
        candidate_user_id=candidate_user_id,
        match_score=match_result.score,
        reasoning=match_result.reasoning,
        system_prompt_type=match_result.system_prompt_type,
        counter=counter+1
    )
    
    db.add(result)
    db.commit()
    db.refresh(result)


def create_matchmaking_user_rating(db, user_id, candidate_user_id, counter, score):
    user_rating = models.MatchMakingUserRating(
        user_id=user_id,
        candidate_user_id=candidate_user_id,
        counter=counter,
        score=score
    )
    db.add(user_rating)
    db.commit()
    db.refresh(user_rating)
    
    
    
    

