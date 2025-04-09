from flask import Flask, request
import requests
import os

app = Flask(__name__)
BOT_TOKEN = '8056198011:AAFZMYMpWGvOjhEucRhquBJ1Hoc0d8y0K6s'
TELEGRAM_API_URL = f'https://api.telegram.org/bot{BOT_TOKEN}/sendMessage'
TELEGRAM_FILE_API = f'https://api.telegram.org/file/bot{BOT_TOKEN}/'

@app.route('/')
def index():
    return 'Бот работает!'

@app.route('/telegram', methods=['POST'])
def telegram_webhook():
    data = request.get_json()

    if 'message' in data:
        chat_id = data['message']['chat']['id']
        message = data['message']
        
        if 'video' in message:
            file_id = message['video']['file_id']
            # Получаем ссылку на файл
            file_info = requests.get(f"https://api.telegram.org/bot{BOT_TOKEN}/getFile?file_id={file_id}").json()
            file_path = file_info['result']['file_path']
            file_url = TELEGRAM_FILE_API + file_path

            # Скачиваем видео
            video_data = requests.get(file_url)
            video_filename = f"video_{file_id}.mp4"
            with open(video_filename, 'wb') as f:
                f.write(video_data.content)

            reply = f"Видео получено и сохранено как {video_filename}"

        elif 'text' in message:
            text = message['text']
            reply = f"Ты написал: {text}"

        else:
            reply = "Я пока не знаю, что с этим делать..."

        # Ответ пользователю
        requests.post(TELEGRAM_API_URL, json={
            'chat_id': chat_id,
            'text': reply
        })

    return 'ok'

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=10000)
