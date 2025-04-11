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
        # 1. Получаем file_path по file_id
        file_info = requests.get(f"{TELEGRAM_API_URL}/getFile?file_id={file_id}").json()
        file_path = file_info['result']['file_path']

        # 2. Скачиваем файл
        file_url = f"{TELEGRAM_FILE_API}/{file_path}"
        audio_content = requests.get(file_url).content

        local_filename = "voice.ogg"
        with open(local_filename, "wb") as f:
            f.write(audio_content)

        # 3. Отправляем в Whisper
        with open(local_filename, "rb") as f:
            response = requests.post(
                "https://api.openai.com/v1/audio/transcriptions",
                headers={
                    "Authorization": f"Bearer {OPENAI_API_KEY}"
                },
                files={"file": f},
                data={"model": "whisper-1"}
            )

        result = response.json()
        text = result.get("text", "❌ Не удалось распознать речь.")

        # 4. Отправляем результат в Telegram
        requests.post(f'{TELEGRAM_API_URL}/sendMessage', json={
            'chat_id': chat_id,
            'text': f"📝 Расшифровка:\n{text}"
        })

    except Exception as e:
        requests.post(f'{TELEGRAM_API_URL}/sendMessage', json={
            'chat_id': chat_id,
            'text': f"❌ Ошибка обработки аудио: {e}"
        })
