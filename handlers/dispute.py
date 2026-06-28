"""
Dispute and utility command handlers.
Handles /dispute, /balance, /save, /verify commands.
"""
from telegram import Update
from telegram.ext import ContextTypes

from models.escrow_deal import deal_store
from config import DealStatus, ADMIN_IDS
from utils.keyboards import dispute_keyboard
from utils.formatting import format_dispute_message, format_balance_message


async def dispute_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle /dispute command - open a dispute for the current deal."""
    chat_id = update.effective_chat.id
    user = update.effective_user
    
    # Get the deal
    deal = deal_store.get_deal_by_chat(chat_id)
    
    if not deal:
        deal_id = context.user_data.get("current_deal_id")
        if deal_id:
            deal = deal_store.get_deal(deal_id)
    
    if not deal:
        await update.message.reply_text(
            "❌ No escrow deal found for this chat.\n"
            "Use /escrow to create a deal first."
        )
        return
    
    # Check if user is a participant
    if not deal.is_participant(user.id):
        await update.message.reply_text(
            "⚠️ Only deal participants can open a dispute."
        )
        return
    
    # Check if deal is in a state where disputes make sense
    if deal.status in (DealStatus.CREATED, DealStatus.RELEASED, DealStatus.REFUNDED):
        await update.message.reply_text(
            f"⚠️ Cannot open dispute in current state: {deal.status.upper()}\n"
            "Disputes can only be opened for active deals."
        )
        return
    
    if deal.status == DealStatus.DISPUTED:
        await update.message.reply_text(
            "⚖️ A dispute is already open for this deal.\n"
            "An admin will review it shortly."
        )
        return
    
    # Open the dispute
    deal.update_status(DealStatus.DISPUTED)
    deal_store.update_deal(deal)
    
    # Notify in the chat
    await update.message.reply_text(
        text=format_dispute_message(deal),
        parse_mode="HTML",
        reply_markup=dispute_keyboard(),
    )
    
    # Notify admins
    for admin_id in ADMIN_IDS:
        try:
            await context.bot.send_message(
                chat_id=admin_id,
                text=(
                    "🚨 <b>NEW DISPUTE</b>\n"
                    "━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
                    f"🔑 Deal ID: <code>{deal.deal_id}</code>\n"
                    f"👤 Opened by: @{user.username or user.first_name} (ID: {user.id})\n"
                    f"👤 Seller: @{deal.seller_username}\n"
                    f"👤 Buyer: @{deal.buyer_username}\n"
                    f"💰 Amount: {deal.quantity} {deal.token}\n"
                    f"🌐 Network: {deal.network}\n\n"
                    "Please review and resolve this dispute."
                ),
                parse_mode="HTML",
            )
        except Exception:
            pass  # Admin might have blocked the bot


async def dispute_callback(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle dispute button callbacks."""
    query = update.callback_query
    await query.answer()
    
    if query.data == "dispute_evidence":
        await query.edit_message_text(
            text=(
                "📝 <b>SUBMIT EVIDENCE</b>\n"
                "━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
                "Please send your evidence in this chat:\n\n"
                "• Screenshots of conversations\n"
                "• Transaction hashes/proofs\n"
                "• Any relevant documents\n\n"
                "An admin will review all evidence and make a decision."
            ),
            parse_mode="HTML",
        )
    elif query.data == "dispute_cancel":
        chat_id = update.effective_chat.id
        deal = deal_store.get_deal_by_chat(chat_id)
        
        if deal and deal.status == DealStatus.DISPUTED:
            deal.update_status(DealStatus.DEPOSITED)
            deal_store.update_deal(deal)
        
        await query.edit_message_text(
            "✅ Dispute cancelled.\n"
            "The deal continues as normal."
        )


async def balance_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle /balance command - show current escrow balance."""
    chat_id = update.effective_chat.id
    
    # Get the deal
    deal = deal_store.get_deal_by_chat(chat_id)
    
    if not deal:
        deal_id = context.user_data.get("current_deal_id")
        if deal_id:
            deal = deal_store.get_deal(deal_id)
    
    if not deal:
        await update.message.reply_text(
            "❌ No escrow deal found for this chat.\n"
            "Use /escrow to create a deal first."
        )
        return
    
    await update.message.reply_text(
        text=format_balance_message(deal),
        parse_mode="HTML",
    )


async def save_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle /save command - save deal information to persistent storage."""
    chat_id = update.effective_chat.id
    
    # Get the deal
    deal = deal_store.get_deal_by_chat(chat_id)
    
    if not deal:
        deal_id = context.user_data.get("current_deal_id")
        if deal_id:
            deal = deal_store.get_deal(deal_id)
    
    if not deal:
        await update.message.reply_text(
            "❌ No escrow deal found for this chat."
        )
        return
    
    # Force save to disk
    deal_store.save()
    
    await update.message.reply_text(
        text=(
            "💾 <b>DEAL SAVED</b>\n"
            "━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
            f"🔑 Deal ID: <code>{deal.deal_id}</code>\n"
            f"📊 Status: {deal.status.upper()}\n"
            f"📝 Type: {deal.deal_type.upper()}\n\n"
            "✅ Deal information has been saved successfully."
        ),
        parse_mode="HTML",
    )


async def verify_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle /verify command - verify a transaction."""
    chat_id = update.effective_chat.id
    
    # Get the deal
    deal = deal_store.get_deal_by_chat(chat_id)
    
    if not deal:
        deal_id = context.user_data.get("current_deal_id")
        if deal_id:
            deal = deal_store.get_deal(deal_id)
    
    if not deal:
        await update.message.reply_text(
            "❌ No escrow deal found for this chat."
        )
        return
    
    if not deal.transaction_id:
        await update.message.reply_text(
            "⚠️ No transaction to verify.\n"
            "Use /deposit first to generate a transaction."
        )
        return
    
    # In production, this would query blockchain APIs
    # For simulation, show the transaction details
    status_text = "CONFIRMED ✅" if deal.status in (DealStatus.DEPOSITED, DealStatus.RELEASED) else deal.status.upper()
    
    await update.message.reply_text(
        text=(
            "🔍 <b>TRANSACTION VERIFICATION</b>\n"
            "━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
            f"🔑 Transaction ID: <code>{deal.transaction_id}</code>\n"
            f"📊 Status: <b>{status_text}</b>\n"
            f"💎 Token: {deal.token}\n"
            f"🌐 Network: {deal.network}\n"
            f"📬 Escrow Address: <code>{deal.escrow_address or 'N/A'}</code>\n"
            f"💰 Amount: {deal.quantity} {deal.token}\n\n"
            "━━━━━━━━━━━━━━━━━━━━━━━━\n"
            "⚠️ <i>In production, this verifies on-chain.</i>"
        ),
        parse_mode="HTML",
    )
