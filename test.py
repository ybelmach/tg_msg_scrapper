import os
from openai import OpenAI

from config import OPENAI_API_KEY

client = OpenAI(
    api_key=OPENAI_API_KEY,
)

msg = """🌐 Использование глобальной контрольной группы на практике: тонкости, нюансы, подводные камни
Как оценить эффект от совокупности изменений в продукте? Глобальная контрольная группа поможет увидеть результат в динамике, но есть ряд особенностей ее применения на практике."""

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

print(chat_completion.choices[0].message.content)
