from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    MessageHandler,
    CallbackQueryHandler,
    ContextTypes,
    filters,
)
import os

from handlers.utils import send_message
from handlers.state import user_states
from handlers.handlers_buttons import (
    send_story_action_buttons,
    handle_story_action_callback,
    handle_user_choice,
)
from handlers.handlers_stories import (
    handle_single_video_processing,
    process_stories_multiple,
    handle_stories_pipeline
)
from handlers.handlers_video import handle_video
from handlers.handlers_reels import handle_transcribe
from handlers.handlers_text import handle_text
from handlers.handlers_image import handle_image
from handlers.handlers_translate import handle_translate
from handlers.handlers_plan import handle_plan
from handlers.handlers_subtitles import handle_subtitles
from handlers.handlers_publish import handle_publish
from handlers.handlers_voice import handle_voice, handle_voice_transcription
from handlers.handlers_runway import handle_capcut
from handlers.handlers_support import handle_support
from handlers.handlers_pay import handle_pay
from handlers.handlers_post import handle_post_platform_selection
from handlers.handlers_notify import notify_task_success

BOT_TOKEN = os.getenv("BOT_TOKEN")

menu_keyboard = [
    ["📚 Stories", "🧠 Вытащить Текст"],
    ["🎬 Скачать видео в Mp4", "🎞 REELS"],
    ["📚 Переводчик", "🖼 Фото"],
    ["📜 Подписка", "📂 Контент"],
    ["🛠 Поддержка"]
]
menu_markup = ReplyKeyboardMarkup(menu_keyboard, resize_keyboard=True)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id
    await context.bot.send_message(
        chat_id=chat_id,
        text="Контент машина запущена! Что будем делать? 👇",
        reply_markup=menu_markup,
    )

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text
    chat_id = update.effective_chat.id
    state = user_states.get(chat_id, {}).get("mode")

    if text == "📚 Stories":
        send_story_action_buttons(chat_id)
    elif text == "🧠 Вытащить Текст":
        await handle_text(update, context)
    elif text == "🎬 Скачать видео в Mp4":
        await handle_video(update, context)
    elif text == "🎞 REELS":
        await handle_transcribe(update, context)
    elif text == "📚 Переводчик":
        await handle_translate(update, context)
    elif text == "🖼 Фото":
        await handle_image(update, context)
    elif text == "📜 Подписка":
        await handle_plan(update, context)
    elif text == "📂 Контент":
        await handle_publish(update, context)
    elif text == "🛠 Поддержка":
        await handle_support(update, context)
    elif text.isdigit():
        await handle_user_choice(chat_id, text, user_states[chat_id].get("video"))
    else:
        await context.bot.send_message(chat_id=chat_id, text="Не понял команду. Выбери кнопку из меню.")

async def handle_video_file(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id
    state = user_states.get(chat_id, {}).get("mode")
    if state == "single_processing":
        await handle_single_video_processing(update, context)
    elif state == "stories_multiple":
        await process_stories_multiple(update, context)

async def handle_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    chat_id = query.message.chat_id
    data = query.data
    handle_story_action_callback(chat_id, data)

if __name__ == "__main__":
    app = ApplicationBuilder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    app.add_handler(MessageHandler(filters.VIDEO, handle_video_file))
    app.add_handler(MessageHandler(filters.VOICE, handle_voice))
    app.add_handler(CallbackQueryHandler(handle_callback))
    app.run_polling()
