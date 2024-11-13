import time
import uuid
from datetime import datetime

from config import MAX_WORDS_NUM
from db.models import Channels
from db.database import get_db
from db.services import ChannelService, MessageService, WrappedUrlService
from logging_config import logger
from utils import find_last_message, get_summarized_msg, get_photos_num, get_time
from schemas import Channel, Message, WrappedUrl
import requests
from bs4 import BeautifulSoup


def process_channel(db, channel):
    try:
        url = f"https://t.me/s/{channel.telegram_name}"
        response = requests.get(url)
        response.raise_for_status()
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
        last_message_id = find_last_message(soup, channel)
        photos_num = get_photos_num(soup=soup, start_id=last_message_id)
        if photos_num:
            logger.info(f"Photos found: {photos_num}")
            last_message_id += photos_num
        else:
            logger.info("No photos found.")
        data = Channel(id=channel.id, telegram_name=channel.telegram_name, created_at=channel.created_at,
                       last_message_id=last_message_id)
        ChannelService.update_channel_id(db, data)
        logger.info(f"Last message ID ({last_message_id}) added to database successfully.")
    except Exception as e:
        logger.error(f"Error parsing or updating last message ID: {e}")


def process_new_messages(db, channel, soup):
    try:
        last_public_message_id = find_last_message(soup, channel)
        messages = soup.find_all('div', class_='tgme_widget_message_text js-message_text')
        messages_to_summarize = []
        logger.info(f"Last message in DB: {channel.last_message_id}, new last message: {last_public_message_id}")
        if last_public_message_id > channel.last_message_id:

            msg_ids = []
            photos_num = get_photos_num(soup=soup, start_id=channel.last_message_id + 1)
            try:
                for i in range(last_public_message_id - channel.last_message_id - photos_num):  # 1 2 3 4 5 6 7 8 9
                    if i != 0:
                        try:
                            current_id = msg_ids[-1][0] + msg_ids[-1][1] + 1
                        except IndexError as e:
                            logger.error(f"ERROR msg_ids index error {e}")
                            continue
                        photo_num = get_photos_num(soup=soup, msg_id=current_id)
                        msg_ids.append((current_id, photo_num))
                    else:
                        photo_num = get_photos_num(soup=soup, msg_id=channel.last_message_id + 1)
                        msg_ids.append((channel.last_message_id + 1, photo_num))
            except Exception as e:
                logger.error(f"Error parsing or updating last message ID (loop error): {e}")
            msg_ids.reverse()
            logger.info(f"New messages id's: {msg_ids}")

            prev_photo_nums = 0
            for i, msg_ids_tuple in enumerate(msg_ids):
                msg_id, photo_num = msg_ids_tuple
                if i != 0:
                    prev_photo_nums += msg_ids[i-1][1]
                index = -(i+1+prev_photo_nums)
                msg = messages[index].get_text()

                words_num = len(msg.split())
                if words_num < MAX_WORDS_NUM:  #
                    logger.info(f"Message {msg_id} didn't add to DB (words_num={words_num})")
                    # update_last_message_id(db, channel, last_public_message_id)  # + photo_num
                    continue
                else:
                    messages_to_summarize.append((msg_id, msg))
                # Реализовать выявление плохих сообщений и их добавление в messages_to_summarize
                # bad_numbers: List[int] = find_bad_msgs(soup)
                # for number in bad_numbers:
                #     bad_msg_text = get_bad_msg_text(number, msg_url)
                #     messages_to_summarize.append(bad_msg_text)
                logger.info(f"New message [{msg_id}] added to list: {msg}")

        if messages_to_summarize:
            process = summarize_and_save_messages(db, channel, messages_to_summarize, soup)
            if process:
                update_last_message_id(db, channel, last_public_message_id)
            else:
                logger.error(f"Message didn't save correctly, skipping summarizing")

    except Exception as e:
        logger.error(f"Error processing new messages for channel {channel.telegram_name}: {e}")


def update_last_message_id(db, channel, last_public_message_id):
    try:
        data = Channel(id=channel.id, telegram_name=channel.telegram_name, created_at=channel.created_at,
                       last_message_id=last_public_message_id)
        ChannelService.update_channel_id(db, data)
        logger.info(f"Last message ID ({last_public_message_id}) updated successfully.")
        return True
    except Exception as e:
        logger.error(f"Error updating last message ID: {e}")


def summarize_and_save_messages(db, channel, messages_to_summarize, soup):
    for photo_num, msg_id, msg in messages_to_summarize:
        try:
            summarized_msg = get_summarized_msg(msg)
            msg_url = f"https://t.me/{channel.telegram_name}/{msg_id}"
            msg_time = get_time(soup=soup, save_msg_id=msg_id-photo_num)
            wrapped_data = WrappedUrl(id=uuid.uuid4(), url=msg_url)
            wrapped_url_id = WrappedUrlService.add_wrapped_url(db=db, data=wrapped_data)
            message_data = Message(id=uuid.uuid4(), telegram_id=msg_id, created_at=datetime.now(),
                                   summary=summarized_msg, url=msg_url, channel_id=channel.id, sended_at=msg_time,
                                   wrapped_url_id=wrapped_url_id)
            MessageService.add_message(db=db, data=message_data)
            logger.info(f"Message [{msg_id}] summarized and saved to database.")
        except Exception as e:
            logger.error(f"Error summarizing or saving message [{msg_id}]: {e}")
    return True


def main():
    try:
        with next(get_db()) as db:
            channels = db.query(Channels).all()
    except Exception as e:
        logger.error(f"Error fetching channels from database: {e}")
    while True:
        try:
            logger.info("Starting a task...")
            # Вызов основной логики
            for channel in channels:
                process_channel(db, channel)
                print()  #
        except Exception as e:
            logger.error(f"Task execution error: {e}")

        logger.info("Waiting for next launch in 1 hour...")
        time.sleep(900)
        logger.info("45 minutes left...")
        time.sleep(900)
        logger.info("30 minutes left...")
        time.sleep(900)
        logger.info("15 minutes left...")


if __name__ == "__main__":
    main()
