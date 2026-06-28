"""
Start command handler for the Escrow Bot.
Handles /start command and the START button callback.
"""
from telegram import Update
from telegram.ext import ContextTypes

from utils.keyboards import start_keyboard, escrow_type_keyboard
from utils.formatting import format_start_message


async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle /start command - show welcome message and menu."""
    await update.message.reply_text(
        text=format_start_message(),
        parse_mode="HTML",
        reply_markup=start_keyboard(),
    )


async def start_button_callback(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle the START button press."""
    query = update.callback_query
    await query.answer()
    
    await query.edit_message_text(
        text=(
            "🚀 <b>READY TO START!</b>\n"
            "━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
            "Use /escrow to create a new escrow deal.\n\n"
            "📋 <b>Quick Guide:</b>\n"
            "1️⃣ Create escrow with /escrow\n"
            "2️⃣ Join the escrow group\n"
            "3️⃣ Fill deal details with /dd\n"
            "4️⃣ Declare roles: /seller & /buyer\n"
            "5️⃣ Select token with /token\n"
            "6️⃣ Deposit with /deposit\n"
            "7️⃣ Release or refund when ready\n\n"
            "💡 Type /help for more information."
        ),
        parse_mode="HTML",
    )
