import logging

from db.models import Channels, Messages
from schemas import Channel, Message
from logging_config import logger


class ChannelService:
    @staticmethod
    def update_channel_id(db, data: Channel):
        post_query = db.query(Channels).filter(Channels.id == data.id)
        if post_query.first() is None:
            logger.error(f"Channel {data.id} not found")
        post_query.update(data.model_dump(), synchronize_session=False)
        db.commit()


class MessageService:
    @staticmethod
    def add_message(db, data: Message):
        new_message = Messages(**data.model_dump())

        telegram_ids = [i.telegram_id for i in MessageService.get_messages(db)]
        if data.telegram_id not in telegram_ids:
            db.add(new_message)
            db.commit()
            db.refresh(new_message)
            return new_message
        else:
            logger.error(f"Message {data.telegram_id} already exists, skipping saving")

    @staticmethod
    def get_messages(db):
        return db.query(Messages).all()
