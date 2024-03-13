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
    ai_wingman: 'AIWingman'
    participant: 'Participant'
    
    class Config:
        orm_mode = True

class UserProfileBase(BaseModel):
    bio: Optional[str] = None
    interests: Optional[str] = None
    preferences: Optional[str] = None

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
    participant: 'Participant'

    class Config:
        orm_mode = True

class ParticipantBase(BaseModel):
    type: ParticipantType

class ParticipantCreate(ParticipantBase):
    user_id: Optional[UUID] = None
    ai_wingman_id: Optional[UUID] = None

class Participant(ParticipantBase):
    id: UUID
    user_id: Optional[UUID] = None
    ai_wingman_id: Optional[UUID] = None
    conversations: List['Conversation']

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
    participants: List[Participant]
    messages: List[Message]

    class Config:
        orm_mode = True

class QuestionBase(BaseModel):
    content: str

class QuestionCreate(QuestionBase):
    pass

class Question(QuestionBase):
    id: UUID
    created_at: datetime

    class Config:
        orm_mode = True