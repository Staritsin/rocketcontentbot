import os
import requests
from flask import request
from telegram import InlineKeyboardButton, InlineKeyboardMarkup

BOT_TOKEN = os.environ.get('BOT_TOKEN')

# Текстовый ответ по кнопке 📤 Постинг
def handle_publish(chat_id):
    TELEGRAM_API_URL = f'https://api.telegram.org/bot{BOT_TOKEN}/sendMessage'
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

# Финальная отправка Reels + кнопки
def publish_reels(chat_id, video_url):
    TELEGRAM_API_URL = f"https://api.telegram.org/bot{BOT_TOKEN}/sendVideo"
    keyboard = [
        [InlineKeyboardButton("🌟 Всё получилось", callback_data='success')],
        [InlineKeyboardButton("🔙 В меню", callback_data='menu')]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard).to_dict()

    requests.post(TELEGRAM_API_URL, json={
        "chat_id": chat_id,
        "video": video_url,
        "caption": "🎬 Твой Reels готов к публикации!",
        "reply_markup": reply_markup
    })
