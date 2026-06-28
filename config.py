"""
Configuration for P2P Crypto Escrow Bot
"""
import os
from dotenv import load_dotenv

load_dotenv()

# Bot Token - Set via environment variable or .env file
BOT_TOKEN = os.getenv("BOT_TOKEN", "YOUR_BOT_TOKEN_HERE")

# Admin user IDs (can manage disputes, override actions)
ADMIN_IDS = [int(x) for x in os.getenv("ADMIN_IDS", "").split(",") if x.strip()]

# Escrow settings
DEPOSIT_TIMEOUT_MINUTES = 20.0  # Address reset timer
MAX_GROUP_MEMBERS = 2  # Max members per escrow group

# Bot info
BOT_NAME = "P2P Crypto Escrow Bot"
BOT_VERSION = "1.0.0"

# Supported tokens and networks
SUPPORTED_TOKENS = {
    "BTC": {
        "name": "Bitcoin",
        "networks": ["Bitcoin"]
    },
    "LTC": {
        "name": "Litecoin",
        "networks": ["Litecoin"]
    },
    "USDT": {
        "name": "Tether",
        "networks": ["BSC(BEP20)", "TRON(TRC20)"]
    }
}

# Deal statuses
class DealStatus:
    CREATED = "created"
    DETAILS_FILLED = "details_filled"
    ROLES_SET = "roles_set"
    TOKEN_SELECTED = "token_selected"
    ACCEPTED = "accepted"
    DEPOSITED = "deposited"
    RELEASED = "released"
    REFUNDED = "refunded"
    DISPUTED = "disputed"
    EXPIRED = "expired"
