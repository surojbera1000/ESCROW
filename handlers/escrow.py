"""
Escrow creation handler.
Handles /escrow command, type selection, and group creation.
"""
from telegram import Update, ChatPermissions
from telegram.ext import ContextTypes

from models.escrow_deal import deal_store
from utils.keyboards import escrow_type_keyboard
from utils.formatting import format_escrow_type_message, format_welcome_group_message
from config import MAX_GROUP_MEMBERS


async def escrow_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle /escrow command - show type selection."""
    await update.message.reply_text(
        text="Please select your escrow type from below.",
        reply_markup=escrow_type_keyboard(),
    )


async def escrow_type_callback(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle escrow type selection (P2P or Product Deal)."""
    query = update.callback_query
    await query.answer()
    
    user = query.from_user
    callback_data = query.data  # escrow_type_p2p or escrow_type_product
    
    # Determine deal type
    deal_type = "p2p" if "p2p" in callback_data else "product"
    deal_type_display = "P2P" if deal_type == "p2p" else "Product Deal"
    
    # Create the deal
    deal = deal_store.create_deal(creator_id=user.id, deal_type=deal_type)
    
    # Store the current deal_id in user context for later use
    context.user_data["current_deal_id"] = deal.deal_id
    
    # Try to create a supergroup
    try:
        # Create a new supergroup for the escrow
        group_title = f"Escrow-{deal.deal_id} ({deal_type_display})"
        
        # Note: Bot API createNewSuperGroup is not directly available.
        # We use the workaround of creating a group via the bot.
        # The bot needs to be able to create groups (requires specific permissions).
        
        # Attempt to create chat
        chat = await context.bot.create_new_sticker_set  # This won't work - use alternative approach
        
    except Exception:
        pass
    
    # Since Telegram Bot API doesn't support direct group creation,
    # we provide the deal info and instruct the user to create a group and add the bot.
    # Alternative: If bot has channel/group admin rights, create invite link.
    
    await query.edit_message_text(
        text=(
            f"✅ <b>ESCROW CREATED</b>\n"
            f"━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
            f"🔑 Deal ID: <code>{deal.deal_id}</code>\n"
            f"📝 Type: <b>{deal_type_display}</b>\n\n"
            f"━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
            f"📋 <b>NEXT STEPS:</b>\n\n"
            f"1️⃣ Create a private group for this deal\n"
            f"2️⃣ Add this bot to the group as <b>Admin</b>\n"
            f"3️⃣ Send /link {deal.deal_id} in the group to connect it\n\n"
            f"⚠️ <b>This group is for 2 members only.</b>\n\n"
            f"Once linked, the bot will pin the welcome message "
            f"and guide you through the process."
        ),
        parse_mode="HTML",
    )


async def link_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """
    Handle /link [deal_id] command - link a group chat to an existing deal.
    This is used after the user creates a group and adds the bot.
    """
    chat = update.effective_chat
    user = update.effective_user
    
    # Only works in groups
    if chat.type not in ("group", "supergroup"):
        await update.message.reply_text(
            "⚠️ This command only works in group chats.\n"
            "Create a group, add me as admin, then use /link [deal_id]."
        )
        return
    
    # Parse deal_id from command
    if not context.args or len(context.args) < 1:
        await update.message.reply_text(
            "⚠️ Usage: /link <deal_id>\n"
            "Example: /link A7F3B2C1"
        )
        return
    
    deal_id = context.args[0].upper()
    deal = deal_store.get_deal(deal_id)
    
    if not deal:
        await update.message.reply_text(
            f"❌ Deal <code>{deal_id}</code> not found.\n"
            "Please check the Deal ID and try again.",
            parse_mode="HTML",
        )
        return
    
    # Verify the user is the deal creator
    if deal.creator_id != user.id:
        await update.message.reply_text(
            "❌ Only the deal creator can link a group."
        )
        return
    
    # Check if deal is already linked
    if deal.chat_id:
        await update.message.reply_text(
            f"⚠️ This deal is already linked to a group."
        )
        return
    
    # Link the chat to the deal
    deal_store.link_chat(deal_id, chat.id)
    
    # Try to create invite link with member limit
    try:
        invite = await chat.create_invite_link(
            member_limit=MAX_GROUP_MEMBERS,
            name=f"Escrow {deal_id}"
        )
        deal.invite_link = invite.invite_link
        deal_store.update_deal(deal)
        
        invite_text = f"\n🔗 Invite Link: {invite.invite_link}\n⚠️ <b>This link is for {MAX_GROUP_MEMBERS} members only.</b>"
    except Exception:
        invite_text = ""
    
    # Send and pin welcome message
    welcome_msg = await update.message.reply_text(
        text=format_welcome_group_message(),
        parse_mode="HTML",
    )
    
    # Try to pin the message
    try:
        await welcome_msg.pin(disable_notification=True)
    except Exception:
        pass  # Bot might not have pin permissions
    
    # Send confirmation
    await update.message.reply_text(
        text=(
            f"✅ <b>GROUP LINKED SUCCESSFULLY</b>\n"
            f"━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
            f"🔑 Deal ID: <code>{deal.deal_id}</code>\n"
            f"📝 Type: <b>{deal.deal_type.upper()}</b>\n"
            f"{invite_text}\n\n"
            f"Now use /dd to fill deal details."
        ),
        parse_mode="HTML",
    )


async def on_bot_added_to_group(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle when bot is added to a new group."""
    chat = update.effective_chat
    
    # Check if there's an unlinked deal from the user who added the bot
    if update.message and update.message.from_user:
        user_id = update.message.from_user.id
        user_deals = deal_store.get_user_deals(user_id)
        
        # Find the most recent unlinked deal
        unlinked_deal = None
        for deal in reversed(user_deals):
            if deal.chat_id is None:
                unlinked_deal = deal
                break
        
        if unlinked_deal:
            # Auto-link the deal
            deal_store.link_chat(unlinked_deal.deal_id, chat.id)
            
            # Pin welcome message
            welcome_msg = await chat.send_message(
                text=format_welcome_group_message(),
                parse_mode="HTML",
            )
            
            try:
                await welcome_msg.pin(disable_notification=True)
            except Exception:
                pass
            
            # Create invite link
            try:
                invite = await chat.create_invite_link(
                    member_limit=MAX_GROUP_MEMBERS,
                    name=f"Escrow {unlinked_deal.deal_id}"
                )
                unlinked_deal.invite_link = invite.invite_link
                deal_store.update_deal(unlinked_deal)
                
                await chat.send_message(
                    text=(
                        f"🔗 <b>Invite Link:</b> {invite.invite_link}\n"
                        f"⚠️ <b>This link is for {MAX_GROUP_MEMBERS} members only.</b>"
                    ),
                    parse_mode="HTML",
                )
            except Exception:
                pass
            
            await chat.send_message(
                text=(
                    f"✅ Auto-linked to Deal: <code>{unlinked_deal.deal_id}</code>\n"
                    f"Use /dd to start filling deal details."
                ),
                parse_mode="HTML",
            )
        else:
            await chat.send_message(
                text=(
                    "🔐 <b>P2P CRYPTO ESCROW BOT</b>\n\n"
                    "Use /link <deal_id> to connect this group to an escrow deal.\n"
                    "Or use /escrow in my DM first to create a new deal."
                ),
                parse_mode="HTML",
            )
