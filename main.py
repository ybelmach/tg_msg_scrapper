import uuid
from datetime import datetime

from db.models import Channels
from db.database import get_db

import requests
from bs4 import BeautifulSoup

from db.services import updating_id, adding_msg
from schemas import Channel, Message
from utils import find_last_message, find_bad_msgs, get_bad_msg_text, get_summarized_msg

try:
    with next(get_db()) as db:
        channels = db.query(Channels).all()
except Exception as e:
    print(f"Error: {e}")
for channel in channels:
    try:
        url = f"https://t.me/s/{channel.telegram_name}"
        response = requests.get(url)
    except Exception as e:
        raise f"Connection error: {e}"
    soup = BeautifulSoup(response.text, 'html.parser')
    print(url)

    if channel.last_message_id is None:
        try:
            last_message_id = find_last_message(soup)
        except Exception as e:
            raise f"Error with parsing last message id: {e}"

        # Добавление id в БД
        data = Channel(id=channel.id, telegram_id=channel.telegram_id, telegram_name=channel.telegram_name,
                       created_at=channel.created_at, last_message_id=last_message_id)
        try:
            updating_id(db, data)
        except Exception as e:
            raise f"Error with writing to database: {e}"
        print("Writing id to database successfully.")

        # Отображение последних 3 в дайджесте

    else:
        messages = soup.find_all('div', class_='tgme_widget_message_text js-message_text')
        last_public_message_id = find_last_message(soup)
        last_message_id = channel.last_message_id
        messages_number = last_public_message_id - last_message_id

        messages_to_summarize = []
        # bad_numbers: List[int] = find_bad_msgs(soup)
        # for number in bad_numbers:
        #     bad_msg_text = get_bad_msg_text(number, msg_url)
        #     messages_to_summarize.append(bad_msg_text)

        for i in range(1, messages_number + 1):
            temp = ()
            msg = messages[-i].get_text()
            messages_to_summarize.append((last_message_id + i, msg))
            print(f"\t[{last_message_id + i}]: {msg}")

        if len(messages_to_summarize) > 0:
            # Добавление id в БД
            data = Channel(id=channel.id, telegram_id=channel.telegram_id, telegram_name=channel.telegram_name,
                           created_at=channel.created_at, last_message_id=last_public_message_id)
            try:
                updating_id(db, data)
            except Exception as e:
                raise f"Error with writing to database: {e}"
            print("Writing id to database successfully.")

            for element in messages_to_summarize:
                # Суммаризация сообщений
                msg_id, msg = element[0], element[1]
                summarized_msg = get_summarized_msg(msg)
                print(f"\t[{msg_id}]: {summarized_msg}")
                msg_url = f"https://t.me/{channel.telegram_name}/{msg_id}"

                # Добавление сообщения в БД
                data = Message(id=str(uuid.uuid4()), telegram_id=msg_id, created_at=datetime.now(),
                               summary=summarized_msg, uri=msg_url, channel_id=channel.id)
                try:
                    adding_msg(db, data)
                except Exception as e:
                    raise f"Error with writing to database: {e}"
                print("Writing summarized message to database successfully.")
