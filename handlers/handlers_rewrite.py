import os
import requests
from telegram import InlineKeyboardButton
import handlers.state as state
from handlers.telegram_webhook_fix import ask_for_rating

BOT_TOKEN = os.environ.get('BOT_TOKEN')
OPENAI_API_KEY = os.environ.get('OPENAI_API_KEY')

TELEGRAM_API_URL = f'https://api.telegram.org/bot{BOT_TOKEN}/sendMessage'


def handle_rewrite(chat_id):
    text = (
        "✍️ Рерайт текста\n"
        "Отправь мне текст, и я перепишу его — сделаю более цепляющим, лаконичным или адаптирую под соцсети."
    )
    requests.post(TELEGRAM_API_URL, json={
        'chat_id': chat_id,
        'text': text
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

        # обновляем состояние с новым текстом
        user_states[chat_id]['last_transcript'] = rewritten

        # отправляем результат
        requests.post(TELEGRAM_API_URL, json={
            'chat_id': chat_id,
            'text': f"✍️ Рерайт:\n{rewritten}"
        })

        # кнопки после рерайта
        keyboard = [
            [InlineKeyboardButton("📤 Использовать как пост", callback_data='use_as_post')],
            [InlineKeyboardButton("🎬 Сделать Reels", callback_data='make_reels')],
            [InlineKeyboardButton("🌟 Всё получилось", callback_data='success')],
            [InlineKeyboardButton("🔙 Вернуться в меню", callback_data='menu')]
        ]
        reply_markup = {
            'inline_keyboard': [[btn.to_dict() for btn in row] for row in keyboard]
        }

        requests.post(TELEGRAM_API_URL, json={
            'chat_id': chat_id,
            'text': "Что делаем дальше? 👇",
            'reply_markup': reply_markup
        })

        # оценка
        ask_for_rating(chat_id)

    except Exception as e:
        requests.post(TELEGRAM_API_URL, json={
            'chat_id': chat_id,
            'text': f"❌ Ошибка рерайта: {e}"
        })
