from flask import Flask, request
import requests
import os

app = Flask(__name__)
BOT_TOKEN = '8056198011:AAFZMYMpWGvOjhEucRhquBJ1Hoc0d8y0K6s'
TELEGRAM_API_URL = f'https://api.telegram.org/bot{BOT_TOKEN}/sendMessage'

@app.route('/')
def index():
    return 'Бот работает!'

@app.route('/telegram', methods=['POST'])
def telegram_webhook():
    data = request.get_json()

    if 'message' in data:
        chat_id = data['message']['chat']['id']
        if 'text' in data['message']:
            text = data['message']['text']
            reply = f"Ты написал: {text}"
        elif 'voice' in data['message']:
            reply = f"Я получил голосовое сообщение!"
        elif 'photo' in data['message']:
            reply = f"Фото получено!"
        elif 'video' in data['message']:
            reply = f"Видео получено!"
        else:
            reply = "Я пока не знаю, что с этим делать..."

        requests.post(TELEGRAM_API_URL, json={
            'chat_id': chat_id,
            'text': reply
        })

    return 'ok'

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=10000)
