import requests
import os

BOT_TOKEN = os.environ.get('BOT_TOKEN')
OPENAI_API_KEY = os.environ.get('OPENAI_API_KEY')

TELEGRAM_API_URL = f'https://api.telegram.org/bot{BOT_TOKEN}'
TELEGRAM_FILE_API = f'https://api.telegram.org/file/bot{BOT_TOKEN}'


def handle_voice(chat_id):
    # Отправка инструкции
    text = (
        "🎧 Работа с голосом\n"
        "Отправь мне голосовое сообщение — я превращу его в текст с помощью нейросети Whisper.\n"
        "Затем ты сможешь сделать рерайт или использовать текст для генерации поста или видео."
    )
    requests.post(f'{TELEGRAM_API_URL}/sendMessage', json={
        'chat_id': chat_id,
        'text': text
    })


def handle_voice_transcription(chat_id, file_id):
    try:
        print("📥 Получен file_id:", file_id)

        # Получаем file_path
        file_info = requests.get(f"{TELEGRAM_API_URL}/getFile?file_id={file_id}").json()
        file_path = file_info['result']['file_path']
        file_url = f"{TELEGRAM_FILE_API}/{file_path}"
        print("🔗 Скачивание по ссылке:", file_url)

        # Скачиваем файл
        audio_content = requests.get(file_url).content
        local_filename = "voice.ogg"
        with open(local_filename, "wb") as f:
            f.write(audio_content)

        # Отправляем в Whisper
        print("📤 Отправка в Whisper...")
        with open(local_filename, "rb") as f:
            response = requests.post(
                "https://api.openai.com/v1/audio/transcriptions",
                headers={"Authorization": f"Bearer {OPENAI_API_KEY}"},
                files={"file": f},
                data={"model": "whisper-1"}
            )

        result = response.json()
        print("✅ Ответ от Whisper:", result)

        text = result.get("text", "❌ Не удалось распознать речь.")
        requests.post(f'{TELEGRAM_API_URL}/sendMessage', json={
            'chat_id': chat_id,
            'text': f"📝 Расшифровка:\n{text}"
        })

    except Exception as e:
        requests.post(f'{TELEGRAM_API_URL}/sendMessage', json={
            'chat_id': chat_id,
            'text': f"❌ Ошибка обработки аудио: {e}"
        })

