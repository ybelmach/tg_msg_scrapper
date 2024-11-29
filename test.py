from datetime import datetime

import requests
from bs4 import BeautifulSoup

telegram_name = 'jsvdoodhrllr'

url = f"https://t.me/s/{telegram_name}" # noqa
print(f"Processing URL: {url}")
response = requests.get(url)
response.raise_for_status()
soup = BeautifulSoup(response.text, 'lxml')

messages = (soup.find_all('section', class_='tgme_channel_history js-message_history')[0]
            .find_all('div', class_='tgme_widget_message_wrap js-widget_message_wrap'))



for index in range(-len(messages), 0):  # noqa
    # print(messages[index])
    print(f'index: {index}')


    try:
        print(messages[index].find('div', class_='tgme_widget_message_text js-message_text').get_text())  # Text
    except AttributeError as e:
        print("Message only can be view in telegram")

    print(int(messages[index].find('a', class_='tgme_widget_message_date').get('href').split('/')[-1]))  # msg_id

    print(datetime.fromisoformat(messages[index].find('time', class_='time').get('datetime')))  # datetime
    print()

try:
    print(messages[-1].find('a', class_='tgme_widget_message_date').get('href').split('/')[-1])  # Last msg id
except IndexError as e:
    print("Channel haven't got any messages.")
