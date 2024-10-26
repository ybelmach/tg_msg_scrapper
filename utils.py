import requests
from bs4 import BeautifulSoup
from openai import OpenAI

from config import OPENAI_API_KEY


def find_last_message(soup: BeautifulSoup) -> int:
    # Находим все сообщения
    messages = soup.find_all('div', class_='tgme_widget_message')

    if messages:  # Проверяем, что сообщения найдены
        last_message = messages[-1]

        # Проверяем, существует ли атрибут 'data-post'
        if 'data-post' in last_message.attrs:
            last_message_id = last_message['data-post']
            last_message_id = int(last_message_id.split('/')[-1])  # Извлекаем ID после '/'
            print(last_message_id)
        else:
            raise "Attribute 'data-post' not found in the last message."
    else:
        print("No messages found.")
        last_message_id = 0
    return last_message_id


def find_bad_msgs(soup: BeautifulSoup):
    message_ids = []
    messages = soup.find_all('div', class_='message_media_not_supported')

    for message in messages:
        link = message.find('a', class_='message_media_view_in_telegram')
        if link is not None:
            if link.text == 'VIEW IN TELEGRAM':
                message_id = link['href'].split('/')[-1]
                try:
                    message_id = int(message_id)
                except ValueError:
                    continue
                message_ids.append(message_id)
    return message_ids


# Доделать
def get_bad_msg_text(msg_id: int, msg_url: str) -> str:
    try:
        response = requests.get(msg_url)
    except Exception as e:
        print(f"Connection error: {e}")
    soup = BeautifulSoup(response.text, 'lxmx')
    text = soup.find('div', class_='tgme_widget_message_text js-message_text')
    # for i in range(1, messages_number + 1):
    #     msg = messages[-i].get_text()
    #     messages_to_summarize.append(msg)
    #     print(f"\t[{i}]: {msg}")


def get_summarized_msg(msg: str):
    client = OpenAI(
        api_key=OPENAI_API_KEY,
    )

    message = f"""Представь что ты копирайтер.
    Я предоставлю тебе текст сообщения, а ты должен выделить из него главное размером до 10 слов.
    В ответе предоставь только результат.

    <message>
    {msg}
    </message>
    """

    chat_completion = client.chat.completions.create(
        messages=[
            {
                "role": "user",
                "content": message,
            }
        ],
        model="gpt-4o-mini",
    )

    summarized_message = chat_completion.choices[0].message.content
    return summarized_message
