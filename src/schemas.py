from pydantic import BaseModel
from datetime import datetime


class InitAIMessage(BaseModel):
    from_id: str
    to_id: str

    class Config:
        orm_mode = True


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
