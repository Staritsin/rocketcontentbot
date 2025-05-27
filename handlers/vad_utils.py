import subprocess
import os

def remove_silence(input_path, output_path):
    try:
        # Если формат .mov, конвертируем в mp4
        if input_path.lower().endswith('.mov'):
            mp4_path = input_path.replace('.mov', '_converted.mp4')
            subprocess.run([
                "ffmpeg", "-y", "-i", input_path,
                "-vcodec", "libx264", "-acodec", "aac",
                mp4_path
            ], check=True)
            input_path = mp4_path

        # Удаление тишины с правильным export
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

        print("[DEBUG] STDOUT:", result.stdout.decode())
        print("[DEBUG] STDERR:", result.stderr.decode())
        print("[DEBUG] Тишина удалена. Файл сохранён:", output_path)
        return output_path

    except subprocess.CalledProcessError as e:
        print("[ERROR] Ошибка при удалении тишины:")
        print(e)
        print("[STDERR]:", e.stderr.decode() if e.stderr else "нет stderr")
        print("[STDOUT]:", e.stdout.decode() if e.stdout else "нет stdout")
        return None
