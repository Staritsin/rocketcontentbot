import subprocess
import os

def remove_silence(input_path, output_path):
    try:
        # Конвертируем в промежуточный .mp4, если входной — .mov
        if input_path.lower().endswith('.mov'):
            temp_mp4 = input_path.replace('.mov', '_converted.mp4')
            subprocess.run([
                "ffmpeg", "-y", "-i", input_path,
                "-vcodec", "libx264", "-acodec", "aac",
                temp_mp4
            ], check=True)
            input_path = temp_mp4

        # Удаляем тишину, сохраняем видео
        subprocess.run([
            "auto-editor",
            input_path,
            "--edit", "audio:threshold=3%",
            "--frame_margin", "2",
            "--video-speed", "1",
            "--export", "video",
            "--output-file", output_path,
            "--video-codec", "libx264"
        ], check=True)

        return output_path

    except subprocess.CalledProcessError as e:
        print(f"[ERROR] Ошибка при обработке видео: {e}")
        return None
