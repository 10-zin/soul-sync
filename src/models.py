from datetime import datetime, timezone
import enum
import uuid
from sqlalchemy import UUID, Boolean, Column, Integer, String, Text, DateTime, ForeignKey, Table, Enum, Float
from sqlalchemy.orm import relationship

from .database import Base
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()


# Define the association table for conversations and participants
conversation_participant_association = Table(
    'conversation_participant_association', Base.metadata,
    Column('conversation_id', UUID(as_uuid=True), ForeignKey('conversations.id')),
    Column('participant_id', UUID(as_uuid=True), ForeignKey('participants.id'))
)

class ParticipantType(enum.Enum):
    human = "user"
    ai = "ai"

class Participant(Base):
    __tablename__ = 'participants'

    id = Column(UUID(as_uuid=True), primary_key=True, index=True, default=uuid.uuid4, unique=True, nullable=False)
    type = Column(Enum(ParticipantType))  # Could be 'user' or 'ai_wingman'
    user_id = Column(UUID(as_uuid=True), ForeignKey('users.id'), nullable=True)
    user = relationship("User", back_populates="participant", uselist=False)
    ai_wingman_id = Column(UUID(as_uuid=True), ForeignKey('ai_wingmen.id'), nullable=True)
    ai_wingman = relationship("AIWingman", back_populates="participant", uselist=False)
    conversations = relationship("Conversation", secondary="conversation_participant_association", back_populates="participants")
    messages = relationship("Message", back_populates="sender")

class User(Base):
    __tablename__ = "users"

    id = Column(UUID(as_uuid=True), primary_key=True, index=True, default=uuid.uuid4, unique=True, nullable=False)
    username = Column(String, unique=True, index=True)
    email = Column(String, unique=True, index=True)
    hashed_password = Column(String)
    is_active = Column(Boolean, default=True)
    
    ai_wingman_id = Column(UUID(as_uuid=True), ForeignKey('ai_wingmen.id'))
    ai_wingman = relationship("AIWingman", back_populates="user")

    profile = relationship("UserProfile", back_populates="user", uselist=False)
    participant = relationship("Participant", back_populates="user", uselist=False)
    questions_asked = relationship("QuestionAsked", back_populates="user")

class UserProfile(Base):
    __tablename__ = "user_profiles"

    id = Column(UUID(as_uuid=True), primary_key=True, index=True, default=uuid.uuid4, unique=True, nullable=False)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), unique=True)
    
    first_name = Column(String)
    last_name = Column(String)
    occupation = Column(String)
    interests = Column(Text)
    age = Column(Integer)
    location = Column(String)
    bio = Column(Text)

    user = relationship("User", back_populates="profile", uselist=False)

class AIWingman(Base):
    __tablename__ = "ai_wingmen"
    
    id = Column(UUID(as_uuid=True), primary_key=True, index=True, default=uuid.uuid4, unique=True, nullable=False)
    level = Column(Integer, default=1)
    knowledge = Column(Text)  # JSON or similar format to store what it learns about the user
    conversation_id_user_default = Column(UUID(as_uuid=True), ForeignKey("conversations.id"))
    
    user = relationship("User", back_populates="ai_wingman", uselist=False)
    participant = relationship("Participant", back_populates="ai_wingman", uselist=False)

class Conversation(Base):
    __tablename__ = "conversations"

    id = Column(UUID(as_uuid=True), primary_key=True, index=True, default=uuid.uuid4, unique=True, nullable=False)
    created_at = Column(DateTime)

    messages = relationship("Message", back_populates="conversation")
    participants = relationship("Participant", secondary=conversation_participant_association, back_populates="conversations")

class Message(Base):
    __tablename__ = "messages"

    id = Column(UUID(as_uuid=True), primary_key=True, index=True, default=uuid.uuid4, unique=True, nullable=False)
    conversation_id = Column(UUID(as_uuid=True), ForeignKey("conversations.id"))
    conversation = relationship("Conversation", back_populates="messages")
    content = Column(Text)
    created_at = Column(DateTime, default=datetime.now(timezone.utc))

    sender_id = Column(UUID(as_uuid=True), ForeignKey("participants.id"))
    sender = relationship("Participant", back_populates="messages")
    
    
class Question(Base):
    __tablename__ = "questions"

    id = Column(UUID(as_uuid=True), primary_key=True, index=True, default=uuid.uuid4, unique=True, nullable=False)
    content = Column(Text)
    created_at = Column(DateTime, default=datetime.now(timezone.utc))
    
    frequency_days = Column(Integer, default=1)
    
    instances = relationship("QuestionAsked", back_populates="question")
    
    
class QuestionAsked(Base):
    __tablename__ = 'questions_asked'
    id = Column(UUID(as_uuid=True), primary_key=True, index=True, default=uuid.uuid4, unique=True, nullable=False)
    user_id = Column(UUID(as_uuid=True), ForeignKey('users.id'))
    question_id = Column(UUID(as_uuid=True), ForeignKey('questions.id'))
    conversation_id = Column(UUID(as_uuid=True), ForeignKey('conversations.id'))
    asked_at = Column(DateTime, default=datetime.now(timezone.utc))

    user = relationship("User", back_populates="questions_asked")
    question = relationship("Question", back_populates="instances")
    
    messages_count = Column(Integer, default=0, nullable=False)

class MatchmakingResult(Base):
    __tablename__ = "matchmaking_results"

    id = Column(UUID(as_uuid=True), primary_key=True, index=True, default=uuid.uuid4, unique=True, nullable=False)
    user_id = Column(UUID(as_uuid=True), ForeignKey('users.id')) 
    match_score = Column(Float)  # Example field, adjust based on what you store for a matchmaking result
    reasoning = Column(Text)
    system_prompt_type = Column(Integer)  # Field for system prompt type
    counter = Column(Integer)

class MatchmakingCounter(Base):
    __tablename__ = "matchmaking_counter"

    id = Column(UUID(as_uuid=True), primary_key=True, index=True, default=uuid.uuid4, unique=True, nullable=False)
    user_id = Column(UUID(as_uuid=True), ForeignKey('users.id')) 
    counter = Column(Integer, default=0, nullable=False)

    
    