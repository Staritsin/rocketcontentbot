# handlers_subtitles.py

import os
import requests

BOT_TOKEN = os.environ.get('BOT_TOKEN')
TELEGRAM_API_URL = f'https://api.telegram.org/bot{BOT_TOKEN}/sendMessage'

def handle_subtitles(chat_id):
    text = (
        "🎞 Субтитры к видео\n"
        "Я создам субтитры на основе твоего видео или текста.\n"
        "Просто отправь материал — и я подготовлю субтитры для вставки."
    )
    requests.post(TELEGRAM_API_URL, json={
        'chat_id': chat_id,
        'text': text
    })
