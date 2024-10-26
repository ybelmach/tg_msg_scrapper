import uuid
import datetime

from pydantic import BaseModel


class Channel(BaseModel):
    id: uuid.UUID
    telegram_id: int
    telegram_name: str
    created_at: datetime.datetime
    last_message_id: int


class Message(BaseModel):
    id: str  # UUID
    telegram_id: int
    created_at: datetime.datetime
    summary: str
    uri: str
    channel_id: uuid.UUID
