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

# {'url': 'https://t.me/s/frontendproglib', 'last_msg_id': 'null', 'tags_for_response': []},
# {'url': 'https://t.me/s/python_ready', 'last_msg_id': 'null', 'tags_for_response': []},
# {'url': 'https://t.me/s/bezsmuzi', 'last_msg_id': 'null', 'tags_for_response': []},
# {'url': 'https://t.me/s/black_triangle_tg', 'last_msg_id': 'null', 'tags_for_response': []},
# {'url': 'https://t.me/s/fitu_bsuir', 'last_msg_id': 'null', 'tags_for_response': []},
# {'url': 'https://t.me/s/prepodsteam', 'last_msg_id': 'null', 'tags_for_response': []},
# https://t.me/s/frontendproglib