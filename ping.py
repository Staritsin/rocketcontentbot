import requests
import time

# Сюда вставь ссылку на свой бот
URL = 'https://rocketcontentbot.onrender.com'  # заменишь на свою

while True:
    try:
        response = requests.get(URL)
        print('✅ Пинг отправлен:', response.status_code)
    except Exception as e:
        print('❌ Ошибка пинга:', e)
    
    time.sleep(600)  # каждые 10 минут
