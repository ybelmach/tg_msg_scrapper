from datetime import datetime

import requests
from bs4 import BeautifulSoup
from openai import OpenAI
from config import OPENAI_API_KEY, MAX_WORDS_NUM
from logging_config import logger


def get_last_message_id(messages: list) -> int | None:
    """
    Find last message ID in telegram chat.
    """
    try:
        try:
            last_message_id = int(messages[-1].find('a', class_='tgme_widget_message_date').get('href').split('/')[-1])
        except IndexError:
            last_message_id = 0
        logger.info(f"Last message ID found: {last_message_id}")
        return last_message_id
    except Exception as e:
        logger.error(f"Error finding the last message: {e}")


def get_bad_msg_text(msg_id: int, tg_name: str) -> str:
    """
    Извлекает текст сообщения, если оно не поддерживается в браузере.
    """
    try:
        url = f"https://t.me/{tg_name}/{msg_id}"
        response = requests.post(url)
        soup = BeautifulSoup(response.text, 'lxml')
        message = soup.find('meta', property='og:description').get('content')
        print(f"Message: {message[:10]}")
        return message
    except requests.RequestException as e:
        logger.error(f"Connection error while fetching message {msg_id}: {e}")
    except Exception as e:
        logger.error(f"Error parsing message {msg_id}: {e}")


def get_summarized_msg(msg: str) -> str:
    """
    Суммирует текст сообщения до 10 слов с использованием OpenAI API.
    """
    try:
        client = OpenAI(api_key=OPENAI_API_KEY)
        prompt = f"""Составь краткий анонс для сообщения ниже, состоящий не более чем из {MAX_WORDS_NUM} слов.
        Анонс должен давать краткое саммари сообщения, не упуская важные детали.
        Включи в анонс ключевые факты из сообщения, если нужно.
        Если в сообщении есть абзац точно и емко описывающий все сообщение, используй его в качестве анонса. 

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
