import requests
import os
from telegram import InlineKeyboardButton, InlineKeyboardMarkup

BOT_TOKEN = os.environ.get('BOT_TOKEN')
TELEGRAM_API_URL = f'https://api.telegram.org/bot{BOT_TOKEN}'

# Хранилище состояния пользователя
user_states = {}

def handle_post_platform_selection(chat_id):
    text = "Выбери, куда хочешь опубликовать пост 👇"
    keyboard = [
        [InlineKeyboardButton("📸 Instagram", callback_data='post_instagram')],
        [InlineKeyboardButton("🗣 Telegram", callback_data='post_telegram')],
        [InlineKeyboardButton("📬 Спам-рассылка", callback_data='post_spam')],
        [InlineKeyboardButton("📢 ВКонтакте", callback_data='post_vk')],
        [InlineKeyboardButton("🔙 Вернуться в меню", callback_data='menu')]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard).to_dict()

    requests.post(f'{TELEGRAM_API_URL}/sendMessage', json={
        'chat_id': chat_id,
        'text': text,
        'reply_markup': reply_markup
    })

def generate_platform_post(chat_id, platform):
    last_text = user_states.get(chat_id, {}).get('last_transcript')
    if not last_text:
        requests.post(f'{TELEGRAM_API_URL}/sendMessage', json={
            'chat_id': chat_id,
            'text': "❌ Нет текста для публикации. Сначала сделай транскрибацию."
        })
        return

    if platform == 'instagram':
        text = f"📸 Instagram пост:\n\n{last_text}\n\n👉 Напиши в комменты, что думаешь!"

    elif platform == 'telegram':
        text = f"🗣 Telegram пост:\n\n{last_text}"

    elif platform == 'spam':
        preview = last_text[:300].strip()
        text = (
            f"📬 Спам-рассылка:\n\n"
            f"**Заголовок:** {preview[:50]}...\n"
            f"**Текст:** {preview}\n"
            f"[📌 Подробнее](https://your-link.com)"
        )

    elif platform == 'vk':
        text = f"📢 Пост для ВКонтакте:\n\n{last_text}\n\n#контент #бот #искусственныйинтеллект"

    else:
        text = "❌ Неизвестная платформа"

    requests.post(f'{TELEGRAM_API_URL}/sendMessage', json={
        'chat_id': chat_id,
        'text': text,
        'parse_mode': 'Markdown'
    })

def handle_rewrite_transcript(chat_id):
    import json

    last_text = user_states.get(chat_id, {}).get('last_transcript')
    if not last_text:
        requests.post(f'{TELEGRAM_API_URL}/sendMessage', json={
            'chat_id': chat_id,
            'text': "❌ Текст для рерайта не найден. Сначала сделай транскрибацию."
        })
        return

    prompt = f"Сделай рерайт следующего текста, сохранив смысл и структуру:\n\n{last_text}"
    try:
        response = requests.post(
            "https://api.openai.com/v1/chat/completions",
            headers={
                "Authorization": f"Bearer {os.environ.get('OPENAI_API_KEY')}",
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
