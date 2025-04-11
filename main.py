from flask import Flask, request, jsonify
import requests
import yt_dlp
import re
import os
from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from handlers.handlers_video import handle_video
from handlers.handlers_reels import handle_transcribe
from handlers.handlers_rewrite import handle_rewrite
from handlers.handlers_capcut import handle_capcut
from handlers.handlers_subtitles import handle_subtitles
from handlers.handlers_thumbnail import handle_thumbnail
from handlers.handlers_publish import handle_publish
from handlers.handlers_voice import handle_voice
from handlers.handlers_text import handle_text
from handlers.handlers_image import handle_image
from handlers.handlers_plan import handle_plan
from handlers.handlers_pay import handle_pay
from handlers.handlers_support import handle_support
from handlers.utils import TELEGRAM_API_URL  # или передай как параметр
from handlers.handlers_transcribe import (
    handle_transcribe_mode,
    handle_transcribe_input
)

app = Flask(__name__)
BOT_TOKEN = os.environ.get('BOT_TOKEN')
OPENAI_API_KEY = os.environ.get('OPENAI_API_KEY')
TELEGRAM_API_URL = f'https://api.telegram.org/bot{BOT_TOKEN}/sendMessage'
TELEGRAM_FILE_API = f'https://api.telegram.org/file/bot{BOT_TOKEN}/'

@app.route('/')
def index():
    return 'Бот работает!'

@app.route('/telegram', methods=['POST'])
def telegram_webhook():
    data = request.get_json()
    print("\U0001F525 Получены данные от Telegram:", data)

    # Обработка callback-кнопок
    if 'callback_query' in data:
        callback = data['callback_query']
        chat_id = callback['message']['chat']['id']
        query_data = callback['data']
        callback_id = callback['id']

        requests.post(f"https://api.telegram.org/bot{BOT_TOKEN}/answerCallbackQuery", json={
            'callback_query_id': callback_id
        })

        handlers = {
            'video': handle_video,
            'voice': handle_voice,
            'text': handle_text,
            'image': handle_image,
            'plan': handle_plan,
            'pay': handle_pay,
            'support': handle_support,
            'transcribe': handle_transcribe,
            'rewrite': handle_rewrite,
            'capcut': handle_capcut,
            'subtitles': handle_subtitles,
            'thumbnail': handle_thumbnail,
            'publish': handle_publish
        }

        if query_data == 'smart_reels':
            send_message(chat_id, "\ud83d\udcf2 Умное создание Reels\nОтправь мне видео или ссылку. Я сделаю: транскрибацию, рерайт, субтитры, видео из шаблона, обложку и публикацию.\n\nВыбери действие:")
            keyboard = [
                [InlineKeyboardButton("\ud83c\udd24 Транскрибация", callback_data='transcribe'),
                 InlineKeyboardButton("\u270d\ufe0f Рерайт", callback_data='rewrite')],
                [InlineKeyboardButton("\ud83e\uddf9 Видео из шаблона CapCut", callback_data='capcut'),
                 InlineKeyboardButton("\ud83c\udf9e Субтитры", callback_data='subtitles')],
                [InlineKeyboardButton("\ud83d\uddbc Обложка", callback_data='thumbnail'),
                 InlineKeyboardButton("\ud83d\udce4 Постинг", callback_data='publish')]
            ]
            reply_markup = {'inline_keyboard': [[btn.to_dict() for btn in row] for row in keyboard]}
            requests.post(TELEGRAM_API_URL, json={
                'chat_id': chat_id,
                'text': 'Выбери, что сделать с видео \ud83d\udc47',
                'reply_markup': reply_markup
            })
        elif query_data in handlers:
            handlers[query_data](chat_id)

        return jsonify(success=True)

    # Обработка обычных сообщений
    if 'message' in data:
        message = data['message']
        chat_id = message['chat']['id']

        if 'video' in message or 'document' in message:
            if user_states.get(chat_id) == 'transcribe':
                handle_transcribe_input(chat_id, message)
                return jsonify(success=True)

        if 'text' in message:
            text = message['text']

            if user_states.get(chat_id) == 'transcribe':
                handle_transcribe_input(chat_id, text)
                return jsonify(success=True)

            if text.lower() == '/start':
                reply = (
                    "Привет! \ud83d\udc4b Я — твой персональный AI-ассистент..."
                    "\nГотов начать? Жми /menu \ud83d\ude0a"
                )
                send_message(chat_id, reply)

            elif text.lower() == '/menu':
                keyboard = [
                    [InlineKeyboardButton("\ud83c\udfa8 Видео", callback_data='video'),
                     InlineKeyboardButton("\ud83c\udfa7 Голос", callback_data='voice')],
                    [InlineKeyboardButton("\u270d\ufe0f Текст", callback_data='text'),
                     InlineKeyboardButton("\ud83d\uddbc Картинки", callback_data='image')],
                    [InlineKeyboardButton("\ud83d\udcc5 План", callback_data='plan'),
                     InlineKeyboardButton("\ud83d\udcb3 Оплата", callback_data='pay')],
                    [InlineKeyboardButton("\ud83d\udcf2 Умный Reels", callback_data='smart_reels')],
                    [InlineKeyboardButton("\ud83d\udee0 Поддержка", callback_data='support')]
                ]
                reply_markup = {'inline_keyboard': [[btn.to_dict() for btn in row] for row in keyboard]}
                requests.post(TELEGRAM_API_URL, json={
                    'chat_id': chat_id,
                    'text': 'Что будем делать? \ud83d\udc47',
                    'reply_markup': reply_markup
                })

            else:
                send_message(chat_id, "\u2705 Бот получил сообщение!")

    return jsonify(success=True)

def send_message(chat_id, text):
    requests.post(TELEGRAM_API_URL, json={
        'chat_id': chat_id,
        'text': text
    })

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=10000, threaded=True)
