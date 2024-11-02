import requests
from bs4 import BeautifulSoup
from openai import OpenAI
from config import OPENAI_API_KEY
from logging_config import logger


def find_last_message(soup: BeautifulSoup, channel) -> int:
    """
    Ищет последний ID сообщения на странице.
    """
    try:
        last_message_id = 0
        messages = soup.find_all('div', class_='tgme_widget_message')
        if messages:
            last_message = messages[-1]
            if 'data-post' in last_message.attrs:
                last_message_id = last_message['data-post'].split('/')[-1]
                logger.info(f"Last message ID found: {last_message_id}")
            else:
                logger.error("Attribute 'data-post' not found in the last message.")
        else:
            logger.info("No messages found.")
        return int(last_message_id)
    except Exception as e:
        logger.error(f"Error finding the last message: {e}")


def find_bad_msgs(soup: BeautifulSoup):
    """
    Ищет сообщения, содержащие медиа или другой контент, который не поддерживается.
    """
    try:
        message_ids = []
        messages = soup.find_all('div', class_='message_media_not_supported')

        for message in messages:
            link = message.find('a', class_='message_media_view_in_telegram')
            if link and link.text == 'VIEW IN TELEGRAM':
                message_id = link['href'].split('/')[-1]
                try:
                    message_id = int(message_id)
                    message_ids.append(message_id)
                except ValueError:
                    logger.warning(f"Invalid message ID format: {message_id}")
        logger.info(f"Found {len(message_ids)} unsupported messages.")
        return message_ids
    except Exception as e:
        logger.error(f"Error finding bad messages: {e}")


def get_photos_num(soup, start_id: int | None = None, msg_id: int = 0) -> int:
    logger.info(f"Starting finding numbers of images...")

    messages = soup.find_all('div', class_='tgme_widget_message')
    if messages:
        photos_num = 0
        for message in messages:
            if 'data-post' in message.attrs:
                message_id = int(message['data-post'].split('/')[-1])
                if start_id:
                    if start_id > message_id:
                        continue
                    current_photo_num = len(message.find_all(
                        "a",
                        class_='tgme_widget_message_photo_wrap grouped_media_wrap blured js-message_photo'
                    ))
                    photos_num += current_photo_num - 1
                    logger.info(f"Additional photos number in message {message_id}: {current_photo_num}")
                else:
                    if msg_id == message_id:
                        photo_num = len(message.find_all(
                            "a",
                            class_='tgme_widget_message_photo_wrap grouped_media_wrap blured js-message_photo'
                        )) - 1
                        if photo_num < 0:
                            photo_num = 0
                        logger.info(f"Additional photos number in one message ({msg_id}): {photo_num}")
                        return photo_num
            else:
                logger.error("Attribute 'data-post' not found in the last message.")
        if photos_num < 0:
            photos_num = 0
        logger.info(f"Additional photos number: {photos_num}")
        return photos_num
    else:
        logger.info("No messages found.")


# Доделать
def get_bad_msg_text(msg_id: int, msg_url: str) -> str:
    """
    Извлекает текст сообщения, если оно не поддерживается в Telegram.
    """
    try:
        response = requests.get(msg_url)
        response.raise_for_status()  # Проверка на ошибки запроса
        soup = BeautifulSoup(response.text, 'lxml')
        text = soup.find('div', class_='tgme_widget_message_text js-message_text')
        # for i in range(1, messages_number + 1):
        #     msg = messages[-i].get_text()
        #     messages_to_summarize.append(msg)
        #     print(f"\t[{i}]: {msg}")
    except requests.RequestException as e:
        logger.error(f"Connection error while fetching message {msg_id}: {e}")
    except Exception as e:
        logger.error(f"Error parsing message {msg_id}: {e}")
    return 'test'


def get_summarized_msg(msg: str) -> str:
    """
    Суммирует текст сообщения до 10 слов с использованием OpenAI API.
    """
    try:
        client = OpenAI(api_key=OPENAI_API_KEY)
        prompt = f"""Представь что ты копирайтер.
        Я предоставлю тебе текст сообщения, а ты должен выделить из него главное размером до 10 слов.
        В ответе предоставь только результат.
    
        <message>
        {msg}
        </message>
        """

        response = client.chat.completions.create(
            messages=[{"role": "user", "content": prompt, }],
            model="gpt-4o-mini",
        )

        summarized_message = response.choices[0].message.content
        logger.info(f"Summarized message: {summarized_message}")
        return summarized_message
    except Exception as e:
        logger.error(f"Error summarizing message: {e}")
