import requests
import os
from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from handlers.state import user_states
from handlers.telegram_webhook_fix import ask_for_rating

BOT_TOKEN = os.environ.get('BOT_TOKEN')
OPENAI_API_KEY = os.environ.get('OPENAI_API_KEY')

TELEGRAM_API_URL = f'https://api.telegram.org/bot{BOT_TOKEN}'
TELEGRAM_FILE_API = f'https://api.telegram.org/file/bot{BOT_TOKEN}'

def handle_voice(chat_id):
    text = (
        "🎙️ Работа с голосом\n"
        "Отправь мне голосовое, аудио или видео — я превращу его в текст...\n"
        "Затем ты сможешь сделать рерайт или использовать текст для генерации поста или видео."
    )
    requests.post(f'{TELEGRAM_API_URL}/sendMessage', json={
        'chat_id': chat_id,
        'text': text
    })

def handle_voice_transcription(chat_id, file_id):
    try:
        file_info = requests.get(f"{TELEGRAM_API_URL}/getFile?file_id={file_id}").json()
        file_path = file_info['result']['file_path']
        file_url = f"{TELEGRAM_FILE_API}/{file_path}"

        audio_content = requests.get(file_url).content

        local_filename = "voice.ogg"
        with open(local_filename, "wb") as f:
            f.write(audio_content)

        with open(local_filename, "rb") as f:
            response = requests.post(
                "https://api.openai.com/v1/audio/transcriptions",
                headers={"Authorization": f"Bearer {OPENAI_API_KEY}"},
                files={"file": f},
                data={"model": "whisper-1"}
            )

        result = response.json()
        text = result.get("text", "❌ Не удалось распознать речь.")
        if chat_id not in user_states:
            user_states[chat_id] = {}
        user_states[chat_id]['last_transcript'] = text


        requests.post(f'{TELEGRAM_API_URL}/sendMessage', json={
            'chat_id': chat_id,
            'text': f"📝 Расшифровка:\n{text}"
        })

        keyboard = [
            [InlineKeyboardButton("✍️ Сделать рерайт", callback_data='rewrite_transcript')],
            [InlineKeyboardButton("📤 Использовать как пост", callback_data='use_as_post')],
            [InlineKeyboardButton("🎬 Сделать Reels", callback_data='make_reels')],
            [InlineKeyboardButton("🌟 Всё получилось", callback_data='success')],
            [InlineKeyboardButton("🔙 Вернуться в меню", callback_data='menu')]
        ]
        reply_markup = {'inline_keyboard': [[btn.to_dict() for btn in row] for row in keyboard]}

        requests.post(f'{TELEGRAM_API_URL}/sendMessage', json={
            'chat_id': chat_id,
            'text': "Что делаем дальше? 👇",
            'reply_markup': reply_markup
        })

        ask_for_rating(chat_id)

    except Exception as e:
        requests.post(f'{TELEGRAM_API_URL}/sendMessage', json={
            'chat_id': chat_id,
            'text': f"❌ Ошибка обработки аудио: {e}"
        })

def handle_rewrite_transcript(chat_id):
    try:
        last_text = state.user_states.get(chat_id, {}).get('last_transcript')
        if not last_text:
            raise ValueError("Текст не найден для рерайта")

        prompt = f"Сделай рерайт следующего текста, сохранив смысл и структуру:\n\n{last_text}"
        response = requests.post(
            "https://api.openai.com/v1/chat/completions",
            headers={
                "Authorization": f"Bearer {OPENAI_API_KEY}",
                "Content-Type": "application/json"
            },
            json={
                "model": "gpt-3.5-turbo",
                "messages": [
                    {"role": "system", "content": "Ты опытный копирайтер."},
                    {"role": "user", "content": prompt}
                ]
            }
        )
        result = response.json()
        rewritten = result['choices'][0]['message']['content']

        requests.post(f'{TELEGRAM_API_URL}/sendMessage', json={
            'chat_id': chat_id,
            'text': f"✍️ Рерайт:\n{rewritten}"
        })

    except Exception as e:
        requests.post(f'{TELEGRAM_API_URL}/sendMessage', json={
            'chat_id': chat_id,
            'text': f"❌ Ошибка рерайта: {e}"
        })
def handle_transcribe_input(chat_id, message):
    try:
        if 'video' in message:
            file_id = message['video']['file_id']
        elif 'document' in message:
            file_id = message['document']['file_id']
        elif 'audio' in message:
            file_id = message['audio']['file_id']
        elif 'voice' in message:
            file_id = message['voice']['file_id']
        else:
            raise ValueError("Нет поддерживаемого видео, документа или аудио.")

        handle_voice_transcription(chat_id, file_id)

    except Exception as e:
        requests.post(f'{TELEGRAM_API_URL}/sendMessage', json={
            'chat_id': chat_id,
            'text': f"❌ Ошибка: {e}"
        })
