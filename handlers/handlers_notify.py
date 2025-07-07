import requests
from os import getenv

TELEGRAM_API_URL = f"https://api.telegram.org/bot{getenv('BOT_TOKEN')}"

def send_message(chat_id, text, parse_mode=None):
    data = {
        'chat_id': chat_id,
        'text': text,
    }
    if parse_mode:
        data['parse_mode'] = parse_mode

    requests.post(f"{TELEGRAM_API_URL}/sendMessage", json=data)


def notify_task_success(chat_id: int, task_id: int):
    message = (
        "Контент машина\n"
        "Ваша задача\n\n"
        "✅ Задача успешно выполнена!\n"
        f"🆔 ID задачи: <a href='https://example.com/task/{task_id}'>{task_id}</a>\n"
        "✍️ Статус: Готово"
    )
    send_message(chat_id, message, parse_mode="HTML")
