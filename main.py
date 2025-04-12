from flask import Flask, request, jsonify
import requests
import os
from telegram import InlineKeyboardButton
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
from handlers.utils import TELEGRAM_API_URL
from handlers.handlers_transcribe import handle_transcribe_mode, handle_transcribe_input
from handlers.handlers_voice import handle_voice_transcription
from handlers.telegram_webhook_fix import (
    handle_post_platform_selection,
    generate_platform_post,
    handle_rewrite_transcript,
    send_transcript_file,
    handle_callback_rating
)


app = Flask(__name__)
BOT_TOKEN = os.environ.get('BOT_TOKEN')
TELEGRAM_API_URL = f'https://api.telegram.org/bot{BOT_TOKEN}/sendMessage'
user_states = {}

@app.route('/')
def index():
    return 'Бот работает!'

@app.route('/telegram', methods=['POST'])
def telegram_webhook():
    data = request.get_json()
    print("🔥 Получены данные от Telegram:", data)

    # === CALLBACK QUERY ===
    if 'callback_query' in data:
        callback = data['callback_query']
        chat_id = callback['message']['chat']['id']
        query_data = callback['data']
        callback_id = callback['id']
        
        # Ответ Telegram
        requests.post(f"https://api.telegram.org/bot{BOT_TOKEN}/answerCallbackQuery", json={
            'callback_query_id': callback_id
        })
        
        # === добавь сюда
        if handle_callback_rating(query_data, chat_id):
            return jsonify(success=True)

        if query_data == 'video':
            handle_video(chat_id)
        elif query_data == 'voice':
            handle_voice(chat_id)
        elif query_data == 'text':
            handle_text(chat_id)
        elif query_data == 'image':
            handle_image(chat_id)
        elif query_data == 'plan':
            handle_plan(chat_id)
        elif query_data == 'pay':
            handle_pay(chat_id)
        elif query_data == 'support':
            handle_support(chat_id)
        elif query_data == 'smart_reels':
            send_message(chat_id, "📲 Умное создание Reels\nОтправь мне видео или ссылку. Я сделаю: транскрибацию, рерайт, субтитры, видео из шаблона, обложку и публикацию.")
            keyboard = [
                [InlineKeyboardButton("🔤 Транскрибация", callback_data='transcribe'),
                 InlineKeyboardButton("✍️ Рерайт", callback_data='rewrite')],
                [InlineKeyboardButton("🧩 Видео из шаблона CapCut", callback_data='capcut'),
                 InlineKeyboardButton("🎞 Субтитры", callback_data='subtitles')],
                [InlineKeyboardButton("🖼 Обложка", callback_data='thumbnail'),
                 InlineKeyboardButton("📤 Постинг", callback_data='publish')]
            ]
            reply_markup = {'inline_keyboard': [[btn.to_dict() for btn in row] for row in keyboard]}
            requests.post(TELEGRAM_API_URL, json={
                'chat_id': chat_id,
                'text': 'Выбери, что сделать с видео 👇',
                'reply_markup': reply_markup
            })
        elif query_data == 'transcribe':
            user_states[chat_id] = 'transcribe'
            send_message(chat_id, "✉️ Отправь видео или текст для транскрибации.")
        
        elif query_data == 'rewrite':
            handle_rewrite(chat_id)
        
        elif query_data == 'capcut':
            handle_capcut(chat_id)
        
        elif query_data == 'subtitles':
            handle_subtitles(chat_id)
        
        elif query_data == 'thumbnail':
            handle_thumbnail(chat_id)
        
        elif query_data == 'publish':
            handle_publish(chat_id)
        
        elif query_data == 'use_as_post':
            handle_post_platform_selection(chat_id)
        
        elif query_data == 'post_instagram':
            generate_platform_post(chat_id, 'instagram')
        
        elif query_data == 'post_telegram':
            generate_platform_post(chat_id, 'telegram')
        
        elif query_data == 'post_spam':
            generate_platform_post(chat_id, 'spam')
        
        elif query_data == 'post_vk':
            generate_platform_post(chat_id, 'vk')
        
        elif query_data == 'rewrite_transcript':
            send_message(chat_id, "✍️ Окей, запускаю рерайт текста!")
            handle_rewrite_transcript(chat_id)

        
        elif query_data == 'make_reels':
            send_message(chat_id, "🎬 Начинаю сборку Reels.")
        
        elif query_data == 'success':
            send_message(chat_id, "🌟 Рад, что всё получилось!")
        
        elif query_data == 'menu':
            send_message(chat_id, "🔙 Возвращаю в меню. Напиши /menu")

        elif query_data == 'download_transcript':
            send_transcript_file(chat_id)

        return jsonify(success=True)

    # === MESSAGE ===
    if 'message' in data:
        message = data['message']
        chat_id = message['chat']['id']

        if 'voice' in message or 'audio' in message:
            file_id = message['voice']['file_id'] if 'voice' in message else message['audio']['file_id']
            handle_voice_transcription(chat_id, file_id)
            return jsonify(success=True)

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
                send_message(chat_id, "Привет! 👋 Я — твой персональный AI-ассистент...\nГотов начать? Жми /menu 😊")
            elif text.lower() == '/menu':
                keyboard = [
                    [InlineKeyboardButton("🎬 Видео", callback_data='video'),
                     InlineKeyboardButton("🎧 Голос", callback_data='voice')],
                    [InlineKeyboardButton("✍️ Текст", callback_data='text'),
                     InlineKeyboardButton("🖼 Картинки", callback_data='image')],
                    [InlineKeyboardButton("📅 План", callback_data='plan'),
                     InlineKeyboardButton("💳 Оплата", callback_data='pay')],
                    [InlineKeyboardButton("📲 Умный Reels", callback_data='smart_reels')],
                    [InlineKeyboardButton("🛠 Поддержка", callback_data='support')]
                ]
                reply_markup = {'inline_keyboard': [[btn.to_dict() for btn in row] for row in keyboard]}
                requests.post(TELEGRAM_API_URL, json={
                    'chat_id': chat_id,
                    'text': 'Что будем делать? 👇',
                    'reply_markup': reply_markup
                })

            elif text.lower() == '/stats':
                from handlers.telegram_webhook_fix import handle_stats_request
                handle_stats_request(chat_id)
            elif text.lower() == '/help':
            send_message(chat_id, 
                "📚 Что я умею:\n\n"
                "/menu — главное меню\n"
                "/stats — статистика\n"
                "/help — список команд\n"
                "/about — кто я и зачем\n\n"
                "✉️ Отправь видео, голос или текст — и я всё обработаю!")
            
            elif text.lower() == '/about':
            send_message(chat_id, 
                "🤖 Обо мне:\n"
                "Я — бот Александра Старицина, эксперта по нейросетям и автоматизации бизнеса.\n\n"
                "Я помогаю тебе:\n"
                "— расшифровывать голос и видео\n"
                "— делать Reels из шаблона\n"
                "— генерировать и публиковать посты\n"
                "— работать с CapCut, Telegram, Instagram\n\n"
                "🌐 Подробнее: https://revolife.ru")


            else:
                send_message(chat_id, "✅ Бот получил сообщение!")

    return jsonify(success=True)

def send_message(chat_id, text):
    requests.post(TELEGRAM_API_URL, json={
        'chat_id': chat_id,
        'text': text
    })

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=10000, threaded=True)
