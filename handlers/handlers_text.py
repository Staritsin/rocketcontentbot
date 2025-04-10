import requests
import os

BOT_TOKEN = os.environ.get('BOT_TOKEN')
TELEGRAM_API_URL = f'https://api.telegram.org/bot{BOT_TOKEN}/sendMessage'

def handle_text(chat_id):
    text = (
        "✍️ Работа с текстом\n"
        "Отправь мне текст или выбери действие:\n\n"
        "- 🔁 Рерайт текста\n"
        "- 🧠 Генерация идеи поста\n"
        "- 🎬 Сценарий по видео или теме\n\n"
        "Скоро добавим кнопки для выбора!"
    )

    requests.post(TELEGRAM_API_URL, json={
        'chat_id': chat_id,
        'text': text
    })
