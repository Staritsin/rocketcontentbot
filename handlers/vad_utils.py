import subprocess
import os

def remove_silence(input_path, output_path):
    try:
        print("[Шаг 1] Проверка расширения:", input_path)

        # Если .mov — конвертируем
        if input_path.lower().endswith('.mov'):
            mp4_path = input_path.replace('.mov', '_converted.mp4')
            print(f"[Шаг 2] Конвертирую .mov → .mp4 → {mp4_path}")
            subprocess.run([
                "ffmpeg", "-y", "-i", input_path,
                "-vcodec", "libx264", "-acodec", "aac",
                mp4_path
            ], check=True)
            input_path = mp4_path

        # Удаление тишины
        print(f"[Шаг 3] Удаляю тишину в файле {input_path}")
        result = subprocess.run([
            "auto-editor",
            input_path,
            "--edit", "audio:threshold=3%",
            "--frame_margin", "2",
            "--video-speed", "1",
            "--export", "default",
            "--output-file", output_path,
            "--video-codec", "libx264"
        ], check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

        print("[Шаг 4] STDOUT:", result.stdout.decode())
        print("[Шаг 5] STDERR:", result.stderr.decode())
        print("[Шаг 6] ✅ Тишина удалена. Файл сохранён:", output_path)

        return output_path

    except subprocess.CalledProcessError as e:
        print("[ОШИБКА] Ошибка при удалении тишины")
        print("[STDERR]:", e.stderr.decode() if e.stderr else "нет stderr")
        print("[STDOUT]:", e.stdout.decode() if e.stdout else "нет stdout")
        return None
