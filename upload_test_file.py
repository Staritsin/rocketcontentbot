import shutil

# Откуда берём (предположим, ты закинул файл в handlers/)
src = "handlers/test_input.mov"

# Куда копируем
dst = "uploads/test_input.mov"

shutil.copy(src, dst)
print("✅ Файл успешно скопирован в uploads/")
