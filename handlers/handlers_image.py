import requests
import os

BOT_TOKEN = os.environ.get('BOT_TOKEN')
TELEGRAM_API_URL = f'https://api.telegram.org/bot{BOT_TOKEN}/sendMessage'

def handle_image(chat_id):
    text = (
        "🖼 Работа с изображениями\n"
        "Напиши, что ты хочешь увидеть — я сгенерирую картинку с помощью нейросети."
    )

    requests.post(TELEGRAM_API_URL, json={
        'chat_id': chat_id,
        'text': text
    })

