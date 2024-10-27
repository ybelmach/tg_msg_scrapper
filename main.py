import time
import uuid
from datetime import datetime

from config import MAX_WORDS_NUM
from db.models import Channels
from db.database import get_db
from db.services import ChannelService, MessageService
from utils import find_last_message, get_summarized_msg
from schemas import Channel, Message
import requests
from bs4 import BeautifulSoup
import logging

# Настройка логирования
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def process_channel(db, channel):
    try:
        url = f"https://t.me/s/{channel.telegram_name}"
        response = requests.get(url)
        response.raise_for_status()  # Проверка статуса ответа
        soup = BeautifulSoup(response.text, 'lxml')
        logger.info(f"Processing URL: {url}")

        if channel.last_message_id is None:
            process_last_message(db, channel, soup)
            # Отображение последних 3 (MSG_NUM) в дайджесте
        else:
            process_new_messages(db, channel, soup)

    except requests.RequestException as e:
        logger.error(f"Connection error: {e}")
    except Exception as e:
        logger.error(f"Error processing channel {channel.telegram_name}: {e}")


def process_last_message(db, channel, soup):
    try:
        last_message_id = find_last_message(soup)
        data = Channel(id=channel.id, telegram_id=None, telegram_name=channel.telegram_name, created_at=channel.created_at,
                       last_message_id=last_message_id)
        ChannelService.update_channel_id(db, data)
        logger.info("Last message ID added to database successfully.")
    except Exception as e:
        logger.error(f"Error parsing or updating last message ID: {e}")


def process_new_messages(db, channel, soup):
    try:
        last_public_message_id = find_last_message(soup)
        messages = soup.find_all('div', class_='tgme_widget_message_text js-message_text')
        messages_to_summarize = []

        for i in range(1, last_public_message_id - channel.last_message_id + 1):
            msg = messages[-i].get_text()
            words_num = len(msg.split())
            if words_num < MAX_WORDS_NUM:
                summarized_msg, msg_id = msg, channel.last_message_id + i
                try:
                    msg_url = f"https://t.me/{channel.telegram_name}/{msg_id}"
                    message_data = Message(id=uuid.uuid4(), created_at=datetime.now(), summary=summarized_msg,
                                           url=msg_url, channel_id=channel.id)
                    MessageService.add_message(db, message_data)
                    logger.info(f"Message [{msg_id}] saved to database without summarizing.")
                except Exception as e:
                    logger.error(f"Error saving message without summarizing [{msg_id}]: {e}")
            else:
                messages_to_summarize.append((channel.last_message_id + i, msg))
            # Реализовать выявление плохих сообщений и их добавление в messages_to_summarize
            # bad_numbers: List[int] = find_bad_msgs(soup)
            # for number in bad_numbers:
            #     bad_msg_text = get_bad_msg_text(number, msg_url)
            #     messages_to_summarize.append(bad_msg_text)
            logger.info(f"New message [{channel.last_message_id + i}]: {msg}")

        if messages_to_summarize:
            summarize_and_save_messages(db, channel, messages_to_summarize)
            update_last_message_id(db, channel, last_public_message_id)

    except Exception as e:
        logger.error(f"Error processing new messages for channel {channel.telegram_name}: {e}")


def update_last_message_id(db, channel, last_public_message_id):
    try:
        data = Channel(id=channel.id, telegram_name=channel.telegram_name, created_at=channel.created_at,
                       last_message_id=last_public_message_id)
        ChannelService.update_channel_id(db, data)
        logger.info("Last message ID updated successfully.")
    except Exception as e:
        logger.error(f"Error updating last message ID: {e}")


def summarize_and_save_messages(db, channel, messages_to_summarize):
    for msg_id, msg in messages_to_summarize:
        try:
            summarized_msg = get_summarized_msg(msg)
            msg_url = f"https://t.me/{channel.telegram_name}/{msg_id}"
            message_data = Message(id=uuid.uuid4(), created_at=datetime.now(), summary=summarized_msg, url=msg_url,
                                   channel_id=channel.id)
            MessageService.add_message(db, message_data)
            logger.info(f"Message [{msg_id}] summarized and saved to database.")
        except Exception as e:
            logger.error(f"Error summarizing or saving message [{msg_id}]: {e}")


def main():
    try:
        with next(get_db()) as db:
            channels = db.query(Channels).all()
    except Exception as e:
        logger.error(f"Error fetching channels from database: {e}")
    while True:
        try:
            logging.info("Starting a task...")
            # Вызов основной логики
            for channel in channels:
                process_channel(db, channel)
        except Exception as e:
            logging.error(f"Task execution error: {e}")

        logging.info("Waiting for next launch in 1 hour...")
        time.sleep(900)
        logging.info("45 minutes left...")
        time.sleep(900)
        logging.info("30 minutes left...")
        time.sleep(900)
        logging.info("15 minutes left...")


if __name__ == "__main__":
    main()
