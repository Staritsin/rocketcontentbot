import subprocess
import os

def remove_silence(input_path, output_path):
    try:
        # Конвертируем .mov → .mp4, если нужно
        if input_path.lower().endswith('.mov'):
            mp4_path = input_path.replace('.mov', '_converted.mp4')
            subprocess.run([
                "ffmpeg", "-y", "-i", input_path,
                "-vcodec", "libx264", "-acodec", "aac",
                mp4_path
            ], check=True)
            input_path = mp4_path

        # Обрезка тишины через ffmpeg silenceremove
        subprocess.run([
            "ffmpeg", "-y", "-i", input_path,
            "-af", "silenceremove=start_periods=1:start_duration=0.5:start_threshold=-50dB:\
detection=peak,areverse,silenceremove=start_periods=1:start_duration=0.5:start_threshold=-50dB:\
detection=peak,areverse",
            "-c:v", "copy",
            output_path
        ], check=True)

        return output_path

    except subprocess.CalledProcessError as e:
        print(f"[ERROR] Ошибка при удалении тишины: {e}")
        return None
