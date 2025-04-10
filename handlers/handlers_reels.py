import os
import requests
from flask import request

BOT_TOKEN = os.environ.get('BOT_TOKEN')
TELEGRAM_API_URL = f'https://api.telegram.org/bot{BOT_TOKEN}/sendMessage'
WHISPER_API_URL = 'https://api.openai.com/v1/audio/transcriptions'
OPENAI_API_KEY = os.environ.get('OPENAI_API_KEY')

def handle_transcribe(chat_id):
    try:
        if 'voice' in request.json['message']:
            file_id = request.json['message']['voice']['file_id']
        elif 'audio' in request.json['message']:
            file_id = request.json['message']['audio']['file_id']
        else:
            requests.post(TELEGRAM_API_URL, json={
                'chat_id': chat_id,
                'text': "❌ Не удалось найти аудиофайл для транскрибации."
            })
            return

        file_info_url = f"https://api.telegram.org/bot{BOT_TOKEN}/getFile?file_id={file_id}"
        file_info = requests.get(file_info_url).json()
        file_path = file_info['result']['file_path']

        file_url = f"https://api.telegram.org/file/bot{BOT_TOKEN}/{file_path}"
        audio_response = requests.get(file_url)

        filename = 'audio.ogg'
        with open(filename, "wb") as f:
            f.write(audio_response.content)

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
                'text': f"\U0001F4AC Готовая транскрибация:\n{result['text']}"
            })
        else:
            requests.post(TELEGRAM_API_URL, json={
                'chat_id': chat_id,
                'text': f"❌ Ошибка транскрибации: {result}"
            })

    except Exception as e:
        requests.post(TELEGRAM_API_URL, json={
            'chat_id': chat_id,
            'text': f"⚠️ Ошибка: {e}"
        })
