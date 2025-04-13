# handlers_subtitles.py

import os
import requests

BOT_TOKEN = os.environ.get('BOT_TOKEN')
TELEGRAM_API_URL = f'https://api.telegram.org/bot{BOT_TOKEN}/sendMessage'


def generate_srt(transcript_text):
    """
    Преобразует текст в .srt формат для наложения субтитров
    """
    phrases = transcript_text.split(". ")
    srt_lines = []

    for i, phrase in enumerate(phrases):
        start_time = timedelta(seconds=i * 2)
        end_time = timedelta(seconds=(i + 1) * 2)
        start_str = str(start_time).split(".")[0]
        end_str = str(end_time).split(".")[0]

        start_str = "0" + start_str if len(start_str) == 7 else start_str
        end_str = "0" + end_str if len(end_str) == 7 else end_str

        srt_lines.append(f"{i+1}")
        srt_lines.append(f"{start_str},000 --> {end_str},000")
        srt_lines.append(phrase.strip())
        srt_lines.append("")

    return "\n".join(srt_lines)

def save_subtitles_file(text, filename="/tmp/subtitles.srt"):
    srt_content = generate_srt(text)
    with open(filename, "w", encoding="utf-8") as f:
        f.write(srt_content)
    return filename

def handle_subtitles(chat_id):
    text = (
        "🎞 Субтитры для видео\n"
        "Отправь видео или текст — я наложу субтитры автоматически."
    )
    requests.post(TELEGRAM_API_URL, json={
        'chat_id': chat_id,
        'text': text
    })

# handlers/handlers_subtitles.py

def generate_subtitles(chat_id, transcript_text, video_url):
    """
    Заглушка: в будущем добавим реальную вставку в видео.
    Пока просто сохраняем .srt и выводим путь.
    """
    path = save_subtitles_file(transcript_text)
    print(f"✅ Субтитры сгенерированы: {path}")
    return path
    
def handle_publish(chat_id):
    text = (
        "📤 Публикация контента\n"
        "Выбери, куда опубликовать: Instagram, Telegram, VK и другие.\n"
        "Скоро добавим автоматический постинг."
    )
    requests.post(TELEGRAM_API_URL, json={
        'chat_id': chat_id,
        'text': text
    })
