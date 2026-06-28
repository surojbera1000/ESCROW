"""
Release and Refund handlers.
Handles /release and /refund commands with confirmation flow.
"""
from telegram import Update
from telegram.ext import ContextTypes

from models.escrow_deal import deal_store
from config import DealStatus
from utils.keyboards import confirm_release_keyboard, confirm_refund_keyboard
from utils.formatting import (
    format_release_warning,
    format_refund_warning,
    format_release_success,
    format_refund_success,
)


async def release_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle /release command - release funds to buyer."""
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
            "❌ No escrow deal found for this chat."
        )
        return
    
    # Check deal status
    if deal.status != DealStatus.DEPOSITED:
        if deal.status == DealStatus.RELEASED:
            await update.message.reply_text("✅ Funds have already been released.")
        elif deal.status == DealStatus.REFUNDED:
            await update.message.reply_text("↩️ Funds have already been refunded.")
        else:
            await update.message.reply_text(
                "⚠️ Cannot release funds. Deposit must be made first.\n"
                f"Current status: {deal.status.upper()}"
            )
        return
    
    # Only seller can release (or admin)
    if user.id != deal.seller_id and user.id not in (deal.creator_id,):
        await update.message.reply_text(
            "⚠️ Only the <b>SELLER</b> can release funds to the buyer.",
            parse_mode="HTML",
        )
        return
    
    # Show warning and confirmation
    await update.message.reply_text(
        text=format_release_warning(),
        parse_mode="HTML",
        reply_markup=confirm_release_keyboard(),
    )


async def refund_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle /refund command - refund funds to seller."""
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
            "❌ No escrow deal found for this chat."
        )
        return
    
    # Check deal status
    if deal.status != DealStatus.DEPOSITED:
        if deal.status == DealStatus.RELEASED:
            await update.message.reply_text("✅ Funds have already been released.")
        elif deal.status == DealStatus.REFUNDED:
            await update.message.reply_text("↩️ Funds have already been refunded.")
        else:
            await update.message.reply_text(
                "⚠️ Cannot refund funds. Deposit must be made first.\n"
                f"Current status: {deal.status.upper()}"
            )
        return
    
    # Only buyer can refund (or admin)
    if user.id != deal.buyer_id and user.id not in (deal.creator_id,):
        await update.message.reply_text(
            "⚠️ Only the <b>BUYER</b> can initiate a refund to the seller.",
            parse_mode="HTML",
        )
        return
    
    # Show warning and confirmation
    await update.message.reply_text(
        text=format_refund_warning(),
        parse_mode="HTML",
        reply_markup=confirm_refund_keyboard(),
    )


async def confirm_action_callback(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle confirmation callbacks for release and refund."""
    query = update.callback_query
    await query.answer()
    
    chat_id = update.effective_chat.id
    callback_data = query.data
    
    # Get the deal
    deal = deal_store.get_deal_by_chat(chat_id)
    
    if not deal:
        deal_id = context.user_data.get("current_deal_id")
        if deal_id:
            deal = deal_store.get_deal(deal_id)
    
    if not deal:
        await query.edit_message_text("❌ Error: Deal not found.")
        return
    
    # Handle release confirmation
    if callback_data == "confirm_release_yes":
        if deal.status != DealStatus.DEPOSITED:
            await query.edit_message_text("⚠️ Deal is no longer in deposit state.")
            return
        
        # Process release
        deal.update_status(DealStatus.RELEASED)
        deal_store.update_deal(deal)
        
        # Cancel any countdown jobs
        if context.application.job_queue:
            jobs = context.application.job_queue.get_jobs_by_name(f"countdown_{deal.deal_id}")
            for job in jobs:
                job.schedule_removal()
            expire_jobs = context.application.job_queue.get_jobs_by_name(f"expire_{deal.deal_id}")
            for job in expire_jobs:
                job.schedule_removal()
        
        await query.edit_message_text(
            text=format_release_success(deal),
            parse_mode="HTML",
        )
    
    elif callback_data == "confirm_release_no":
        await query.edit_message_text(
            "❌ Release cancelled.\n"
            "Use /release when you're ready to release funds."
        )
    
    # Handle refund confirmation
    elif callback_data == "confirm_refund_yes":
        if deal.status != DealStatus.DEPOSITED:
            await query.edit_message_text("⚠️ Deal is no longer in deposit state.")
            return
        
        # Process refund
        deal.update_status(DealStatus.REFUNDED)
        deal_store.update_deal(deal)
        
        # Cancel any countdown jobs
        if context.application.job_queue:
            jobs = context.application.job_queue.get_jobs_by_name(f"countdown_{deal.deal_id}")
            for job in jobs:
                job.schedule_removal()
            expire_jobs = context.application.job_queue.get_jobs_by_name(f"expire_{deal.deal_id}")
            for job in expire_jobs:
                job.schedule_removal()
        
        await query.edit_message_text(
            text=format_refund_success(deal),
            parse_mode="HTML",
        )
    
    elif callback_data == "confirm_refund_no":
        await query.edit_message_text(
            "❌ Refund cancelled.\n"
            "Use /refund when you're ready to refund funds."
        )
