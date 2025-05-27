import subprocess
import os
from handlers.utils import send_message  # 👈 обязательно подключи

def remove_silence(chat_id, input_path, output_path):
    try:
        send_message(chat_id, f"[1] 🎬 Начинаю удаление тишины из: {os.path.basename(input_path)}")
        print(f"[1] Начало обработки файла: {input_path}")

        # Конвертация .mov → .mp4
        if input_path.lower().endswith('.mov'):
            mp4_path = input_path.replace('.mov', '_converted.mp4')
            send_message(chat_id, f"[2] 🔁 Конвертирую MOV → MP4: {os.path.basename(mp4_path)}")
            print(f"[2] Конвертация в .mp4: {mp4_path}")
            subprocess.run([
                "ffmpeg", "-y", "-i", input_path,
                "-vcodec", "libx264", "-acodec", "aac",
                mp4_path
            ], check=True)
            input_path = mp4_path

        # Удаление тишины
        send_message(chat_id, f"[3] 🔇 Запускаю auto-editor для: {os.path.basename(input_path)}")
        print(f"[3] Запуск auto-editor для {input_path} → {output_path}")

        result = subprocess.run([
            "auto-editor",
            input_path,
            "--edit", "audio:threshold=3%",
            "--frame_margin", "2",
            "--video-speed", "1",
            "--export", "default",  # ⚠️ ВАЖНО: "video" → "default"
            "--output-file", output_path,
            "--video-codec", "libx264"
        ], check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

        # Успех
        send_message(chat_id, "✅ Тишина удалена. Видео готово.")
        print("[4] ✅ Успешно. Output файл:", output_path)

        return output_path

    except subprocess.CalledProcessError as e:
        send_message(chat_id, f"❌ Ошибка в auto-editor: {e}")
        stderr = e.stderr.decode() if e.stderr else "нет stderr"
        stdout = e.stdout.decode() if e.stdout else "нет stdout"
        print("[ОШИБКА] stderr:", stderr)
        print("[ОШИБКА] stdout:", stdout)
        return None
