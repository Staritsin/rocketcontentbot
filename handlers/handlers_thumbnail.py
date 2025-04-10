# handlers_thumbnail.py

import os
import requests

BOT_TOKEN = os.environ.get('BOT_TOKEN')
TELEGRAM_API_URL = f'https://api.telegram.org/bot{BOT_TOKEN}/sendMessage'

def handle_thumbnail(chat_id):
    text = (
        "🖼 Обложка для видео\n"
        "Хочешь яркую обложку для Reels? Отправь тему или текст — я сгенерирую изображение."
    )
    requests.post(TELEGRAM_API_URL, json={
        'chat_id': chat_id,
        'text': text
    })
