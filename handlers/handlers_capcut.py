import requests
import os
from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from handlers.state import user_states
from handlers.handlers_voice import handle_voice_transcription
from handlers.handlers_rewrite import handle_rewrite_transcript
from handlers.utils import TELEGRAM_API_URL

# 🔹 Шаг 1. Пользователь отправил видео или ссылку
def handle_capcut(chat_id):
    text = (
        "🎬 Умный CapCut-сборщик Reels\n"
        "Отправь мне видео или ссылку на Reels/YouTube. "
        "Я сделаю для тебя ролик с шаблоном, футажами, субтитрами и публикацией."
    )
    requests.post(f"{TELEGRAM_API_URL}/sendMessage", json={
        'chat_id': chat_id,
        'text': text
    })

# 🔹 Шаг 2. Обработка входного контента (видео или ссылка)
def process_capcut_input(chat_id, message):
    try:
        if 'video' in message:
            file_id = message['video']['file_id']
            handle_voice_transcription(chat_id, file_id)

        elif 'text' in message:
            text = message['text']
            if text.startswith("http"):
                user_states[chat_id] = {'video_link': text}
                requests.post(f"{TELEGRAM_API_URL}/sendMessage", json={
                    'chat_id': chat_id,
                    'text': "📤 Начинаю обработку ссылки..."
                })
                # TODO: сюда добавишь скачивание видео через yt_dlp
            else:
                raise ValueError("Это не ссылка и не видео")

        else:
            raise ValueError("Не удалось определить тип входных данных")

        # 🔄 Заглушка следующего шага
        keyboard = [[InlineKeyboardButton("🧠 Сделать рерайт", callback_data='rewrite_transcript')]]
        reply_markup = {'inline_keyboard': [[btn.to_dict() for btn in row] for row in keyboard]}
        requests.post(f"{TELEGRAM_API_URL}/sendMessage", json={
            'chat_id': chat_id,
            'text': "✍️ Готов текст. Хочешь рерайт?",
            'reply_markup': reply_markup
        })

    except Exception as e:
        requests.post(f"{TELEGRAM_API_URL}/sendMessage", json={
            'chat_id': chat_id,
            'text': f"❌ Ошибка обработки: {e}"
        })
