import requests
import os

BOT_TOKEN = os.environ.get('BOT_TOKEN')
TELEGRAM_API_URL = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"

def handle_plan(chat_id):
    message = (
        "📅 Контент-план\n\n"
        "Напиши тематику, нишу или продукт — я помогу составить недельный контент-план с идеями для Reels, постов и сторис.\n\n"
        "Например: «продвижение психолога», «онлайн-школа английского», «инфобизнес» и т.д."
    )

    requests.post(TELEGRAM_API_URL, json={
        'chat_id': chat_id,
        'text': message
    })

