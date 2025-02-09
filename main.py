import time
import uuid
from datetime import datetime
from typing import List

from openai import RateLimitError

from config import MAX_WORDS_NUM
from db.models import Channels
from db.database import get_db
from db.services import ChannelService, MessageService, WrappedUrlService  # noqa
from logging_config import logger
from utils import get_last_message_id, get_summarized_msg, get_bad_msg_text
from schemas import Channel, Message, WrappedUrl
import requests
from bs4 import BeautifulSoup


# todo: Убрать все noqa, подумать, что делать с недоступными каналами
def process_channel(db, channel):
    try:
        url = f"https://t.me/s/{channel.telegram_name}"  # noqa
        logger.info(f"Processing URL: {url}")
        response = requests.get(url)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'lxml')

        try:
            messages: List[str] = (soup.find('section', class_='tgme_channel_history js-message_history')
                                   .find_all('div', class_='tgme_widget_message_wrap js-widget_message_wrap'))
        except AttributeError:
            logger.error(f"Channel {channel.telegram_name} is unavailable to parse")
            return 
        except Exception as e:
            logger.error(f"Error while processing channel {channel.telegram_name}: {e}")
            return

        if channel.last_message_id is not None:
            process_new_messages(messages, channel, db)
        else:
            process_last_message(db, messages, channel)

    except requests.RequestException as e:
        logger.error(f"Connection error: {e}")
    except Exception as e:
        logger.error(f"Error processing channel {channel.telegram_name}: {e}")


def process_last_message(db, messages: list, channel: Channel):
    last_msg_id = get_last_message_id(messages)
    try:
        data = Channel(id=channel.id, telegram_name=channel.telegram_name, created_at=channel.created_at,
                       last_message_id=last_msg_id)
        ChannelService.update_channel_id(db, data)
        logger.info(f"Last message ID ({last_msg_id}) added to database successfully.")
    except Exception as e:
        logger.error(f"Error saving last_msg_id to DB: {e}")


def process_new_messages(messages: list, channel: Channel, db):
    try:
        last_message_id = get_last_message_id(messages)
        logger.info(f"Last message in DB: {channel.last_message_id}, new last message: {last_message_id}")
        if last_message_id <= channel.last_message_id:
            logger.info("No new messages")
            return
        for index in range(-len(messages), 0):
            msg_id = int(messages[index].find('a', class_='tgme_widget_message_date').get('href').split('/')[-1])
            if msg_id <= channel.last_message_id:
                continue

            logger.info(f'Message №{index}:')
            try:
                message = messages[index].find('div', class_='tgme_widget_message_text js-message_text').get_text()
                logger.info(f"New message [{msg_id}]: {message[:10]} ... {message[:-10:-1]}")
            except AttributeError:
                logger.info(f"Got \"bad\" message ({msg_id})")
                message = get_bad_msg_text(msg_id, channel.telegram_name)
                if message is None:
                    logger.info(f"Didn't got \"bad\" message ({msg_id})")

            words_num = len(message.split())
            if words_num < MAX_WORDS_NUM:  # todo: Решить, что делать в таком случае?, сохранение нового id
                logger.info(f"Message {msg_id} didn't add to DB (words_num={words_num})")
                continue

            msg_datetime = datetime.fromisoformat(messages[index].find('time', class_='time').get('datetime'))

            # todo: Реализовать выявление плохих сообщений и их добавление в messages_to_summarize
            summarize_and_save_messages(db, channel, message, msg_id, msg_datetime)
            update_last_message_id(db, channel, last_message_id)
    except Exception as e:
        logger.error(f"Error processing new messages for channel {channel.telegram_name}: {e}")


def summarize_and_save_messages(db, channel: Channel, message: str, msg_id: int, msg_datetime: datetime):
    try:  # noqa
        summarized_msg = get_summarized_msg(message)
        msg_url = f"https://t.me/{channel.telegram_name}/{msg_id}"
        wrapped_data = WrappedUrl(id=uuid.uuid4(), url=msg_url)  # noqa
        wrapped_url_id = WrappedUrlService.add_wrapped_url(db=db, data=wrapped_data)
        message_data = Message(id=uuid.uuid4(), telegram_id=msg_id, created_at=datetime.now(),
                               summary=summarized_msg, channel_id=channel.id, sent_at=msg_datetime,
                               wrapped_url_id=wrapped_url_id)
        MessageService.add_message(db=db, data=message_data)
        logger.info(f"Message [{msg_id}] summarized and saved to database.")
    except RateLimitError:
        logger.error(f"OpenAPI billing error. Please pay for using gpt")
    except Exception as e:
        logger.error(f"Error summarizing or saving message [{msg_id}]: {e}")


def update_last_message_id(db, channel: Channel, last_public_message_id: int):
    try:
        data = Channel(id=channel.id, telegram_name=channel.telegram_name, created_at=channel.created_at,
                       last_message_id=last_public_message_id)
        ChannelService.update_channel_id(db, data)
        logger.info(f"Last message ID ({last_public_message_id}) updated successfully.")
    except Exception as e:
        logger.error(f"Error updating last message ID: {e}")


def main():
    while True:
        try:
            logger.info("Starting a task...\n")
            # Получение списка каналов из базы данных
            with next(get_db()) as db:
                channels = db.query(Channels).all()

            # Вызов основной логики
            for channel in channels:
                try:
                    # Открываем новое подключение к базе данных для каждого канала
                    with next(get_db()) as db:
                        process_channel(db, channel)
                        print()  #
                except Exception as e:
                    logger.error(f"Error processing channel {channel}: {e}")
        except Exception as e:
            logger.error(f"Error during task execution: {e}")

        logger.info("Waiting for next launch in 1 hour...")
        time.sleep(900)
        logger.info("45 minutes left...")
        time.sleep(900)
        logger.info("30 minutes left...")
        time.sleep(900)
        logger.info("15 minutes left...")


if __name__ == "__main__":
    main()
