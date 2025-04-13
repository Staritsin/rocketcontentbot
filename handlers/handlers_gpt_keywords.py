import os
import requests

OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY")
GPT_MODEL = "gpt-3.5-turbo"

def extract_keywords_from_text(text, count=5):
    """
    Извлекает ключевые слова из текста с помощью GPT.
    Возвращает список ключевых слов.
    """
    prompt = (
        f"Извлеки {count} ключевых слов или фраз (1-3 слова), которые отражают суть текста.\n"
        f"Ответ верни в формате списка через запятую, без номеров и без лишнего текста:\n\n{text}"
    )

    try:
        response = requests.post(
            "https://api.openai.com/v1/chat/completions",
            headers={
                "Authorization": f"Bearer {OPENAI_API_KEY}",
                "Content-Type": "application/json"
            },
            json={
                "model": GPT_MODEL,
                "messages": [
                    {"role": "system", "content": "Ты маркетолог, умеешь вычленять суть из текста для видео и контента."},
                    {"role": "user", "content": prompt}
                ]
            }
        )

        result = response.json()

        if response.status_code != 200:
            raise Exception(f"Ошибка GPT: {result}")

        keywords_raw = result['choices'][0]['message']['content']
        keywords = [kw.strip().lower() for kw in keywords_raw.split(",") if kw.strip()]
        return keywords

    except Exception as e:
        print(f"[GPT_KEYWORDS] ❌ Ошибка при извлечении ключевых слов: {e}")
        return []
