"""
Deal details handler (/dd command).
Uses ConversationHandler for multi-step input collection.
"""
from telegram import Update
from telegram.ext import (
    ContextTypes,
    ConversationHandler,
    CommandHandler,
    MessageHandler,
    filters,
)

from models.escrow_deal import deal_store
from config import DealStatus
from utils.formatting import (
    format_deal_details_prompt,
    format_deal_details_rate,
    format_deal_details_conditions,
    format_deal_details_summary,
)

# Conversation states
QUANTITY, RATE, CONDITIONS = range(3)


async def dd_start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Start the deal details conversation. /dd command."""
    chat_id = update.effective_chat.id
    
    # Check if this chat is linked to a deal
    deal = deal_store.get_deal_by_chat(chat_id)
    
    if not deal:
        # Check if user has a current deal in their context (for DM usage)
        deal_id = context.user_data.get("current_deal_id")
        if deal_id:
            deal = deal_store.get_deal(deal_id)
    
    if not deal:
        await update.message.reply_text(
            "❌ No escrow deal found for this chat.\n\n"
            "Use /escrow to create a new deal first, then /link it to a group.",
            parse_mode="HTML",
        )
        return ConversationHandler.END
    
    # Store deal_id in conversation context
    context.user_data["dd_deal_id"] = deal.deal_id
    
    await update.message.reply_text(
        text=format_deal_details_prompt(),
        parse_mode="HTML",
    )
    return QUANTITY


async def dd_quantity(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Receive quantity and ask for rate."""
    quantity = update.message.text.strip()
    context.user_data["dd_quantity"] = quantity
    
    await update.message.reply_text(
        text=format_deal_details_rate(),
        parse_mode="HTML",
    )
    return RATE


async def dd_rate(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Receive rate and ask for conditions."""
    rate = update.message.text.strip()
    context.user_data["dd_rate"] = rate
    
    await update.message.reply_text(
        text=format_deal_details_conditions(),
        parse_mode="HTML",
    )
    return CONDITIONS


async def dd_conditions(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Receive conditions and save deal details."""
    conditions = update.message.text.strip()
    
    # Get the deal
    deal_id = context.user_data.get("dd_deal_id")
    deal = deal_store.get_deal(deal_id)
    
    if not deal:
        await update.message.reply_text("❌ Error: Deal not found. Please start over with /escrow.")
        return ConversationHandler.END
    
    # Save deal details
    deal.quantity = context.user_data["dd_quantity"]
    deal.rate = context.user_data["dd_rate"]
    deal.conditions = conditions
    deal.update_status(DealStatus.DETAILS_FILLED)
    deal_store.update_deal(deal)
    
    # Clean up context
    for key in ["dd_quantity", "dd_rate", "dd_deal_id"]:
        context.user_data.pop(key, None)
    
    await update.message.reply_text(
        text=format_deal_details_summary(deal),
        parse_mode="HTML",
    )
    return ConversationHandler.END


async def dd_cancel(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Cancel the deal details conversation."""
    # Clean up context
    for key in ["dd_quantity", "dd_rate", "dd_deal_id"]:
        context.user_data.pop(key, None)
    
    await update.message.reply_text(
        "❌ Deal details entry cancelled.\n"
        "Use /dd to start again."
    )
    return ConversationHandler.END


# Build the conversation handler
dd_conversation_handler = ConversationHandler(
    entry_points=[CommandHandler("dd", dd_start)],
    states={
        QUANTITY: [MessageHandler(filters.TEXT & ~filters.COMMAND, dd_quantity)],
        RATE: [MessageHandler(filters.TEXT & ~filters.COMMAND, dd_rate)],
        CONDITIONS: [MessageHandler(filters.TEXT & ~filters.COMMAND, dd_conditions)],
    },
    fallbacks=[CommandHandler("cancel", dd_cancel)],
    per_chat=True,
    per_user=False,
)
