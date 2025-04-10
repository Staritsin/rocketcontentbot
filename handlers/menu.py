# handlers/menu.py
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import CallbackContext

def menu(update: Update, context: CallbackContext):
    """
    Handler function for the /menu command. 
    Displays an inline keyboard with options for the user to choose actions.
    """
    # Define the buttons for the menu
    keyboard = [
        [
            InlineKeyboardButton("📹 Видео с телефона", callback_data="upload_video"),
            InlineKeyboardButton("🔗 Ссылка на Reels", callback_data="reels_link"),
        ],
        [
            InlineKeyboardButton("📝 Генерация текста", callback_data="generate_text"),
            InlineKeyboardButton("📜 Сценарий текста", callback_data="script_text"),
        ],
        [
            InlineKeyboardButton("💳 Оплата", callback_data="payment"),
            InlineKeyboardButton("🛠 Техподдержка", callback_data="support"),
        ],
    ]

    # Create the inline keyboard markup
    reply_markup = InlineKeyboardMarkup(keyboard)

    # Send the message with the inline keyboard
    update.message.reply_text(
        "Выберите действие из меню ниже:",
        reply_markup=reply_markup
    )
