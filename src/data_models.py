from sqlalchemy import Column, String, DateTime
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime
import os

Base = declarative_base()


class ChatMessageModel(Base):
    __tablename__ = os.getenv("DB_TABLE_NAME")  # Actual table name in the database -> chat_messages

    text_message = Column(String, index=True)
    from_id = Column(String, index=True)
    to_id = Column(String, index=True)
    message_id = Column(String, primary_key=True, index=True)
    time = Column(DateTime, default=datetime.utcnow)
