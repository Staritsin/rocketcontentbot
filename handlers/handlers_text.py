from telegram import InlineKeyboardButton, InlineKeyboardMarkup
import requests
import os

BOT_TOKEN = os.environ.get('BOT_TOKEN')
TELEGRAM_API_URL = f'https://api.telegram.org/bot{BOT_TOKEN}/sendMessage'

def handle_text(chat_id):
    text = "✍️ Работа с текстом\nВыбери, что ты хочешь сделать с текстом:"

    keyboard = [
        [
            InlineKeyboardButton("🪄 Генерация текста", callback_data='text_generate'),
            InlineKeyboardButton("✍️ Рерайт", callback_data='text_rewrite')
        ],
        [
            InlineKeyboardButton("📜 Сценарий", callback_data='text_script')
        ]
    ]

    reply_markup = {'inline_keyboard': [[btn.to_dict() for btn in row] for row in keyboard]}

    requests.post(TELEGRAM_API_URL, json={
        'chat_id': chat_id,
        'text': text,
        'reply_markup': reply_markup
    })
