"""
Inline keyboard builders for the Escrow Bot.
"""
from telegram import InlineKeyboardButton, InlineKeyboardMarkup


def start_keyboard() -> InlineKeyboardMarkup:
    """Main start menu keyboard."""
    keyboard = [
        [InlineKeyboardButton("🚀 START", callback_data="start_menu")],
    ]
    return InlineKeyboardMarkup(keyboard)


def escrow_type_keyboard() -> InlineKeyboardMarkup:
    """Escrow type selection keyboard."""
    keyboard = [
        [
            InlineKeyboardButton("🤝 P2P", callback_data="escrow_type_p2p"),
            InlineKeyboardButton("📦 Product Deal", callback_data="escrow_type_product"),
        ]
    ]
    return InlineKeyboardMarkup(keyboard)


def token_keyboard() -> InlineKeyboardMarkup:
    """Token selection keyboard."""
    keyboard = [
        [
            InlineKeyboardButton("🪙 LTC", callback_data="token_LTC"),
            InlineKeyboardButton("₿ BTC", callback_data="token_BTC"),
            InlineKeyboardButton("💵 USDT", callback_data="token_USDT"),
        ]
    ]
    return InlineKeyboardMarkup(keyboard)


def network_keyboard(token: str) -> InlineKeyboardMarkup:
    """Network selection keyboard based on chosen token."""
    networks = {
        "BTC": [("Bitcoin", "network_Bitcoin")],
        "LTC": [("Litecoin", "network_Litecoin")],
        "USDT": [
            ("BSC(BEP20)", "network_BSC(BEP20)"),
            ("TRON(TRC20)", "network_TRON(TRC20)"),
        ],
    }
    
    buttons = networks.get(token, [])
    keyboard = [[InlineKeyboardButton(name, callback_data=cb)] for name, cb in buttons]
    keyboard.append([InlineKeyboardButton("⬅️ Back", callback_data="token_back")])
    return InlineKeyboardMarkup(keyboard)


def accept_reject_keyboard() -> InlineKeyboardMarkup:
    """Accept/Reject deal declaration keyboard."""
    keyboard = [
        [
            InlineKeyboardButton("Accept ✅", callback_data="deal_accept"),
            InlineKeyboardButton("Reject ❌", callback_data="deal_reject"),
        ]
    ]
    return InlineKeyboardMarkup(keyboard)


def check_payment_keyboard() -> InlineKeyboardMarkup:
    """Check payment button for deposit."""
    keyboard = [
        [InlineKeyboardButton("🔍 Check Payment", callback_data="check_payment")],
    ]
    return InlineKeyboardMarkup(keyboard)


def confirm_release_keyboard() -> InlineKeyboardMarkup:
    """Confirm release action keyboard."""
    keyboard = [
        [
            InlineKeyboardButton("Yes ✅", callback_data="confirm_release_yes"),
            InlineKeyboardButton("No ❌", callback_data="confirm_release_no"),
        ]
    ]
    return InlineKeyboardMarkup(keyboard)


def confirm_refund_keyboard() -> InlineKeyboardMarkup:
    """Confirm refund action keyboard."""
    keyboard = [
        [
            InlineKeyboardButton("Yes ✅", callback_data="confirm_refund_yes"),
            InlineKeyboardButton("No ❌", callback_data="confirm_refund_no"),
        ]
    ]
    return InlineKeyboardMarkup(keyboard)


def dispute_keyboard() -> InlineKeyboardMarkup:
    """Dispute options keyboard."""
    keyboard = [
        [
            InlineKeyboardButton("📝 Submit Evidence", callback_data="dispute_evidence"),
            InlineKeyboardButton("❌ Cancel Dispute", callback_data="dispute_cancel"),
        ]
    ]
    return InlineKeyboardMarkup(keyboard)
