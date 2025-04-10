import os
import requests
from flask import request

BOT_TOKEN = os.environ.get('BOT_TOKEN')
TELEGRAM_API_URL = f'https://api.telegram.org/bot{BOT_TOKEN}/sendMessage'

def handle_rewrite(chat_id):
    text = (
        "✍️ Рерайт текста\n"
        "Отправь мне текст, и я перепишу его — сделаю более цепляющим, лаконичным или адаптирую под формат Reels."
    )

    requests.post(TELEGRAM_API_URL, json={
        'chat_id': chat_id,
        'text': text
    })
