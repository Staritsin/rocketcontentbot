import requests
import os

BOT_TOKEN = os.environ.get('BOT_TOKEN')
TELEGRAM_API_URL = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"

def handle_pay(chat_id):
    message = (
        "💳 Оплата подписки\n\n"
        "Оплатить доступ к AI-функциям можно по этой ссылке:\n"
        "https://yourpaymentpage.com\n\n"
        "После оплаты тебе откроются:\n"
        "— Генерация контента\n"
        "— Видео по шаблону\n"
        "— Голос в текст\n"
        "— Автопостинг и план"
    )

    requests.post(TELEGRAM_API_URL, json={
        'chat_id': chat_id,
        'text': message
    })

