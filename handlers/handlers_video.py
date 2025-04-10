import os
import requests
from flask import request

BOT_TOKEN = os.environ.get('BOT_TOKEN')
TELEGRAM_API_URL = f'https://api.telegram.org/bot{BOT_TOKEN}/sendMessage'

def handle_video(chat_id):
    text = (
        "🎬 Работа с видео\n"
        "Отправь мне ссылку на видео (Reels, TikTok, YouTube, VK и т.д.) или загрузи файл напрямую.\n"
        "Я загружу его и подготовлю для дальнейшей обработки: рерайт, субтитры, голос и т.п."
    )
    requests.post(TELEGRAM_API_URL, json={
        'chat_id': chat_id,
        'text': text
    })
