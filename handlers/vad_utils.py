import subprocess
import os
from handlers.utils import send_message  # 👈 обязательно подключи

def remove_silence(chat_id, input_path, output_path):
    try:
        command = [
            "auto-editor", input_path,
            "--edit", "audio:threshold=4%",
            "--frame_margin", "6",
            "--min-clip-length", "1.0",
            "--video-speed", "1",
            "--mark-as-loud", "0.02",
            "--export", "default",
            "--output-file", output_path,
            "--video-codec", "libx264"
        ]

        print(f"[DEBUG] Running auto-editor: {' '.join(command)}")
        subprocess.run(command, check=True)

        return output_path

    except subprocess.CalledProcessError as e:
        print(f"[ERROR] Auto-editor failed: {e}")
        return None


        # Удаление тишины
        send_message(chat_id, f"[3] 🔇 Запускаю auto-editor для: {os.path.basename(input_path)}")
        print(f"[3] Запуск auto-editor для {input_path} → {output_path}")

        subprocess.run([
            "auto-editor",
            input_path,
            "--edit", "audio:threshold=2%",
            "--frame_margin", "10",
            "--min-clip-length", "0.5",
            "--video-speed", "1",
            "--mark-as-loud", "0.015",
            "--export", "default",
            "--output-file", output_path,
            "--video-codec", "libx264"
        ], check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)


        # Успех
        send_message(chat_id, "✅ Тишина удалена. Видео готово.")
        print("[4] ✅ Успешно. Output файл:", output_path)

        if not os.path.exists(output_path):
            send_message(chat_id, f"⚠️ Auto-Editor отработал, но файл не найден: {output_path}")
            print(f"[ОШИБКА] Нет файла после обработки: {output_path}")
            return None


        return output_path

    except subprocess.CalledProcessError as e:
        send_message(chat_id, f"❌ Ошибка в auto-editor: {e}")
        stderr = e.stderr.decode() if e.stderr else "нет stderr"
        stdout = e.stdout.decode() if e.stdout else "нет stdout"
        print("[ОШИБКА] stderr:", stderr)
        print("[ОШИБКА] stdout:", stdout)
        return None
