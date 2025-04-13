# handlers_subtitles.py

import os
import requests

BOT_TOKEN = os.environ.get('BOT_TOKEN')
TELEGRAM_API_URL = f'https://api.telegram.org/bot{BOT_TOKEN}/sendMessage'

def handle_subtitles(chat_id):
    text = (
        "🎞 Субтитры для видео\n"
        "Отправь видео или текст — я наложу субтитры автоматически."
    )
    requests.post(TELEGRAM_API_URL, json={
        'chat_id': chat_id,
        'text': text
    })

# handlers/handlers_subtitles.py

def generate_subtitles(chat_id, text, video_url):
    """
    🔧 Заглушка: в будущем добавим генерацию субтитров.
    Сейчас — просто выводим лог.
    """
    print(f"📝 Генерация субтитров для {chat_id}: {text[:30]}... → {video_url}")

def handle_publish(chat_id):
    text = (
        "📤 Публикация контента\n"
        "Выбери, куда опубликовать: Instagram, Telegram, VK и другие.\n"
        "Скоро добавим автоматический постинг."
    )
    requests.post(TELEGRAM_API_URL, json={
        'chat_id': chat_id,
        'text': text
    })
