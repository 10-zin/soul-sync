from pydantic import BaseModel
from datetime import datetime
from typing import List, Optional
from uuid import UUID
from .models import ParticipantType


class Token(BaseModel):
    access_token: str
    token_type: str


class TokenData(BaseModel):
    username: Optional[str] = None


class UserBase(BaseModel):
    username: str
    email: str
    ai_wingman_id: Optional[UUID] = None


class UserCreate(UserBase):
    password: str


class UserUpdate(UserBase):
    password: Optional[str] = None


class User(UserBase):
    id: UUID
    is_active: bool
    profile: Optional["UserProfile"] = None
    ai_wingman: "AIWingman"
    participant: "Participant"
    questions_asked: List["QuestionAsked"] = []

    class Config:
        orm_mode = True


class UserAdminResponse(UserBase):
    id: UUID
    is_active: bool
    profile: Optional["UserProfile"] = None
    ai_wingman: "AIWingman"
    participant: "ParticipantInConversation"

    class Config:
        orm_mode = True


class UserProfileBase(BaseModel):
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    occupation: Optional[str] = None
    interests: Optional[str] = None
    age: Optional[int] = None
    location: Optional[str] = None
    bio: Optional[str] = None


class UserProfileCreate(UserProfileBase):
    pass


class UserProfile(UserProfileBase):
    id: UUID
    user_id: UUID

    class Config:
        orm_mode = True


class AIWingmanBase(BaseModel):
    level: int = 1
    knowledge: Optional[str] = None
    conversation_id_user_default: Optional[UUID] = None


class AIWingmanCreate(AIWingmanBase):
    pass


class AIWingman(AIWingmanBase):
    id: UUID
    participant: "ParticipantInConversation"

    class Config:
        orm_mode = True


class ParticipantBase(BaseModel):
    type: ParticipantType


class ParticipantCreate(ParticipantBase):
    user_id: Optional[UUID] = None
    ai_wingman_id: Optional[UUID] = None


class ParticipantInConversation(ParticipantBase):
    id: UUID
    user_id: Optional[UUID] = None
    ai_wingman_id: Optional[UUID] = None

    class Config:
        orm_mode = True


class Participant(ParticipantInConversation):
    conversations: List["Conversation"]

    class Config:
        orm_mode = True


class MessageBase(BaseModel):
    content: str


class MessageCreate(MessageBase):
    conversation_id: UUID
    sender_id: UUID


class Message(MessageBase):
    id: UUID
    conversation_id: UUID
    sender_id: UUID
    created_at: datetime

    class Config:
        orm_mode = True


class ConversationBase(BaseModel):
    pass


class ConversationCreate(ConversationBase):
    participant_ids: List[UUID]


class Conversation(ConversationBase):
    id: UUID
    created_at: datetime
    messages: List[Message]
    participants: List[ParticipantInConversation] = []

    class Config:
        orm_mode = True


# Schema for Question model
class QuestionBase(BaseModel):
    content: str
    frequency_days: int = 0


class QuestionCreate(QuestionBase):
    pass


class Question(QuestionBase):
    id: UUID
    created_at: datetime

    class Config:
        orm_mode = True


# Schema for QuestionAsked model
class QuestionAskedBase(BaseModel):
    asked_at: datetime
    user_id: UUID
    question_id: UUID
    conversation_id: UUID


class QuestionAskedCreate(QuestionAskedBase):
    pass


class QuestionAsked(QuestionAskedBase):
    id: UUID

    class Config:
        orm_mode = True


class MatchmakingResult(BaseModel):
    user_id: UUID
    score: float
    reasoning: str
    system_prompt_type: int
