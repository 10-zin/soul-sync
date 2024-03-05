# from sqlalchemy import Column, String, DateTime
# from sqlalchemy.ext.declarative import declarative_base
# from datetime import datetime

# Base = declarative_base()

# class ChatMessage(Base):
#     __tablename__ = 'chat_messages'

#     message_id = Column(String, primary_key=True, index=True)
#     text_message = Column(String, index=True)
#     from_id = Column(String, index=True)
#     to_id = Column(String, index=True)
#     time = Column(DateTime, default=datetime.utcnow)


from pydantic import BaseModel
from datetime import datetime


class UserMessage(BaseModel):
    text_message: str
    from_id: str
    to_id: str

    class Config:
        orm_mode = True

class ChatMessage(UserMessage):
    message_id: str
    time: datetime
    class Config:
        orm_mode = True


