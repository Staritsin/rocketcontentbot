import requests
import os
import math
import shutil
import yt_dlp
from tempfile import mkdtemp
from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from flask import send_file
import json

stats_file = "stats.json"

def load_stats():
    if os.path.exists(stats_file):
        with open(stats_file, "r") as f:
            return json.load(f)
    return {"users": {}, "ratings": []}

def save_stats(stats):
    with open(stats_file, "w") as f:
        json.dump(stats, f, indent=2)

stats = load_stats()

def record_rating(chat_id, rating):
    chat_id = str(chat_id)
    stats["users"].setdefault(chat_id, {"actions": [], "rating": None})
    stats["users"][chat_id]["rating"] = rating
    stats["ratings"].append(rating)
    save_stats(stats)


BOT_TOKEN = os.environ.get('BOT_TOKEN')
TELEGRAM_API_URL = f'https://api.telegram.org/bot{BOT_TOKEN}'

# Хранилище состояния пользователя
user_states = {}

# === ЛОГ-ФУНКЦИЯ ===
def log_transcription_progress(chat_id, message):
    os.makedirs("logs", exist_ok=True)
    with open("logs/transcribe.log", "a", encoding="utf-8") as log_file:
        log_file.write(f"[chat_id: {chat_id}] {message}\n")

# === ОБНОВЛЕНИЕ СООБЩЕНИЯ ПРОГРЕССА ===
def update_progress_message(chat_id, text):
    state = user_states.setdefault(chat_id, {})
    message_id = state.get("progress_message_id")

    if message_id:
        requests.post(f'{TELEGRAM_API_URL}/editMessageText', json={
            'chat_id': chat_id,
            'message_id': message_id,
            'text': text
        })
    else:
        response = requests.post(f'{TELEGRAM_API_URL}/sendMessage', json={
            'chat_id': chat_id,
            'text': text
        })
        message_id = response.json().get("result", {}).get("message_id")
        if message_id:
            state["progress_message_id"] = message_id

# === ОСТАНОВКА СООБЩЕНИЯ ПРОГРЕССА ===
def clear_progress_message(chat_id):
    state = user_states.get(chat_id, {})
    message_id = state.pop("progress_message_id", None)
    if message_id:
        try:
            requests.post(f'{TELEGRAM_API_URL}/editMessageText', json={
                'chat_id': chat_id,
                'message_id': message_id,
                'text': "✅ Обработка завершена"
            })
        except:
            pass

def handle_post_platform_selection(chat_id):
    text = "Выбери, куда хочешь опубликовать пост 👇"
    keyboard = [
        [InlineKeyboardButton("📸 Instagram", callback_data='post_instagram')],
        [InlineKeyboardButton("🗣 Telegram", callback_data='post_telegram')],
        [InlineKeyboardButton("📬 Спам-рассылка", callback_data='post_spam')],
        [InlineKeyboardButton("📢 ВКонтакте", callback_data='post_vk')],
        [InlineKeyboardButton("📁 Скачать результат", callback_data='download_transcript')],
        [InlineKeyboardButton("🎬 Транскрибировать видео", callback_data='transcribe_video')],
        [InlineKeyboardButton("🔙 Вернуться в меню", callback_data='menu')]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard).to_dict()

    requests.post(f'{TELEGRAM_API_URL}/sendMessage', json={
        'chat_id': chat_id,
        'text': text,
        'reply_markup': reply_markup
    })

def generate_platform_post(chat_id, platform):
    last_text = user_states.get(chat_id, {}).get('last_transcript')
    if not last_text:
        requests.post(f'{TELEGRAM_API_URL}/sendMessage', json={
            'chat_id': chat_id,
            'text': "❌ Нет текста для публикации. Сначала сделай транскрибацию."
        })
        return

    if platform == 'instagram':
        text = f"📸 Instagram пост:\n\n{last_text}\n\n👉 Напиши в комменты, что думаешь!"
    elif platform == 'telegram':
        text = f"🗣 Telegram пост:\n\n{last_text}"
    elif platform == 'spam':
        preview = last_text[:300].strip()
        text = (
            f"📬 Спам-рассылка:\n\n"
            f"**Заголовок:** {preview[:50]}...\n"
            f"**Текст:** {preview}\n"
            f"[📌 Подробнее](https://your-link.com)"
        )
    elif platform == 'vk':
        text = f"📢 Пост для ВКонтакте:\n\n{last_text}\n\n#контент #бот #искусственныйинтеллект"
    else:
        text = "❌ Неизвестная платформа"

    requests.post(f'{TELEGRAM_API_URL}/sendMessage', json={
        'chat_id': chat_id,
        'text': text
    })

def handle_rewrite_transcript(chat_id):
    import json

    last_text = user_states.get(chat_id, {}).get('last_transcript')
    if not last_text:
        requests.post(f'{TELEGRAM_API_URL}/sendMessage', json={
            'chat_id': chat_id,
            'text': "❌ Текст для рерайта не найден. Сначала сделай транскрибацию."
        })
        return

    prompt = f"Сделай рерайт следующего текста, сохранив смысл и структуру:\n\n{last_text}"
    try:
        response = requests.post(
            "https://api.openai.com/v1/chat/completions",
            headers={
                "Authorization": f"Bearer {os.environ.get('OPENAI_API_KEY')}",
                "Content-Type": "application/json"
            },
            json={
                "model": "gpt-3.5-turbo",
                "messages": [
                    {"role": "system", "content": "Ты опытный копирайтер."},
                    {"role": "user", "content": prompt}
                ]
            }
        )
        result = response.json()
        rewritten = result['choices'][0]['message']['content']

        requests.post(f'{TELEGRAM_API_URL}/sendMessage', json={
            'chat_id': chat_id,
            'text': f"✍️ Рерайт:\n{rewritten}"
        })

    except Exception as e:
        requests.post(f'{TELEGRAM_API_URL}/sendMessage', json={
            'chat_id': chat_id,
            'text': f"❌ Ошибка рерайта: {e}"
        })

def send_transcript_file(chat_id):
    result_path = f"transcripts/result_{chat_id}.txt"
    if os.path.exists(result_path):
        requests.post(
            f"https://api.telegram.org/bot{BOT_TOKEN}/sendDocument",
            files={"document": open(result_path, "rb")},
            data={"chat_id": chat_id}
        )
    else:
        requests.post(f'{TELEGRAM_API_URL}/sendMessage', json={
            'chat_id': chat_id,
            'text': "❌ Файл не найден. Попробуй сначала сделать транскрибацию."
        })

def handle_callback_download_transcript(query_data, chat_id):
    if query_data == 'download_transcript':
        send_transcript_file(chat_id)
        return True
    return False

def download_media(source_url_or_path):
    temp_dir = mkdtemp()
    output_path = os.path.join(temp_dir, 'media.mp4')

    if source_url_or_path.startswith("http"):
        ydl_opts = {
            'outtmpl': output_path,
            'format': 'mp4/bestaudio/best',
            'quiet': True,
        }
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([source_url_or_path])
    else:
        shutil.copy(source_url_or_path, output_path)

    return output_path

def handle_transcription_from_any_source(chat_id, source):
    try:
        file_path = download_media(source)
        from handlers.handlers_voice import handle_voice_transcription
        handle_voice_transcription(chat_id, file_path)
        clear_progress_message(chat_id)
    except Exception as e:
        log_transcription_progress(chat_id, f"❌ Ошибка загрузки или транскрибации: {e}")
        requests.post(f'{TELEGRAM_API_URL}/sendMessage', json={
            'chat_id': chat_id,
            'text': f"❌ Ошибка: {e}"
        })

def handle_callback_rating(data, chat_id):
    if data.startswith("rate_"):
        rating = int(data.split("_")[1])
        from handlers.telegram_webhook_fix import record_rating  # или вынеси наверх, если часто используешь
        record_rating(chat_id, rating)
        requests.post(f'{TELEGRAM_API_URL}/sendMessage', json={
            'chat_id': chat_id,
            'text': f"Спасибо за оценку ⭐ {rating}"
        })
        return True
    return False

def ask_for_rating(chat_id):
    keyboard = [
        [InlineKeyboardButton("⭐ 1", callback_data='rate_1'),
         InlineKeyboardButton("⭐ 2", callback_data='rate_2'),
         InlineKeyboardButton("⭐ 3", callback_data='rate_3'),
         InlineKeyboardButton("⭐ 4", callback_data='rate_4'),
         InlineKeyboardButton("⭐ 5", callback_data='rate_5')]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard).to_dict()
    requests.post(f'{TELEGRAM_API_URL}/sendMessage', json={
        'chat_id': chat_id,
        'text': "🙏 Оцени работу бота:",
        'reply_markup': reply_markup
    })

def handle_stats_request(chat_id):
    total_users = len(stats["users"])
    all_actions = sum(len(u["actions"]) for u in stats["users"].values())
    ratings = stats["ratings"]
    avg_rating = round(sum(ratings) / len(ratings), 2) if ratings else "–"
    
    message = (
        f"📊 Статистика:\n"
        f"👥 Пользователей: {total_users}\n"
        f"📦 Всего действий: {all_actions}\n"
        f"⭐ Средняя оценка: {avg_rating}"
    )
    requests.post(f'{TELEGRAM_API_URL}/sendMessage', json={
        'chat_id': chat_id,
        'text': message
    })

def handle_update(update):
    if 'message' in update:
        message = update['message']
        chat_id = message['chat']['id']
        text = message.get('text', '')

        if text == '/start':
            requests.post(f'{TELEGRAM_API_URL}/sendMessage', json={
                'chat_id': chat_id,
                'text': "Привет! Я бот. Пришли видео или текст для обработки."
            })
        elif text.startswith('http'):
            handle_transcription_from_any_source(chat_id, text)
        else:
            requests.post(f'{TELEGRAM_API_URL}/sendMessage', json={
                'chat_id': chat_id,
                'text': f"Ты написал: {text}"
            })

    elif 'callback_query' in update:
        callback = update['callback_query']
        chat_id = callback['message']['chat']['id']
        data = callback['data']

        if handle_callback_rating(data, chat_id):
            return
        if handle_callback_download_transcript(data, chat_id):
            return

        requests.post(f'{TELEGRAM_API_URL}/sendMessage', json={
            'chat_id': chat_id,
            'text': f"Нажата кнопка: {data}"
        })

