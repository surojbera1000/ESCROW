"""
Message formatting helpers for the Escrow Bot.
"""
from models.escrow_deal import EscrowDeal


def format_start_message() -> str:
    """Format the start/welcome message."""
    return (
        "🔐 <b>P2P CRYPTO ESCROW BOT</b>\n"
        "━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
        "🛡️ Creates a safe space for your crypto transactions.\n\n"
        "📋 <b>Available Commands:</b>\n\n"
        "🔹 /escrow — Create new escrow deal\n"
        "🔹 /buyer — Register as buyer\n"
        "🔹 /seller — Register as seller\n"
        "🔹 /deposit — Deposit funds\n"
        "🔹 /balance — Check escrow balance\n"
        "🔹 /release — Release funds to buyer\n"
        "🔹 /refund — Refund funds to seller\n"
        "🔹 /dispute — Open a dispute\n"
        "🔹 /save — Save deal information\n"
        "🔹 /verify — Verify transaction\n\n"
        "━━━━━━━━━━━━━━━━━━━━━━━━\n"
        "⚡ Press <b>START</b> to begin!"
    )


def format_escrow_type_message() -> str:
    """Format escrow type selection message."""
    return (
        "📝 <b>CREATE NEW ESCROW</b>\n"
        "━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
        "Select the type of escrow deal:\n\n"
        "🤝 <b>P2P</b> — Person to Person crypto trade\n"
        "📦 <b>Product Deal</b> — Product/Service exchange\n"
    )


def format_welcome_group_message() -> str:
    """Format the welcome message pinned in escrow group."""
    return (
        "🔐 <b>ESCROW SERVICE</b>\n"
        "━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
        "Welcome to our escrow service.\n\n"
        "Please start with /dd command and fill the DealInfo Form.\n\n"
        "📋 <b>Steps:</b>\n"
        "1️⃣ /dd — Fill deal details\n"
        "2️⃣ /seller [wallet] — Declare seller\n"
        "3️⃣ /buyer [wallet] — Declare buyer\n"
        "4️⃣ /token — Select token & network\n"
        "5️⃣ /deposit — Deposit funds\n"
        "6️⃣ /release or /refund — Complete deal"
    )


def format_deal_details_prompt() -> str:
    """Format the deal details collection prompt."""
    return (
        "📝 <b>DEAL DETAILS FORM</b>\n"
        "━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
        "Please provide the following information:\n\n"
        "Enter the <b>Quantity</b> (amount of crypto):"
    )


def format_deal_details_rate() -> str:
    """Prompt for rate."""
    return "💰 Enter the <b>Rate</b> (price per unit):"


def format_deal_details_conditions() -> str:
    """Prompt for conditions."""
    return (
        "📜 Enter the <b>Conditions</b> (terms of the deal):\n\n"
        "⚠️ <i>Without it disputes wouldn't be resolved.</i>"
    )


def format_deal_details_summary(deal: EscrowDeal) -> str:
    """Format deal details summary after collection."""
    return (
        "✅ <b>DEAL DETAILS SAVED</b>\n"
        "━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
        f"📊 Quantity: <code>{deal.quantity}</code>\n"
        f"💰 Rate: <code>{deal.rate}</code>\n"
        f"📜 Conditions: <code>{deal.conditions}</code>\n\n"
        "⚠️ <i>Without it disputes wouldn't be resolved.</i>\n\n"
        "Next: Use /seller and /buyer to declare roles."
    )


def format_seller_declaration(username: str, user_id: int, wallet: str) -> str:
    """Format seller role declaration message."""
    return (
        f"⚡ SELLER @{username} | Userid: {user_id}\n"
        f"✅ SELLER WALLET <code>{wallet}</code>"
    )


def format_buyer_declaration(username: str, user_id: int, wallet: str) -> str:
    """Format buyer role declaration message."""
    return (
        f"⚡ BUYER @{username} | Userid: {user_id}\n"
        f"✅ BUYER WALLET <code>{wallet}</code>"
    )


def format_token_selection() -> str:
    """Format token selection message."""
    return (
        "💱 <b>SELECT TOKEN</b>\n"
        "━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
        "Choose the cryptocurrency for this deal:"
    )


def format_network_selection(token: str) -> str:
    """Format network selection message."""
    return (
        f"🌐 <b>SELECT NETWORK FOR {token}</b>\n"
        "━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
        "Choose the network:"
    )


def format_declaration_summary(deal: EscrowDeal) -> str:
    """Format the full deal declaration summary."""
    buyer_username = deal.buyer_username or "N/A"
    seller_username = deal.seller_username or "N/A"
    
    return (
        "📋 <b>DEAL DECLARATION</b>\n"
        "━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
        f"👤 Buyer: @{buyer_username}\n"
        f"🆔 Buyer ID: <code>{deal.buyer_id}</code>\n"
        f"💼 Buyer Wallet: <code>{deal.buyer_wallet}</code>\n\n"
        f"👤 Seller: @{seller_username}\n"
        f"🆔 Seller ID: <code>{deal.seller_id}</code>\n"
        f"💼 Seller Wallet: <code>{deal.seller_wallet}</code>\n\n"
        f"💰 Crypto: <b>{deal.token}</b>\n"
        f"🌐 Network: <b>{deal.network}</b>\n\n"
        f"📊 Quantity: <code>{deal.quantity}</code>\n"
        f"💵 Rate: <code>{deal.rate}</code>\n\n"
        "━━━━━━━━━━━━━━━━━━━━━━━━\n"
        "Do both parties accept this deal?"
    )


def format_deposit_message(deal: EscrowDeal, countdown_min: float) -> str:
    """Format the deposit information message."""
    return (
        "💳 <b>DEPOSIT INFORMATION</b>\n"
        "━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
        f"🔑 Transaction ID: <code>{deal.transaction_id}</code>\n"
        f"👤 Seller: @{deal.seller_username} (ID: {deal.seller_id})\n"
        f"👤 Buyer: @{deal.buyer_username} (ID: {deal.buyer_id})\n"
        f"📬 Escrow Address: <code>{deal.escrow_address}</code>\n"
        f"🌐 Network: <b>{deal.network}</b>\n\n"
        f"💰 Amount: <code>{deal.quantity} {deal.token}</code>\n\n"
        "━━━━━━━━━━━━━━━━━━━━━━━━\n"
        f"⏳ Address Reset In: <b>{countdown_min:.2f} Min</b>\n\n"
        "⚠️ Send the exact amount to the escrow address above.\n"
        "Click <b>Check Payment</b> after sending."
    )


def format_release_warning() -> str:
    """Format the release warning message."""
    return (
        "⚠️ <b>RELEASE FUNDS</b>\n"
        "━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
        "You are about to release funds to the <b>BUYER</b>.\n\n"
        "⚠️ <b>Remember, once commands are used payment will be "
        "released, there is no revert!</b>\n\n"
        "Are you sure you want to proceed?"
    )


def format_refund_warning() -> str:
    """Format the refund warning message."""
    return (
        "⚠️ <b>REFUND FUNDS</b>\n"
        "━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
        "You are about to refund funds to the <b>SELLER</b>.\n\n"
        "⚠️ <b>Remember, once commands are used payment will be "
        "released, there is no revert!</b>\n\n"
        "Are you sure you want to proceed?"
    )


def format_release_success(deal: EscrowDeal) -> str:
    """Format successful release message."""
    return (
        "✅ <b>FUNDS RELEASED</b>\n"
        "━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
        f"💸 {deal.quantity} {deal.token} has been released to:\n"
        f"👤 Buyer: @{deal.buyer_username}\n"
        f"💼 Wallet: <code>{deal.buyer_wallet}</code>\n"
        f"🌐 Network: {deal.network}\n\n"
        f"🔑 TXN ID: <code>{deal.transaction_id}</code>\n\n"
        "✅ Deal completed successfully!"
    )


def format_refund_success(deal: EscrowDeal) -> str:
    """Format successful refund message."""
    return (
        "✅ <b>FUNDS REFUNDED</b>\n"
        "━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
        f"💸 {deal.quantity} {deal.token} has been refunded to:\n"
        f"👤 Seller: @{deal.seller_username}\n"
        f"💼 Wallet: <code>{deal.seller_wallet}</code>\n"
        f"🌐 Network: {deal.network}\n\n"
        f"🔑 TXN ID: <code>{deal.transaction_id}</code>\n\n"
        "✅ Refund completed successfully!"
    )


def format_balance_message(deal: EscrowDeal) -> str:
    """Format balance check message."""
    status_emoji = {
        "created": "🆕",
        "details_filled": "📝",
        "roles_set": "👥",
        "token_selected": "💱",
        "accepted": "✅",
        "deposited": "💰",
        "released": "🏁",
        "refunded": "↩️",
        "disputed": "⚖️",
        "expired": "⏰",
    }
    emoji = status_emoji.get(deal.status, "❓")
    
    balance = deal.quantity if deal.status == "deposited" else "0"
    
    return (
        "💰 <b>ESCROW BALANCE</b>\n"
        "━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
        f"🔑 Deal ID: <code>{deal.deal_id}</code>\n"
        f"{emoji} Status: <b>{deal.status.upper()}</b>\n"
        f"💎 Token: {deal.token or 'Not set'}\n"
        f"🌐 Network: {deal.network or 'Not set'}\n"
        f"💰 Balance: <code>{balance} {deal.token or ''}</code>\n"
        f"📬 Escrow Address: <code>{deal.escrow_address or 'Not generated'}</code>"
    )


def format_dispute_message(deal: EscrowDeal) -> str:
    """Format dispute opened message."""
    return (
        "⚖️ <b>DISPUTE OPENED</b>\n"
        "━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
        f"🔑 Deal ID: <code>{deal.deal_id}</code>\n"
        f"👤 Seller: @{deal.seller_username}\n"
        f"👤 Buyer: @{deal.buyer_username}\n"
        f"💰 Amount: {deal.quantity} {deal.token}\n\n"
        "⚠️ An admin will review this dispute.\n"
        "Please submit any evidence to support your claim."
    )
