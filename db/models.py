import datetime

from sqlalchemy import ForeignKey, text
from sqlalchemy.orm import mapped_column, Mapped

from db.database import Base


class Channels(Base):
    __tablename__ = 'channels'

    id: Mapped[str] = mapped_column(primary_key=True, nullable=False)
    telegram_id: Mapped[int] = mapped_column(nullable=False)
    telegram_name: Mapped[str] = mapped_column(nullable=False)
    created_at: Mapped[datetime.datetime] = mapped_column(server_default=text("TIMEZONE('utc', now())"))
    last_message_id: Mapped[int] = mapped_column(nullable=True)


class Messages(Base):
    __tablename__ = 'messages'

    id: Mapped[str] = mapped_column(primary_key=True, nullable=False)
    telegram_id: Mapped[int] = mapped_column(nullable=False)
    created_at: Mapped[datetime.datetime] = mapped_column(server_default=text("TIMEZONE('utc', now())"))
    summary: Mapped[str] = mapped_column(nullable=False)
    uri: Mapped[str] = mapped_column(nullable=True)
    channel_id: Mapped[str] = mapped_column(ForeignKey('channels.id'), nullable=True)
