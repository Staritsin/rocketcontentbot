import requests
import os
import math
import shutil
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

def handle_voice_transcription(chat_id, file_path):
    
# Проверка: установлен ли ffprobe
ffprobe_check = os.popen("which ffprobe").read().strip()
if not ffprobe_check:
    raise EnvironmentError("ffprobe не установлен. Установи его в Render через 'apt install ffmpeg'")

    
    try:
        temp_dir = mkdtemp()
        input_path = os.path.join(temp_dir, "input.ogg")
        file_response = requests.get(f"https://api.telegram.org/file/bot{BOT_TOKEN}/{file_path}")
        with open(input_path, "wb") as f:
            f.write(file_response.content)

        log_transcription_progress(chat_id, f"Файл загружен: {input_path}")

        probe_cmd = f"ffprobe -v error -show_entries format=duration -of default=noprint_wrappers=1:nokey=1 {input_path}"
        duration_str = os.popen(probe_cmd).read().strip()

        if not duration_str:
            raise ValueError("ffprobe не вернул длительность — проверь формат или установку ffmpeg")

        duration = float(duration_str)

        chunk_duration = 60
        total_chunks = math.ceil(duration / chunk_duration)

        log_transcription_progress(chat_id, f"Общая длительность: {duration} сек. Будет {total_chunks} фрагментов")

        full_text = []

        for i in range(total_chunks):
            chunk_path = os.path.join(temp_dir, f"chunk_{i}.mp3")
            start_time = i * chunk_duration
            cmd = f"ffmpeg -i {input_path} -ss {start_time} -t {chunk_duration} -ar 44100 -ac 1 -vn -y {chunk_path}"
            os.system(cmd)

            with open(chunk_path, "rb") as f:
                response = requests.post(
                    "https://api.openai.com/v1/audio/transcriptions",
                    headers={"Authorization": f"Bearer {os.environ.get('OPENAI_API_KEY')}"},
                    files={"file": f},
                    data={"model": "whisper-1"}
                )
                result = response.json()
                full_text.append(result.get("text", ""))

            log_transcription_progress(chat_id, f"Обработан фрагмент {i + 1}/{total_chunks}")

            requests.post(f'{TELEGRAM_API_URL}/sendMessage', json={
                'chat_id': chat_id,
                'text': f"⏳ Прогресс: {i + 1}/{total_chunks} минут обработано..."
            })

        final_text = " ".join(full_text).strip()
        user_states[chat_id] = {'last_transcript': final_text}

        os.makedirs("transcripts", exist_ok=True)
        result_path = f"transcripts/result_{chat_id}.txt"
        with open(result_path, "w", encoding="utf-8") as out:
            out.write(final_text)

        requests.post(f'{TELEGRAM_API_URL}/sendMessage', json={
            'chat_id': chat_id,
            'text': f"📝 Расшифровка:\n{final_text}"
        })

        keyboard = [[InlineKeyboardButton("📁 Скачать результат", callback_data='download_transcript')]]
        reply_markup = InlineKeyboardMarkup(keyboard).to_dict()
        requests.post(f'{TELEGRAM_API_URL}/sendMessage', json={
            'chat_id': chat_id,
            'text': "Что дальше? 👇",
            'reply_markup': reply_markup
        })

        shutil.rmtree(temp_dir)

    except Exception as e:
        log_transcription_progress(chat_id, f"❌ Ошибка транскрибации: {e}")
        requests.post(f'{TELEGRAM_API_URL}/sendMessage', json={
            'chat_id': chat_id,
            'text': f"❌ Ошибка транскрибации: {e}"
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
