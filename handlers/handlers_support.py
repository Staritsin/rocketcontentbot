import requests
import os

BOT_TOKEN = os.environ.get('BOT_TOKEN')
TELEGRAM_API_URL = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"

def handle_support(chat_id):
    message = (
        "🛠 Поддержка\n\n"
        "Если у тебя возникли вопросы или сложности, напиши нам:\n"
        "@rocketcontent_supportbot\n\n"
        "Мы на связи и всегда поможем! 🚀"
    )

    requests.post(TELEGRAM_API_URL, json={
        'chat_id': chat_id,
        'text': message
    })

