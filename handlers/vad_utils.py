import subprocess
import os
from handlers.utils import send_message


def remove_silence(chat_id, input_path, output_path):
    try:
        # Этап 1: Уведомляем пользователя
        send_message(chat_id, f"[1] 🛠️ Начинаю обработку файла: {os.path.basename(input_path)}")
        print(f"[1] Получен файл: {input_path} → будет сохранён как: {output_path}")

        # Этап 2: Составляем команду
        command = [
            "auto-editor",
            input_path,
            "--edit", "audio:threshold=2%",
            "--frame_margin", "10",
            "--min_clip_length", "0.5",
            "--mark_as_loud", "0.015",
            "--video_speed", "1",
            "--output_file", output_path,
            "--video_codec", "libx264"
        ]

        print(f"[2] Команда auto-editor:\n{' '.join(command)}")

        # Этап 3: Запускаем auto-editor
        send_message(chat_id, "[2] 🔇 Запускаю auto-editor...")
        result = subprocess.run(command, capture_output=True, text=True, check=True)

        print(f"[3] Auto-editor stdout:\n{result.stdout}")
        print(f"[3] Auto-editor stderr:\n{result.stderr}")

        # Этап 4: Проверка существования выходного файла
        if not os.path.exists(output_path):
            send_message(chat_id, f"⚠️ Обработка завершилась, но файл не найден: {output_path}")
            print(f"[ОШИБКА] Файл не найден: {output_path}")
            return None

        # Этап 5: Успех
        send_message(chat_id, "✅ Тишина удалена. Видео готово.")
        print(f"[4] ✅ Готово! Файл сохранён: {output_path}")
        return output_path

    except subprocess.CalledProcessError as e:
        send_message(chat_id, f"❌ Ошибка при выполнении auto-editor: {e}")
        print(f"[ОШИБКА] subprocess error: {e}")
        print(f"stdout: {e.stdout}")
        print(f"stderr: {e.stderr}")
        return None

    except Exception as e:
        send_message(chat_id, f"❌ Общая ошибка: {str(e)}")
        print(f"[ОШИБКА] remove_silence(): {str(e)}")
        return None
