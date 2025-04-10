import requests
import os
from telegram import InlineKeyboardButton

BOT_TOKEN = os.environ.get('BOT_TOKEN')
TELEGRAM_API_URL = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"

def handle_menu(chat_id):
    keyboard = [
        [
            InlineKeyboardButton("🎬 Работа с видео", callback_data='video'),
            InlineKeyboardButton("🎧 Работа с голосом", callback_data='voice')
        ],
        [
            InlineKeyboardButton("✍️ Работа с текстом", callback_data='text'),
            InlineKeyboardButton("🖼 Работа с изображениями", callback_data='image')
        ],
        [
            InlineKeyboardButton("📅 Контент-план", callback_data='plan'),
            InlineKeyboardButton("💳 Оплатить", callback_data='pay')
        ],
        [
            InlineKeyboardButton("📲 Создать Reels по видео/ссылке", callback_data='smart_reels')
        ],
        [
            InlineKeyboardButton("🛠 Техподдержка", callback_data='support')
        ]
    ]

    reply_markup = {'inline_keyboard': [[btn.to_dict() for btn in row] for row in keyboard]}

    requests.post(TELEGRAM_API_URL, json={
        'chat_id': chat_id,
        'text': 'Что будем делать? Выбери из меню ниже 👇',
        'reply_markup': reply_markup
    })
