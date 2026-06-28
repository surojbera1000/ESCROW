"""
Deposit handler.
Handles /deposit command, address generation, countdown timer, and payment check.
"""
import time

from telegram import Update
from telegram.ext import ContextTypes

from models.escrow_deal import deal_store
from config import DealStatus, DEPOSIT_TIMEOUT_MINUTES
from utils.keyboards import check_payment_keyboard
from utils.formatting import format_deposit_message
from utils.wallet import generate_escrow_address, generate_transaction_id


async def deposit_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle /deposit command - generate deposit address and start countdown."""
    chat_id = update.effective_chat.id
    user = update.effective_user
    
    # Get the deal for this chat
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
    
    # Check if deal is in accepted state
    if deal.status != DealStatus.ACCEPTED:
        status_messages = {
            DealStatus.CREATED: "⚠️ Please fill deal details first with /dd.",
            DealStatus.DETAILS_FILLED: "⚠️ Please declare /seller and /buyer roles first.",
            DealStatus.ROLES_SET: "⚠️ Please select token with /token first.",
            DealStatus.TOKEN_SELECTED: "⚠️ The deal must be accepted by both parties first.",
            DealStatus.DEPOSITED: "⚠️ Deposit already made. Use /balance to check status.",
            DealStatus.RELEASED: "✅ This deal has already been completed (released).",
            DealStatus.REFUNDED: "✅ This deal has already been refunded.",
            DealStatus.DISPUTED: "⚖️ This deal is under dispute.",
        }
        msg = status_messages.get(deal.status, f"⚠️ Cannot deposit in current state: {deal.status}")
        await update.message.reply_text(msg)
        return
    
    # Generate escrow address and transaction ID
    deal.escrow_address = generate_escrow_address(deal.network, deal.deal_id)
    deal.transaction_id = generate_transaction_id()
    deal.deposit_time = time.time()
    deal.update_status(DealStatus.DEPOSITED)
    deal_store.update_deal(deal)
    
    # Calculate countdown
    countdown_min = DEPOSIT_TIMEOUT_MINUTES
    
    # Send deposit message
    deposit_msg = await update.message.reply_text(
        text=format_deposit_message(deal, countdown_min),
        parse_mode="HTML",
        reply_markup=check_payment_keyboard(),
    )
    
    # Store message ID for countdown updates
    context.chat_data["deposit_message_id"] = deposit_msg.message_id
    context.chat_data["deposit_deal_id"] = deal.deal_id
    
    # Schedule countdown updates using JobQueue
    job_queue = context.application.job_queue
    if job_queue:
        # Schedule periodic countdown updates (every 60 seconds)
        job_queue.run_repeating(
            callback=_update_countdown,
            interval=60,
            first=60,
            chat_id=chat_id,
            name=f"countdown_{deal.deal_id}",
            data={
                "deal_id": deal.deal_id,
                "message_id": deposit_msg.message_id,
                "start_time": time.time(),
            },
        )
        
        # Schedule address expiration
        job_queue.run_once(
            callback=_expire_address,
            when=DEPOSIT_TIMEOUT_MINUTES * 60,
            chat_id=chat_id,
            name=f"expire_{deal.deal_id}",
            data={"deal_id": deal.deal_id},
        )


async def _update_countdown(context: ContextTypes.DEFAULT_TYPE) -> None:
    """Job callback to update the countdown timer on the deposit message."""
    job = context.job
    data = job.data
    deal_id = data["deal_id"]
    message_id = data["message_id"]
    start_time = data["start_time"]
    
    deal = deal_store.get_deal(deal_id)
    if not deal or deal.status != DealStatus.DEPOSITED:
        job.schedule_removal()
        return
    
    # Calculate remaining time
    elapsed = time.time() - start_time
    remaining_min = DEPOSIT_TIMEOUT_MINUTES - (elapsed / 60)
    
    if remaining_min <= 0:
        job.schedule_removal()
        return
    
    # Update the message with new countdown
    try:
        await context.bot.edit_message_text(
            chat_id=job.chat_id,
            message_id=message_id,
            text=format_deposit_message(deal, remaining_min),
            parse_mode="HTML",
            reply_markup=check_payment_keyboard(),
        )
    except Exception:
        pass  # Message might have been deleted or unchanged


async def _expire_address(context: ContextTypes.DEFAULT_TYPE) -> None:
    """Job callback when deposit address expires."""
    job = context.job
    data = job.data
    deal_id = data["deal_id"]
    
    deal = deal_store.get_deal(deal_id)
    if not deal:
        return
    
    # Only expire if still in deposited state (no payment confirmed)
    if deal.status == DealStatus.DEPOSITED:
        deal.update_status(DealStatus.EXPIRED)
        deal.escrow_address = None
        deal_store.update_deal(deal)
        
        await context.bot.send_message(
            chat_id=job.chat_id,
            text=(
                "⏰ <b>ADDRESS EXPIRED</b>\n"
                "━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
                f"🔑 Deal ID: <code>{deal.deal_id}</code>\n\n"
                "The deposit address has expired.\n"
                "Use /deposit to generate a new address."
            ),
            parse_mode="HTML",
        )
    
    # Remove the countdown job
    jobs = context.job_queue.get_jobs_by_name(f"countdown_{deal_id}")
    for j in jobs:
        j.schedule_removal()


async def check_payment_callback(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle Check Payment button callback."""
    query = update.callback_query
    await query.answer()
    
    chat_id = update.effective_chat.id
    
    # Get the deal
    deal = deal_store.get_deal_by_chat(chat_id)
    
    if not deal:
        deal_id = context.chat_data.get("deposit_deal_id")
        if deal_id:
            deal = deal_store.get_deal(deal_id)
    
    if not deal:
        await query.answer("❌ Deal not found.", show_alert=True)
        return
    
    if deal.status == DealStatus.EXPIRED:
        await query.answer("⏰ Address expired. Use /deposit for a new one.", show_alert=True)
        return
    
    # In a real implementation, this would check the blockchain for the transaction
    # For simulation, we'll show a "checking" message and confirm
    
    # Simulate payment verification
    # In production: query blockchain API for incoming transactions to escrow_address
    
    await query.answer("🔍 Checking payment...", show_alert=False)
    
    # For demonstration, show payment as pending
    # In real implementation, this would verify on-chain
    remaining_min = 0.0
    if deal.deposit_time:
        elapsed = time.time() - deal.deposit_time
        remaining_min = max(0, DEPOSIT_TIMEOUT_MINUTES - (elapsed / 60))
    
    await query.edit_message_text(
        text=(
            f"{format_deposit_message(deal, remaining_min)}\n\n"
            "━━━━━━━━━━━━━━━━━━━━━━━━\n"
            "🔍 <b>Payment Status: PENDING</b>\n\n"
            "⏳ Waiting for blockchain confirmation...\n"
            "Please ensure you've sent the exact amount.\n\n"
            "💡 Click <b>Check Payment</b> again after sending."
        ),
        parse_mode="HTML",
        reply_markup=check_payment_keyboard(),
    )
