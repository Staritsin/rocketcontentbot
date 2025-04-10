from flask import Flask, request, jsonify
import requests
import yt_dlp
import re
import os
from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from handlers.handlers_video import handle_video

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

    if 'message' in data:
        chat_id = data['message']['chat']['id']
        message = data['message']

        if 'text' in message:
            text = message['text']

            if text.lower() == '/start':
                reply = (
                    "Привет! 👋 Я — твой персональный AI-ассистент для создания и управления контентом! 🎯\n\n"
                    "Вот что я могу:\n"
                    "🎥 Работаю с видео: Reels, YouTube, Shorts, Telegram, VK\n"
                    "🧠 Работаю с голосом: превращаю в текст голосовые и аудио\n"
                    "✍️ Работаю с текстом: рерайт, генерация, сценарии\n"
                    "🖼 Работаю с изображениями: создаю картинки по твоему запросу\n"
                    "📅 Помогаю с публикациями и контент-планом\n"
                    "📲 Могу создать Reels по ссылке/видео: транскрибация, рерайт, субтитры, генерация, обложка и постинг\n\n"
                    "Как работать со мной:\n"
                    "1. Нажми /menu, чтобы выбрать, что хочешь сделать.\n"
                    "2. Загрузи видео или голосовое сообщение.\n"
                    "3. Я обработаю материал и предложу варианты генерации или публикации.\n\n"
                    "Готов начать? Жми /menu 😊"
                )
                send_message(chat_id, reply)

            elif text.lower() == '/menu':
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

    elif 'callback_query' in data:
        callback = data['callback_query']
        chat_id = callback['message']['chat']['id']
        query_data = callback['data']
        callback_id = callback['id']

        # Ответ на нажатие кнопки (обязателен для Telegram)
        requests.post(f"https://api.telegram.org/bot{BOT_TOKEN}/answerCallbackQuery", json={
            'callback_query_id': callback_id
        })

        if query_data == 'video':
            handle_video(chat_id)
        elif query_data == 'voice':
            send_message(chat_id, "🎧 Работа с голосом\nОтправь голосовое сообщение — я превращу его в текст.")
        elif query_data == 'text':
            send_message(chat_id, "✍️ Работа с текстом\nОтправь мне текст или команду для генерации, рерайта или создания сценария.")
        elif query_data == 'image':
            send_message(chat_id, "🖼 Работа с изображениями\nНапиши, что ты хочешь увидеть, и я сгенерирую картинку.")
        elif query_data == 'plan':
            send_message(chat_id, "📅 Контент-план\nОтправь мне тематику, и я помогу составить план публикаций.")
        elif query_data == 'pay':
            send_message(chat_id, "💳 Оплата\nОплатить можно по ссылке: https://yourpaymentpage.com")
        elif query_data == 'support':
            send_message(chat_id, "🛠 Поддержка\nНапиши в поддержку: @rocketcontent_supportbot")
        elif query_data == 'smart_reels':
            send_message(chat_id, "📲 Умное создание Reels\nОтправь мне видео или ссылку. Я сделаю: транскрибацию, рерайт, субтитры, видео из шаблона, обложку и публикацию.\n\nВыбери действие:", )

            keyboard = [
                [
                    InlineKeyboardButton("🔤 Транскрибация", callback_data='transcribe'),
                    InlineKeyboardButton("✍️ Рерайт", callback_data='rewrite')
                ],
                [
                    InlineKeyboardButton("🧩 Видео из шаблона CapCut", callback_data='capcut'),
                    InlineKeyboardButton("🎞 Субтитры", callback_data='subtitles')
                ],
                [
                    InlineKeyboardButton("🖼 Обложка", callback_data='thumbnail'),
                    InlineKeyboardButton("📤 Постинг", callback_data='publish')
                ]
            ]

            reply_markup = {'inline_keyboard': [[btn.to_dict() for btn in row] for row in keyboard]}

            requests.post(TELEGRAM_API_URL, json={
                'chat_id': chat_id,
                'text': 'Выбери, что сделать с видео 👇',
                'reply_markup': reply_markup
            })

    return jsonify(success=True)

def send_message(chat_id, text):
    requests.post(TELEGRAM_API_URL, json={
        'chat_id': chat_id,
        'text': text
    })

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=10000)
