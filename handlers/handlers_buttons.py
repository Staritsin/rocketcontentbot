from telegram import InlineKeyboardButton
from handlers.rewrite_utils import publish_video, generate_subtitles, insert_clips
from handlers.utils import send_message


def handle_user_choice(chat_id, text, video_path):
    if text in ["1", "1️⃣ Опубликовать"]:
        publish_video(chat_id, video_path)
    elif text in ["2", "2️⃣ Субтитры"]:
        generate_subtitles(chat_id, video_path)
    elif text in ["3", "3️⃣ Вставки"]:
        insert_clips(chat_id, video_path)
    elif text in ["4", "4️⃣ Всё сразу"]:
        generate_subtitles(chat_id, video_path)
        insert_clips(chat_id, video_path)
        publish_video(chat_id, video_path)
    else:
        send_message(chat_id, "❓ Не понял выбор. Используй кнопки или цифры от 1 до 4.")


def send_story_action_buttons(chat_id):
    keyboard = [
        [
            InlineKeyboardButton("🎬 Обработать", callback_data="story_process_one"),
            InlineKeyboardButton("🔗 Соединить 2 и более", callback_data="story_merge")
        ],
        [
            InlineKeyboardButton("📤 Опубликовать готовое", callback_data="story_publish_ready")
        ]
    ]
    reply_markup = {
        "inline_keyboard": [[btn.to_dict() for btn in row] for row in keyboard]
    }
    
    import requests
    from os import getenv
    bot_token = getenv("BOT_TOKEN")
    requests.post(f"https://api.telegram.org/bot{bot_token}/sendMessage", json={
        "chat_id": chat_id,
        "text": "📚 Отлично! Выбери, что сделать с видео 👇",
        "reply_markup": reply_markup
    })


def handle_story_action_callback(chat_id, query_data):
    if query_data == "story_process_one":
        send_message(chat_id, "🎬 Окей! Отправь видео для обработки.")
        from handlers.state import user_states
        user_states[chat_id] = {"mode": "stories_processing"}

    elif query_data == "story_merge":
        send_message(chat_id, "🔗 Хорошо! Отправь 2 или больше видео подряд.")
        from handlers.state import user_states
        user_states[chat_id] = {"mode": "stories_multiple"}

    elif query_data == "story_publish_ready":
        keyboard = [
            [
                InlineKeyboardButton("📸 Фото", callback_data="publish_photo"),
                InlineKeyboardButton("🎥 Видео", callback_data="publish_video")
            ]
        ]
        reply_markup = {
            "inline_keyboard": [[btn.to_dict() for btn in row] for row in keyboard]
        }
        from os import getenv
        import requests
        bot_token = getenv("BOT_TOKEN")
        requests.post(f"https://api.telegram.org/bot{bot_token}/sendMessage", json={
            "chat_id": chat_id,
            "text": "📤 Что ты хочешь опубликовать?",
            "reply_markup": reply_markup
        })
        from handlers.state import user_states
        user_states[chat_id] = {"mode": "publish_ready"}

    else:
        send_message(chat_id, "❓ Не понял выбор.")
