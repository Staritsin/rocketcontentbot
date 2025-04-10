import os
import requests
from flask import request

BOT_TOKEN = os.environ.get('BOT_TOKEN')
TELEGRAM_API_URL = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"

WHISPER_API_URL = "https://api.openai.com/v1/audio/transcriptions"
OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY")


def transcribe_audio(chat_id, file_url):
    try:
        # Скачиваем файл
        audio_response = requests.get(file_url)
        filename = "voice.ogg"
        with open(filename, "wb") as f:
            f.write(audio_response.content)

        # Отправляем в OpenAI Whisper
        with open(filename, "rb") as f:
            response = requests.post(
                WHISPER_API_URL,
                headers={"Authorization": f"Bearer {OPENAI_API_KEY}"},
                files={"file": f},
                data={"model": "whisper-1"}
            )

        result = response.json()

      if "text" in result:
    requests.post(TELEGRAM_API_URL, json={
        'chat_id': chat_id,
        'text': f"📼 Готовая транскрибация:\n{result['text']}"
    })
    else:
    requests.post(TELEGRAM_API_URL, json={
        'chat_id': chat_id,
        'text': f"❌ Ошибка транскрибации: {result}"
    })


    except Exception as e:
        requests.post(TELEGRAM_API_URL, json={
            'chat_id': chat_id,
            'text': f"⚠️ Ошибка при обработке аудио: {e}"
        })
