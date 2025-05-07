from handlers.utils import send_message

def handle_stories_pipeline(chat_id, file_id):
    send_message(chat_id, f"📱 Видео {file_id} получено! Запускаю обработку под Stories.")
