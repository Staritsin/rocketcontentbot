
from flask import Flask, request, jsonify
import requests
import yt_dlp
import re
import os

app = Flask(__name__)
BOT_TOKEN = os.environ.get('BOT_TOKEN')
OPENAI_API_KEY = os.environ.get('OPENAI_API_KEY')
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

        if 'text' in message:
            text = message['text']

            if text.lower() == '/start':
                reply = "Привет! Я бот для создания Reels. Напиши /menu, чтобы выбрать действие."
           
            elif text.lower() == '/menu':
    reply =
    """Выбери действие:
/generate – Создать Reels
/support – Техподдержка
/pay – Оплатить подписку"""
      
            elif text.lower() == '/support':
                reply = "Напиши в поддержку: @your_support_username"
            elif text.lower() == '/generate':
                reply = "Отправь видео или ссылку на Reels, TikTok, YouTube и т.д."
            elif text.lower() == '/pay':
                reply = "Оплатить можно тут: https://yourpaymentpage.com"
            elif re.search(r'https?://[^\s]+', text):
                download_url = f"https://rocketcontentbot.onrender.com/download?url={text}"
                try:
                    result = requests.get(download_url).json()
                    if 'filename' in result:
                        reply = f"Видео загружено: {result['filename']}"
                    else:
                        reply = f"Ошибка при скачивании: {result.get('error', 'Неизвестная ошибка')}"
                except Exception as e:
                    reply = f"Ошибка при загрузке: {str(e)}"
            else:
                reply = f"Ты написал: {text}"

        elif 'video' in message:
            file_id = message['video']['file_id']
            file_info = requests.get(f"https://api.telegram.org/bot{BOT_TOKEN}/getFile?file_id={file_id}").json()
            file_path = file_info['result']['file_path']
            file_url = TELEGRAM_FILE_API + file_path

            video_data = requests.get(file_url)
            video_filename = f"video_{file_id}.mp4"
            with open(video_filename, 'wb') as f:
                f.write(video_data.content)

            reply = f"Видео получено и сохранено как {video_filename}"

        elif 'voice' in message:
            file_id = message['voice']['file_id']
            file_info = requests.get(f"https://api.telegram.org/bot{BOT_TOKEN}/getFile?file_id={file_id}").json()
            file_path = file_info['result']['file_path']
            file_url = TELEGRAM_FILE_API + file_path

            ogg_data = requests.get(file_url)
            ogg_filename = f"voice_{file_id}.ogg"
            with open(ogg_filename, 'wb') as f:
                f.write(ogg_data.content)

            whisper_response = requests.post(
                'https://api.openai.com/v1/audio/transcriptions',
                headers={'Authorization': f'Bearer {OPENAI_API_KEY}'},
                files={
                    'file': (ogg_filename, open(ogg_filename, 'rb')),
                    'model': (None, 'whisper-1')
                }
            )

            if whisper_response.status_code == 200:
                text_result = whisper_response.json()['text']
                reply = f"Твой голос: {text_result}"
            else:
                reply = f"Ошибка при распознавании голоса"

        else:
            reply = "Я пока не знаю, что с этим делать..."

        requests.post(TELEGRAM_API_URL, json={
            'chat_id': chat_id,
            'text': reply
        })

    return 'ok'

@app.route('/download', methods=['GET'])
def download():
    url = request.args.get('url')
    if not url:
        return jsonify({'error': 'No URL provided'}), 400

    try:
        ydl_opts = {
            'format': 'mp4',
            'quiet': True,
            'outtmpl': 'downloaded_video.%(ext)s',
        }

        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info_dict = ydl.extract_info(url, download=True)
            video_file = ydl.prepare_filename(info_dict)
            return jsonify({
                'title': info_dict.get('title'),
                'filename': video_file
            })

    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=10000)
