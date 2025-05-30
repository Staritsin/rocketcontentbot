from handlers.rewrite_utils import publish_video, generate_subtitles, insert_clips
from handlers.utils import send_message
from handlers.state import user_states

def handle_user_choice(chat_id, text):
    video_path = user_states.get(chat_id, {}).get("last_video_path")
    
    if not video_path:
        send_message(chat_id, "⚠️ Видео не найдено. Сначала отправь видео.")
        return

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
