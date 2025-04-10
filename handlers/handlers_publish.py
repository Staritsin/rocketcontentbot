import os
import requests
from flask import request

BOT_TOKEN = os.environ.get('BOT_TOKEN')
TELEGRAM_API_URL = f'https://api.telegram.org/bot{BOT_TOKEN}/sendMessage'

def handle_publish(chat_id):
    text = (
        "📤 Постинг\n\n"
        "Я готов опубликовать контент в твои соцсети!\n"
        "Подключи нужные платформы: Telegram, Instagram, VK и т.д.\n"
        "И я сделаю это автоматически по расписанию или вручную ✨"
    )
    requests.post(TELEGRAM_API_URL, json={
        'chat_id': chat_id,
        'text': text
    })
