from flask import Flask, request, jsonify
from flask import send_from_directory
import requests
import os

import uuid
from handlers.utils import download_telegram_file
from handlers.handlers_stories import handle_single_video_processing


from telegram import InlineKeyboardButton
from handlers.utils import send_message
from handlers.utils import TELEGRAM_API_URL
from handlers.handlers_stories import handle_stories_pipeline, process_stories_multiple
from handlers.handlers_buttons import send_story_action_buttons
from handlers.handlers_buttons import handle_story_action_callback
from handlers.handlers_buttons import handle_user_choice
from handlers.handlers_rewrite import handle_callback_query
from handlers.handlers_video import handle_video
from handlers.handlers_stories import handle_stories_pipeline
from handlers.handlers_reels import handle_transcribe
from handlers.handlers_rewrite import handle_rewrite
from handlers.handlers_runway import handle_capcut, process_capcut_pipeline
from handlers.handlers_subtitles import handle_subtitles
from handlers.handlers_thumbnail import handle_thumbnail
from handlers.handlers_publish import handle_publish
from handlers.handlers_voice import handle_voice
from handlers.handlers_text import handle_text
from handlers.handlers_image import handle_image
from handlers.handlers_plan import handle_plan
from handlers.handlers_pay import handle_pay
from handlers.handlers_support import handle_support
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

user_states = {}

@app.route('/')
def index():
    return 'Бот работает!'

@app.route('/webhook', methods=['POST'])

def telegram_webhook():
    data = request.get_json()
    print("\U0001F525 Получены данные от Telegram:", data)

    if 'callback_query' in data:
        callback = data['callback_query']
        chat_id = callback['message']['chat']['id']
        query_data = callback['data']

        print(f"📩 Поймал callback_query: {query_data}", flush=True)

        if query_data.startswith("story_") or query_data in ["publish_photo", "publish_video"]:
            handle_story_action_callback(chat_id, query_data)
            return jsonify(success=True)

        callback_id = callback['id']

        requests.post(f"https://api.telegram.org/bot{BOT_TOKEN}/answerCallbackQuery", json={
            'callback_query_id': callback_id
        })

        # 👇 Обработка наших кастомных кнопок
        if query_data in ['publish', 'add_inserts', 'add_subtitles']:
            handle_callback_query(callback)
            return jsonify(success=True)

        if handle_callback_rating(query_data, chat_id):
            return jsonify(success=True)


        elif query_data == 'make_stories':
            keyboard = [
                [InlineKeyboardButton("10% склеек", callback_data='stories_10'),
                 InlineKeyboardButton("30%", callback_data='stories_30')],
                [InlineKeyboardButton("50%", callback_data='stories_50'),
                 InlineKeyboardButton("100%", callback_data='stories_100')]
            ]
            reply_markup = {'inline_keyboard': [[btn.to_dict() for btn in row] for row in keyboard]}
            requests.post(TELEGRAM_API_URL, json={
                'chat_id': chat_id,
                'text': 'Выбери сколько процентов вставок нужно: \ud83d\udd22',
                'reply_markup': reply_markup
            })

        elif query_data.startswith('stories_'):
            percent = int(query_data.split('_')[1])
            user_states[chat_id] = {'mode': 'stories_processing', 'inserts_percent': percent}
            send_message(chat_id, f"✅ Принято! Будет использовано {percent}% вставок. Теперь отправь видео.")

        elif query_data == 'stories_ready':
            send_message(chat_id, "\U0001F4E4 Отлично! Готовый Stories принят. Можно публиковать.")

        elif query_data == 'make_reels':
            send_message(chat_id, "\U0001F3A5 Готово! Отправь видео или ссылку — сделаю Reels по шаблону.")
            user_states[chat_id] = {"mode": "capcut_generation"}

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
                [InlineKeyboardButton("\ud83d\udd24 Транскрибация", callback_data='transcribe'),
                 InlineKeyboardButton("\u270d\ufe0f Рерайт", callback_data='rewrite')],
                [InlineKeyboardButton("\U0001F9E9 Видео из шаблона CapCut", callback_data='capcut'),
                 InlineKeyboardButton("\U0001F39E Субтитры", callback_data='subtitles')],
                [InlineKeyboardButton("\U0001F5BC Обложка", callback_data='thumbnail'),
                 InlineKeyboardButton("\U0001F4E4 Постинг", callback_data='publish')]
            ]
            reply_markup = {'inline_keyboard': [[btn.to_dict() for btn in row] for row in keyboard]}
            requests.post(TELEGRAM_API_URL, json={
                'chat_id': chat_id,
                'text': 'Выбери, что сделать с видео \ud83d\udc47',
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
        elif query_data.startswith('post_'):
            generate_platform_post(chat_id, query_data.split('_')[1])
        elif query_data == 'rewrite_transcript':
            send_message(chat_id, "✍️ Окей, запускаю рерайт текста!")
            handle_rewrite_transcript(chat_id)
        elif query_data == 'success':
            send_message(chat_id, "🌟 Рад, что всё получилось!")
        elif query_data == 'menu':
            send_message(chat_id, "🔙 Возвращаю в меню. Напиши /menu")
        elif query_data == 'download_transcript':
            send_transcript_file(chat_id)

        return jsonify(success=True)

    if 'message' in data:
        message = data['message']
        chat_id = message['chat']['id']

        if 'voice' in message or 'audio' in message:
            file_id = message['voice']['file_id'] if 'voice' in message else message['audio']['file_id']
            handle_voice_transcription(chat_id, file_id)
            return jsonify(success=True)

        if 'video' in message or 'document' in message:
            file_id = message['video']['file_id'] if 'video' in message else message['document']['file_id']
            mode = user_states.get(chat_id, {}).get("mode")
            print(f"🎯 Получено видео file_id: {file_id}, режим: {mode}", flush=True)

            if mode == "single_processing":
                uid = str(uuid.uuid4())
                temp_path = f"uploads/{uid}.mp4"
                print(f"📥 Начинаю скачивание по file_id: {file_id} → {temp_path}", flush=True)
                download_telegram_file(file_id, temp_path)
                print(f"📥 single_processing: скачал файл в {temp_path}", flush=True)
                user_states[chat_id]["last_video_path"] = temp_path
                handle_single_video_processing(chat_id, temp_path)
                return jsonify(success=True)


            
            elif mode == "stories_multiple":
                from handlers.handlers_stories import process_stories_multiple
                user_states.setdefault(chat_id, {}).setdefault("video_files", []).append(file_id)
                count = len(user_states[chat_id]["video_files"])
            
                if count >= 2:
                    process_stories_multiple(chat_id, user_states[chat_id]["video_files"])
                    user_states[chat_id] = {}  # сбрасываем
                else:
                    send_message(chat_id, f"📹 Получено {count} видео. Отправь ещё минимум одно.")
                return jsonify(success=True)

        
            elif mode == "publish_ready":
                send_message(chat_id, "📤 Принято! Видео будет опубликовано (заглушка).")
                return jsonify(success=True)
            
            elif mode == "stories_processing":
                handle_stories_pipeline(chat_id, file_id)
                return jsonify(success=True)

            
            if user_states.get(chat_id, {}).get("mode") == "capcut_generation":
                from handlers.handlers_runway import process_capcut_pipeline
                process_capcut_pipeline(chat_id, file_id)
                return jsonify(success=True)
            if user_states.get(chat_id) == 'transcribe':
                handle_transcribe_input(chat_id, message)
                return jsonify(success=True)

        if 'text' in message:
            text = message['text']
            
            if text == "📖 Stories":
                send_story_action_buttons(chat_id)
                return jsonify(success=True)


            if text.strip() in ["1", "2", "3", "4", "1️⃣ Опубликовать", "2️⃣ Субтитры", "3️⃣ Вставки", "4️⃣ Всё сразу"]:
                handle_user_choice(chat_id, text.strip())
                return


            elif text == "🎬 REELS":
                send_message(chat_id, "🎬 Готово! Отправь видео или ссылку — сделаю Reels по шаблону.")
                user_states[chat_id] = {"mode": "capcut_generation"}
                return jsonify(success=True)
        
            elif text == "🎬 Скачать видео в Mp4":
                send_message(chat_id, "🎬 Вставь ссылку на видео (YouTube, Reels, Shorts, Telegram, VK) — скачаю и обработаю.")
                user_states[chat_id] = {'mode': 'download_video'}
                return jsonify(success=True)
        
            elif text == "🧠 Вытащить Текст":
                send_message(chat_id, "🧠 Отправь голос или видео — вытащу текст через Whisper.")
                user_states[chat_id] = {'mode': 'transcribe'}
                return jsonify(success=True)
        
            elif text == "🎙 Переводчик":
                send_message(chat_id, "🌍 Отправь голосовое — переведу на 3 языка.")
                user_states[chat_id] = {'mode': 'translate'}
                return jsonify(success=True)

        
            elif text == "🖼 Фото":
                send_message(chat_id, "🖼 Отправь описание или тему — сгенерирую изображение.")
                user_states[chat_id] = {'mode': 'image_generation'}
                return jsonify(success=True)
        
            elif text == "💳 Подписка":
                send_message(chat_id, "💳 Оплата и подписка через Make — доступна в индивидуальном порядке. Напиши в поддержку.")
                return jsonify(success=True)
        
            elif text == "📂 Контент":
                send_message(chat_id, "📂 Хранилище твоих видео и постов. Пока в разработке.")
                return jsonify(success=True)
        
            elif text == "🛠 Поддержка":
                send_message(chat_id, "🛠 Напиши в @Staritsin или оставь сообщение здесь — я помогу.")
                return jsonify(success=True)
            
            if user_states.get(chat_id) == 'transcribe':
                handle_transcribe_input(chat_id, text)
                return jsonify(success=True)
                
            if text.lower() == '/start':
                send_message(chat_id, "Привет! \ud83d\udc4b Я — твой персональный AI-ассистент...\nГотов начать? Жми /menu \ud83d\ude0a")
            elif text.lower() == '/menu':
                from telegram import ReplyKeyboardMarkup
            
                keyboard = [
                    ["🎬 Скачать видео в Mp4", "🧠 Вытащить Текст"],
                    ["📖 Stories", "🎬 REELS"],
                    ["🖼 Фото", "🎙 Переводчик"],
                    ["💳 Подписка", "📂 Контент", "🛠 Поддержка"]
                ]
                reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
                requests.post(TELEGRAM_API_URL, json={
                    'chat_id': chat_id,
                    'text': 'Что будем делать? 👇',
                    'reply_markup': reply_markup.to_dict()
                })

                return jsonify(success=True)

            elif text.lower() == '/stats':
                from handlers.telegram_webhook_fix import handle_stats_request
                handle_stats_request(chat_id)
            elif text.lower() == '/help':
                send_message(chat_id, "\ud83d\udcda Что я умею:\n\n/menu — главное меню\n/stats — статистика\n/help — список команд\n/about — кто я и зачем\n\n✉️ Отправь видео, голос или текст — и я всё обработаю!")
            elif text.lower() == '/about':
                send_message(chat_id, "\ud83e\udd16 Обо мне:\nЯ — бот Александра Старицина, эксперта по нейросетям и автоматизации бизнеса.\n\nЯ помогаю тебе:\n— расшифровывать голос и видео\n— делать Reels из шаблона\n— генерировать и публиковать посты\n— работать с CapCut, Telegram, Instagram\n\n\ud83c\udf10 Подробнее: https://revolife.ru")
            
            # 🧠 Обработка быстрых команд после получения видео
            if chat_id in user_states and "last_video_path" in user_states[chat_id]:
                video_path = user_states[chat_id]["last_video_path"]
                from handlers.handlers_buttons import handle_user_choice
                handle_user_choice(chat_id, text, video_path)
                return jsonify(success=True)

            else:
                send_message(chat_id, "❓ Не понял выбор. Напиши /menu или выбери кнопку ниже.")
                return jsonify(success=True)
                
        return 'OK', 200  # <-- ЭТО ОБЯЗАТЕЛЬНО

            

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=10000, threaded=True)



