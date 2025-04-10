import os

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
