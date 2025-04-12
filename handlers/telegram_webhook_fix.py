import requests
import os
import math
import shutil
import yt_dlp
from tempfile import mkdtemp
from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from flask import send_file

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
