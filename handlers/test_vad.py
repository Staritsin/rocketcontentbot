import os
from handlers.vad_utils import extract_voice_segments

UPLOAD_DIR = "uploads"
input_path = os.path.join(UPLOAD_DIR, "test_input.mp4")  # заменишь на свой
output_path = os.path.join(UPLOAD_DIR, "test_output.wav")

def mock_send_message(chat_id, text):
    print(f"[Bot -> {chat_id}] {text}")

if __name__ == "__main__":
    chat_id = "debug_user"
    extract_voice_segments(
        input_path=input_path,
        output_path=output_path,
        chat_id=chat_id,
        send_message=mock_send_message
    )
    print("✅ Готово. Сохранился файл:", output_path)
