import requests
import os

BOT_TOKEN = os.environ.get('BOT_TOKEN')
TELEGRAM_API_URL = f'https://api.telegram.org/bot{BOT_TOKEN}/sendMessage'

def handle_voice(chat_id):
    text = (
        "🎧 Работа с голосом\n"
        "Отправь мне голосовое сообщение — я превращу его в текст с помощью нейросети Whisper.\n"
        "Затем ты сможешь сделать рерайт или использовать текст для генерации поста или видео."
    )

    requests.post(TELEGRAM_API_URL, json={
        'chat_id': chat_id,
        'text': text
    })
