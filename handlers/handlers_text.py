# handlers_text.py

import os
import requests

BOT_TOKEN = os.environ.get('BOT_TOKEN')
TELEGRAM_API_URL = f'https://api.telegram.org/bot{BOT_TOKEN}/sendMessage'

def handle_text(chat_id):
    text = (
        "✍️ Работа с текстом\n"
        "Отправь мне текст или команду:\n"
        "- /rewrite – рерайт текста\n"
        "- /script – создать сценарий\n"
        "- /generate – сгенерировать пост или статью"
    )
    requests.post(TELEGRAM_API_URL, json={
        'chat_id': chat_id,
        'text': text
    })

