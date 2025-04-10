# handlers_capcut.py

import os
import requests

BOT_TOKEN = os.environ.get('BOT_TOKEN')
TELEGRAM_API_URL = f'https://api.telegram.org/bot{BOT_TOKEN}/sendMessage'

def handle_capcut(chat_id):
    text = (
        "🧩 Видео из шаблона CapCut\n"
        "Отправь мне исходные данные или выбери шаблон, и я соберу Reels автоматически с помощью CapCut API."
    )
    requests.post(TELEGRAM_API_URL, json={
        'chat_id': chat_id,
        'text': text
    })
