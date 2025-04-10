# handlers_subtitles.py

import os
import requests

BOT_TOKEN = os.environ.get('BOT_TOKEN')
TELEGRAM_API_URL = f'https://api.telegram.org/bot{BOT_TOKEN}/sendMessage'

def handle_subtitles(chat_id):
    text = (
        "🎞 Субтитры для видео\n"
        "Отправь видео или текст — я наложу субтитры автоматически."
    )
    requests.post(TELEGRAM_API_URL, json={
        'chat_id': chat_id,
        'text': text
    })

def handle_publish(chat_id):
    text = (
        "📤 Публикация контента\n"
        "Выбери, куда опубликовать: Instagram, Telegram, VK и другие.\n"
        "Скоро добавим автоматический постинг."
    )
    requests.post(TELEGRAM_API_URL, json={
        'chat_id': chat_id,
        'text': text
    })
