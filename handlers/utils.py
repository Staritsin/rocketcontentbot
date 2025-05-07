import os
import requests

def get_file_url(file_id):
    BOT_TOKEN = os.getenv("BOT_TOKEN")
    file_path_resp = requests.get(f"https://api.telegram.org/bot{BOT_TOKEN}/getFile?file_id={file_id}")
    file_path = file_path_resp.json()["result"]["file_path"]
    return f"https://api.telegram.org/file/bot{BOT_TOKEN}/{file_path}"

def download_telegram_file(file_id, local_path):
    BOT_TOKEN = os.getenv("BOT_TOKEN")
    file_info_url = f"https://api.telegram.org/bot{BOT_TOKEN}/getFile?file_id={file_id}"
    file_path = requests.get(file_info_url).json()["result"]["file_path"]
    file_url = f"https://api.telegram.org/file/bot{BOT_TOKEN}/{file_path}"
    with open(local_path, "wb") as f:
        f.write(requests.get(file_url).content)

def send_message(chat_id, text):
    requests.post(
        f"https://api.telegram.org/bot{os.getenv('BOT_TOKEN')}/sendMessage",
        json={"chat_id": chat_id, "text": text}
    )

# Токен Telegram бота
BOT_TOKEN = os.environ.get('BOT_TOKEN')

# Основной URL Telegram API
TELEGRAM_API_URL = f'https://api.telegram.org/bot{BOT_TOKEN}/sendMessage'

# URL для загрузки файлов из Telegram
TELEGRAM_FILE_API = f'https://api.telegram.org/file/bot{BOT_TOKEN}/'

# OpenAI API ключ
OPENAI_API_KEY = os.environ.get('OPENAI_API_KEY')

# Whisper endpoint (можно использовать в разных обработчиках)
WHISPER_API_URL = 'https://api.openai.com/v1/audio/transcriptions'

# Универсальная функция отправки сообщений в Telegram
def send_message(chat_id, text):
    import requests
    requests.post(TELEGRAM_API_URL, json={
        'chat_id': chat_id,
        'text': text
    })
