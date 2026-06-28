"""
Role declaration handlers (/seller and /buyer commands).
"""
from telegram import Update
from telegram.ext import ContextTypes

from models.escrow_deal import deal_store
from config import DealStatus
from utils.formatting import format_seller_declaration, format_buyer_declaration


async def seller_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """
    Handle /seller [WALLET_ADDRESS] command.
    Registers the user as the seller with their wallet address.
    """
    chat_id = update.effective_chat.id
    user = update.effective_user
    
    # Get the deal for this chat
    deal = deal_store.get_deal_by_chat(chat_id)
    
    if not deal:
        # Try user context
        deal_id = context.user_data.get("current_deal_id")
        if deal_id:
            deal = deal_store.get_deal(deal_id)
    
    if not deal:
        await update.message.reply_text(
            "❌ No escrow deal found for this chat.\n"
            "Use /escrow to create a deal first."
        )
        return
    
    # Check for wallet address argument
    if not context.args or len(context.args) < 1:
        await update.message.reply_text(
            "⚠️ Usage: /seller <WALLET_ADDRESS>\n\n"
            "Example: /seller 0x1234...abcd\n"
            "Please provide your wallet address."
        )
        return
    
    wallet_address = context.args[0]
    
    # Check if this role is already taken by someone else
    if deal.seller_id and deal.seller_id != user.id:
        await update.message.reply_text(
            f"⚠️ Seller role is already taken by @{deal.seller_username}.\n"
            "Only one seller per deal is allowed."
        )
        return
    
    # Check if user is already the buyer
    if deal.buyer_id == user.id:
        await update.message.reply_text(
            "⚠️ You are already registered as the <b>BUYER</b>.\n"
            "You cannot be both buyer and seller.",
            parse_mode="HTML",
        )
        return
    
    # Register as seller
    username = user.username or user.first_name or "Unknown"
    deal.seller_id = user.id
    deal.seller_username = username
    deal.seller_wallet = wallet_address
    
    # Update status if both roles are now set
    if deal.has_both_roles():
        deal.update_status(DealStatus.ROLES_SET)
    
    deal_store.update_deal(deal)
    
    await update.message.reply_text(
        text=format_seller_declaration(username, user.id, wallet_address),
        parse_mode="HTML",
    )
    
    # If both roles set, prompt for next step
    if deal.has_both_roles():
        await update.message.reply_text(
            "✅ Both roles are set!\n"
            "Next: Use /token to select the cryptocurrency and network."
        )


async def buyer_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """
    Handle /buyer [WALLET_ADDRESS] command.
    Registers the user as the buyer with their wallet address.
    """
    chat_id = update.effective_chat.id
    user = update.effective_user
    
    # Get the deal for this chat
    deal = deal_store.get_deal_by_chat(chat_id)
    
    if not deal:
        # Try user context
        deal_id = context.user_data.get("current_deal_id")
        if deal_id:
            deal = deal_store.get_deal(deal_id)
    
    if not deal:
        await update.message.reply_text(
            "❌ No escrow deal found for this chat.\n"
            "Use /escrow to create a deal first."
        )
        return
    
    # Check for wallet address argument
    if not context.args or len(context.args) < 1:
        await update.message.reply_text(
            "⚠️ Usage: /buyer <WALLET_ADDRESS>\n\n"
            "Example: /buyer TXyz...abc\n"
            "Please provide your wallet address."
        )
        return
    
    wallet_address = context.args[0]
    
    # Check if this role is already taken by someone else
    if deal.buyer_id and deal.buyer_id != user.id:
        await update.message.reply_text(
            f"⚠️ Buyer role is already taken by @{deal.buyer_username}.\n"
            "Only one buyer per deal is allowed."
        )
        return
    
    # Check if user is already the seller
    if deal.seller_id == user.id:
        await update.message.reply_text(
            "⚠️ You are already registered as the <b>SELLER</b>.\n"
            "You cannot be both buyer and seller.",
            parse_mode="HTML",
        )
        return
    
    # Register as buyer
    username = user.username or user.first_name or "Unknown"
    deal.buyer_id = user.id
    deal.buyer_username = username
    deal.buyer_wallet = wallet_address
    
    # Update status if both roles are now set
    if deal.has_both_roles():
        deal.update_status(DealStatus.ROLES_SET)
    
    deal_store.update_deal(deal)
    
    await update.message.reply_text(
        text=format_buyer_declaration(username, user.id, wallet_address),
        parse_mode="HTML",
    )
    
    # If both roles set, prompt for next step
    if deal.has_both_roles():
        await update.message.reply_text(
            "✅ Both roles are set!\n"
            "Next: Use /token to select the cryptocurrency and network."
        )
