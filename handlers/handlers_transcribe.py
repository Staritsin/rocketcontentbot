# handlers/handlers_reels.py

from utils import send_message

# Хранилище состояний пользователей
user_states = {}

# Шаг 1. Включаем режим ожидания ссылки или файла
def handle_transcribe_mode(chat_id):
    user_states[chat_id] = 'awaiting_transcribe_input'
    send_message(chat_id, "📥 Жду ссылку на видео (YouTube, TikTok и др.) или загрузи файл для транскрибации.")

# Шаг 2. Обработка видео: скачивание и отправка в Whisper
import yt_dlp
import requests
import os

WHISPER_API_URL = 'https://api.openai.com/v1/audio/transcriptions'
OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY")

def download_video(url, output_path='input.mp4'):
    ydl_opts = {
        'format': 'mp4',
        'outtmpl': output_path,
        'quiet': True
    }
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        ydl.download([url])
    return output_path

def transcribe_video(file_path):
    with open(file_path, 'rb') as f:
        response = requests.post(
            WHISPER_API_URL,
            headers={"Authorization": f"Bearer {OPENAI_API_KEY}"},
            files={"file": f},
            data={"model": "whisper-1"}
        )
    return response.json()

def handle_transcribe_input(chat_id, text):
    try:
        video_path = download_video(text)
        result = transcribe_video(video_path)
        if 'text' in result:
            send_message(chat_id, f"📄 Готовая транскрибация:\n{result['text']}")
        else:
            send_message(chat_id, f"❌ Ошибка транскрибации: {result}")
    except Exception as e:
        send_message(chat_id, f"🚫 Ошибка: {e}")
