import requests
import os
from telegram import InlineKeyboardButton

BOT_TOKEN = os.environ.get('BOT_TOKEN')
TELEGRAM_API_URL = f'https://api.telegram.org/bot{BOT_TOKEN}'

user_states = {}

def handle_select_post_platform(chat_id):
    keyboard = [
        [InlineKeyboardButton("📣 Telegram", callback_data='post_telegram')],
        [InlineKeyboardButton("📸 Instagram", callback_data='post_instagram')],
        [InlineKeyboardButton("🧾 VK", callback_data='post_vk')],
        [InlineKeyboardButton("✉️ Email-рассылка", callback_data='post_email')],
        [InlineKeyboardButton("🔙 Назад", callback_data='menu')]
    ]
    reply_markup = {'inline_keyboard': [[btn.to_dict()] for btn in sum(keyboard, [])]}
    requests.post(f"{TELEGRAM_API_URL}/sendMessage", json={
        'chat_id': chat_id,
        'text': "📤 Куда публикуем пост?",
        'reply_markup': reply_markup
    })

def handle_post_format(chat_id, platform):
    text = user_states.get(chat_id, {}).get('last_transcript', '')
    if not text:
        requests.post(f"{TELEGRAM_API_URL}/sendMessage", json={
            'chat_id': chat_id,
            'text': "❌ Нет текста для публикации."
        })
        return

    if platform == 'telegram':
        post = f"📣 Пост для Telegram:\n\n{text[:4096]}"
    elif platform == 'instagram':
        post = f"📸 Пост для Instagram:\n\n{text[:2200]}\n\n#контент #публикация"
    elif platform == 'vk':
        post = f"🧾 Пост для VK:\n\n{text}\n\n👉 Переходи по ссылке!"
    elif platform == 'email':
        post = f"✉️ Шаблон Email:\n\nЗдравствуйте!\n\n{text}\n\nПерейдите по кнопке ниже 👉"

    else:
        post = "⚠️ Неизвестная платформа."

    requests.post(f"{TELEGRAM_API_URL}/sendMessage", json={
        'chat_id': chat_id,
        'text': post
    })
