import os
import asyncio
from dotenv import load_dotenv
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, ContextTypes

load_dotenv()
BOT_TOKEN = os.getenv("BOT_TOKEN")

# Telegram API credentials for group creation (get from https://my.telegram.org)
API_ID = int(os.getenv("API_ID", "0"))
API_HASH = os.getenv("API_HASH", "")

# Pyrogram client for creating groups (optional - uses bot token)
pyrogram_client = None

try:
    from pyrogram import Client
    if API_ID and API_HASH and BOT_TOKEN:
        pyrogram_client = Client(
            "escrow_bot",
            api_id=API_ID,
            api_hash=API_HASH,
            bot_token=BOT_TOKEN,
        )
except ImportError:
    pyrogram_client = None


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """/start command - shows the main menu."""
    text = (
        "creates a safe space for your\n"
        "escrow                                              /escrow\n\n"
        "know instructions                           /instructions\n\n"
        "assign yourself as a buyer                /buyer\n\n"
        "assign yourself as a seller                /seller\n\n"
        "get a deposit address                      /deposit\n\n"
        "know your trade balance                  /balance\n\n"
        "to release assets                              /release\n\n"
        "to refund assets                               /refund\n\n"
        "call an administrator                         /dispute\n\n"
        "save your address for future use       /save\n\n"
        "verify escrow address                       /verify"
    )

    keyboard = [[InlineKeyboardButton("START", callback_data="start_menu")]]
    await update.message.reply_text(text=text, reply_markup=InlineKeyboardMarkup(keyboard))


async def start_button(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle START button press."""
    query = update.callback_query
    await query.answer()
    await query.edit_message_text("✅ Welcome! Use /escrow to create a new escrow deal.")


async def escrow(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """/escrow command - asks to select escrow type."""
    keyboard = [
        [
            InlineKeyboardButton("P2P", callback_data="escrow_type_p2p"),
            InlineKeyboardButton("Product Deal", callback_data="escrow_type_product"),
        ]
    ]
    await update.message.reply_text(
        text="Please select your escrow type from below.",
        reply_markup=InlineKeyboardMarkup(keyboard),
    )


async def create_group_pyrogram(user_id: int) -> tuple:
    """Create a supergroup using Pyrogram and return (chat_id, invite_link)."""
    global pyrogram_client
    if not pyrogram_client:
        return None, None

    try:
        async with pyrogram_client:
            # Create supergroup
            group = await pyrogram_client.create_supergroup(
                title="Escrow Group",
                description="P2P Crypto Escrow - Secure Trading Space"
            )
            chat_id = group.id

            # Create invite link with member limit
            invite = await pyrogram_client.create_chat_invite_link(
                chat_id=chat_id,
                member_limit=2,
                name="Escrow Invite"
            )

            return chat_id, invite.invite_link
    except Exception as e:
        print(f"Pyrogram group creation failed: {e}")
        return None, None


async def escrow_type_selected(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle P2P or Product Deal button press - create group and show link."""
    query = update.callback_query
    await query.answer()

    user = query.from_user
    # Get full name (first + last joined without space, matching screenshot format)
    first = user.first_name or ""
    last = user.last_name or ""
    full_name = f"{first}{last}".strip() or user.username or "User"

    # Show loading message
    await query.edit_message_text(
        "⏳ Creating a safe trading place for you, please wait..."
    )

    # Small delay to simulate processing
    await asyncio.sleep(2)

    # Try to create group with Pyrogram
    chat_id, invite_link = await create_group_pyrogram(user.id)

    if invite_link:
        # Success - show the group created message with real link
        await query.edit_message_text(
            f"Escrow Group Created\n\n"
            f"Creator: ⏤‌‌‌‌{full_name}\n\n"
            f"Join this escrow group and share the link with the buyer and seller.\n\n"
            f"{invite_link}\n\n"
            f"⚠️ Note: This link is for 2 members only—third parties are not allowed to join."
        )
    else:
        # Fallback: If Pyrogram not configured or failed,
        # Ask user to create group and add bot
        await query.edit_message_text(
            f"Escrow Group Created\n\n"
            f"Creator: ⏤‌‌‌‌{full_name}\n\n"
            f"Join this escrow group and share the link with the buyer and seller.\n\n"
            f"⚠️ To get your group link:\n"
            f"1. Create a private group on Telegram\n"
            f"2. Add this bot as admin (with all permissions)\n"
            f"3. Send /link in the group — bot will generate the invite\n\n"
            f"⚠️ Note: This link is for 2 members only—third parties are not allowed to join."
        )


async def link_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """
    /link command in group - bot generates invite link for the group.
    Used when user creates group manually and adds the bot.
    """
    chat = update.effective_chat
    user = update.effective_user

    # Only works in groups
    if chat.type not in ("group", "supergroup"):
        await update.message.reply_text("⚠️ Use this command inside a group.")
        return

    # Get full name
    first = user.first_name or ""
    last = user.last_name or ""
    full_name = f"{first}{last}".strip() or user.username or "User"

    try:
        # Create invite link with member limit of 2
        invite = await chat.create_invite_link(
            member_limit=2,
            name="Escrow Invite"
        )
        link = invite.invite_link

        await update.message.reply_text(
            f"Escrow Group Created\n\n"
            f"Creator: ⏤‌‌‌‌{full_name}\n\n"
            f"Join this escrow group and share the link with the buyer and seller.\n\n"
            f"{link}\n\n"
            f"⚠️ Note: This link is for 2 members only—third parties are not allowed to join."
        )
    except Exception as e:
        await update.message.reply_text(
            "❌ Failed to create invite link.\n"
            "Make sure the bot is an admin with 'Invite Users' permission."
        )


def main():
    if not BOT_TOKEN:
        print("ERROR: Set BOT_TOKEN in .env file")
        return

    app = Application.builder().token(BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("escrow", escrow))
    app.add_handler(CommandHandler("link", link_command))
    app.add_handler(CallbackQueryHandler(start_button, pattern="^start_menu$"))
    app.add_handler(CallbackQueryHandler(escrow_type_selected, pattern="^escrow_type_"))

    print("✅ Bot running! Press Ctrl+C to stop.")
    app.run_polling(drop_pending_updates=True)


if __name__ == "__main__":
    main()
