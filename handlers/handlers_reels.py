import os
import requests

BOT_TOKEN = os.environ.get("BOT_TOKEN")
TELEGRAM_API_URL = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
WHISPER_API_KEY = os.environ.get("OPENAI_API_KEY")
WHISPER_API_URL = "https://api.openai.com/v1/audio/transcriptions"

def handle_transcribe(chat_id):
    try:
        # Предполагаем, что audio_url уже получен и загружен
        audio_url = "https://yourdomain.com/path/to/audio.ogg"
        audio_response = requests.get(audio_url)
        filename = "audio.ogg"
        with open(filename, "wb") as f:
            f.write(audio_response.content)

        with open(filename, "rb") as f:
            response = requests.post(
                WHISPER_API_URL,
                headers={"Authorization": f"Bearer {WHISPER_API_KEY}"},
                files={"file": f},
                data={"model": "whisper-1"}
            )

        result = response.json()
        if "text" in result:
            requests.post(TELEGRAM_API_URL, json={
                'chat_id': chat_id,
                'text': f"🎬 Готовая транскрибация:\n{result['text']}"
            })
        else:
            requests.post(TELEGRAM_API_URL, json={
                'chat_id': chat_id,
                'text': f"❌ Ошибка транскрибации: {result}"
            })
    except Exception as e:
        requests.post(TELEGRAM_API_URL, json={
            'chat_id': chat_id,
            'text': f"❌ Ошибка при обработке аудио: {e}"
        })
