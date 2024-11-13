import uuid
import datetime

from pydantic import BaseModel


class Channel(BaseModel):
    id: uuid.UUID
    telegram_id: int | None = None
    telegram_name: str
    created_at: datetime.datetime
    last_message_id: int


class Message(BaseModel):
    id: uuid.UUID
    telegram_id: int | None = None
    created_at: datetime.datetime
    summary: str
    channel_id: uuid.UUID
    sended_at: datetime.datetime
    wrapped_url_id: uuid.UUID


class WrappedUrl(BaseModel):
    id: uuid.UUID
    url: str
