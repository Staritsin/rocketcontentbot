import os
import requests

# === Константы ===
BOT_TOKEN = os.getenv("BOT_TOKEN")
TELEGRAM_API_URL = f'https://api.telegram.org/bot{BOT_TOKEN}/sendMessage'
TELEGRAM_FILE_API = f'https://api.telegram.org/file/bot{BOT_TOKEN}/'
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
WHISPER_API_URL = 'https://api.openai.com/v1/audio/transcriptions'


# === Отправка сообщений (с кнопками или без) ===
def send_message(chat_id, text, buttons=None):
    payload = {
        "chat_id": chat_id,
        "text": text
    }
    if buttons:
        payload["reply_markup"] = {
            "keyboard": [[{"text": btn} for btn in row] for row in buttons],
            "resize_keyboard": True
        }

    requests.post(TELEGRAM_API_URL, json=payload)


# === Получение URL файла по file_id ===
def get_file_url(file_id):
    file_path_resp = requests.get(
        f"https://api.telegram.org/bot{BOT_TOKEN}/getFile?file_id={file_id}"
    )
    file_path = file_path_resp.json()["result"]["file_path"]
    return f"{TELEGRAM_FILE_API}{file_path}"


# === Скачивание файла из Telegram ===
def download_telegram_file(file_id, local_path):
    file_path = requests.get(
        f"https://api.telegram.org/bot{BOT_TOKEN}/getFile?file_id={file_id}"
    ).json()["result"]["file_path"]
    file_url = f"{TELEGRAM_FILE_API}{file_path}"

    with open(local_path, "wb") as f:
        f.write(requests.get(file_url).content)
