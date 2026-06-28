"""
Token & Network selection handler.
Handles /token command, token selection, network selection, and declaration summary.
"""
from telegram import Update
from telegram.ext import ContextTypes

from models.escrow_deal import deal_store
from config import DealStatus
from utils.keyboards import token_keyboard, network_keyboard, accept_reject_keyboard
from utils.formatting import (
    format_token_selection,
    format_network_selection,
    format_declaration_summary,
)


async def token_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle /token command - show token selection buttons."""
    chat_id = update.effective_chat.id
    
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
    
    # Check if both roles are set
    if not deal.has_both_roles():
        await update.message.reply_text(
            "⚠️ Both /seller and /buyer must be declared before selecting a token.\n"
            "Please set both roles first."
        )
        return
    
    await update.message.reply_text(
        text=format_token_selection(),
        parse_mode="HTML",
        reply_markup=token_keyboard(),
    )


async def token_callback(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle token selection callback (LTC, BTC, USDT)."""
    query = update.callback_query
    await query.answer()
    
    callback_data = query.data  # token_LTC, token_BTC, token_USDT, token_back
    
    # Handle back button (go back to token selection)
    if callback_data == "token_back":
        await query.edit_message_text(
            text=format_token_selection(),
            parse_mode="HTML",
            reply_markup=token_keyboard(),
        )
        return
    
    # Extract token name
    token = callback_data.replace("token_", "")  # LTC, BTC, USDT
    
    # Store selection in user context
    context.user_data["selected_token"] = token
    
    # Show network selection
    await query.edit_message_text(
        text=format_network_selection(token),
        parse_mode="HTML",
        reply_markup=network_keyboard(token),
    )


async def network_callback(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle network selection callback."""
    query = update.callback_query
    await query.answer()
    
    chat_id = update.effective_chat.id
    callback_data = query.data  # network_BSC(BEP20), network_TRON(TRC20), etc.
    
    # Extract network name
    network = callback_data.replace("network_", "")  # BSC(BEP20), TRON(TRC20), Bitcoin, Litecoin
    
    # Get the selected token from user context
    token = context.user_data.get("selected_token")
    
    if not token:
        await query.edit_message_text(
            "❌ Error: Token selection lost. Please use /token again."
        )
        return
    
    # Get the deal
    deal = deal_store.get_deal_by_chat(chat_id)
    
    if not deal:
        deal_id = context.user_data.get("current_deal_id")
        if deal_id:
            deal = deal_store.get_deal(deal_id)
    
    if not deal:
        await query.edit_message_text(
            "❌ Error: Deal not found. Please start over."
        )
        return
    
    # Save token and network to deal
    deal.token = token
    deal.network = network
    deal.update_status(DealStatus.TOKEN_SELECTED)
    deal_store.update_deal(deal)
    
    # Show declaration summary with Accept/Reject buttons
    await query.edit_message_text(
        text=format_declaration_summary(deal),
        parse_mode="HTML",
        reply_markup=accept_reject_keyboard(),
    )


async def deal_accept_callback(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle deal acceptance callback."""
    query = update.callback_query
    await query.answer("✅ Deal accepted!")
    
    chat_id = update.effective_chat.id
    user = query.from_user
    
    # Get the deal
    deal = deal_store.get_deal_by_chat(chat_id)
    
    if not deal:
        deal_id = context.user_data.get("current_deal_id")
        if deal_id:
            deal = deal_store.get_deal(deal_id)
    
    if not deal:
        await query.edit_message_text("❌ Error: Deal not found.")
        return
    
    # Update deal status to accepted
    deal.update_status(DealStatus.ACCEPTED)
    deal_store.update_deal(deal)
    
    # Update the message
    summary_text = format_declaration_summary(deal)
    accepted_text = (
        f"{summary_text}\n\n"
        "━━━━━━━━━━━━━━━━━━━━━━━━\n"
        f"✅ <b>ACCEPTED</b> by @{user.username or user.first_name}\n\n"
        "💰 Use /deposit to proceed with funding the escrow."
    )
    
    await query.edit_message_text(
        text=accepted_text,
        parse_mode="HTML",
    )


async def deal_reject_callback(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle deal rejection callback."""
    query = update.callback_query
    await query.answer("❌ Deal rejected!")
    
    chat_id = update.effective_chat.id
    user = query.from_user
    
    # Get the deal
    deal = deal_store.get_deal_by_chat(chat_id)
    
    if not deal:
        deal_id = context.user_data.get("current_deal_id")
        if deal_id:
            deal = deal_store.get_deal(deal_id)
    
    if not deal:
        await query.edit_message_text("❌ Error: Deal not found.")
        return
    
    # Reset token selection
    deal.token = None
    deal.network = None
    deal.update_status(DealStatus.ROLES_SET)
    deal_store.update_deal(deal)
    
    await query.edit_message_text(
        text=(
            "❌ <b>DEAL REJECTED</b>\n"
            "━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
            f"Rejected by @{user.username or user.first_name}\n\n"
            "The deal terms were not accepted.\n"
            "Use /token to select a different token/network,\n"
            "or update deal details with /dd."
        ),
        parse_mode="HTML",
    )
