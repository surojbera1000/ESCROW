# 🔐 P2P Crypto Escrow Telegram Bot

A fully functional P2P cryptocurrency escrow bot built with Python and the `python-telegram-bot` library (v20+). This bot facilitates secure crypto trades between buyers and sellers through an automated escrow workflow.

## ✨ Features

- **Escrow Creation** — Create P2P or Product Deal escrow sessions
- **Private Groups** — Automated group linking for deal participants
- **Deal Details** — Structured form for quantity, rate, and conditions
- **Role Declaration** — Buyer/Seller registration with wallet addresses
- **Multi-Token Support** — BTC, LTC, USDT with network selection
- **Deposit System** — Escrow address generation with countdown timer
- **Release/Refund** — One-command fund disbursement with confirmation
- **Dispute Resolution** — Built-in dispute system with admin notification
- **Persistent Storage** — JSON-based deal persistence

## 📋 Supported Tokens & Networks

| Token | Networks |
|-------|----------|
| BTC   | Bitcoin |
| LTC   | Litecoin |
| USDT  | BSC (BEP20), TRON (TRC20) |

## 🚀 Quick Start

### Prerequisites

- Python 3.10+
- A Telegram Bot Token (get from [@BotFather](https://t.me/BotFather))

### Installation

```bash
# 1. Clone or download the project
cd p2p_escrow_bot

# 2. Create virtual environment
python -m venv venv
source venv/bin/activate  # Linux/Mac
# or: venv\Scripts\activate  # Windows

# 3. Install dependencies
pip install -r requirements.txt

# 4. Configure environment
cp .env.example .env
# Edit .env and add your BOT_TOKEN

# 5. Run the bot
python bot.py
```

### Configuration

Edit the `.env` file:

```env
BOT_TOKEN=123456789:ABCdefGHIjklMNOpqrsTUVwxyz
ADMIN_IDS=your_telegram_user_id
```

## 📖 Bot Workflow

### Step 1: Start
User sends `/start` → Bot shows welcome menu with commands and a START button.

### Step 2: Create Escrow
User sends `/escrow` → Selects deal type (P2P or Product) → Bot creates deal and provides instructions.

### Step 3: Link Group
User creates a private Telegram group → Adds bot as admin → Sends `/link [deal_id]` in the group → Bot pins welcome message.

### Step 4: Fill Deal Details
User sends `/dd` → Bot asks for:
- Quantity (amount of crypto)
- Rate (price per unit)
- Conditions (terms of deal)

### Step 5: Declare Roles
```
/seller 0x1234567890abcdef1234567890abcdef12345678
/buyer TXyz123456789abcdef123456789abcdef1234
```

### Step 6: Select Token & Network
User sends `/token` → Selects crypto (LTC/BTC/USDT) → Selects network → Reviews deal summary → Accept or Reject.

### Step 7: Deposit
User sends `/deposit` → Bot generates escrow address → 20-minute countdown begins → Click "Check Payment" after sending.

### Step 8: Complete
- `/release` — Seller releases funds to buyer's wallet
- `/refund` — Buyer refunds funds to seller's wallet

## 🔧 Commands Reference

| Command | Description | Where |
|---------|-------------|-------|
| `/start` | Show main menu | DM |
| `/help` | Show help | Anywhere |
| `/escrow` | Create new escrow | DM |
| `/link [id]` | Link group to deal | Group |
| `/dd` | Fill deal details | Group |
| `/seller [wallet]` | Register as seller | Group |
| `/buyer [wallet]` | Register as buyer | Group |
| `/token` | Select crypto & network | Group |
| `/deposit` | Generate deposit address | Group |
| `/balance` | Check escrow balance | Group |
| `/release` | Release to buyer | Group |
| `/refund` | Refund to seller | Group |
| `/dispute` | Open dispute | Group |
| `/save` | Save deal data | Group |
| `/verify` | Verify transaction | Group |

## 📁 Project Structure

```
p2p_escrow_bot/
├── bot.py                  # Main entry point
├── config.py               # Configuration & constants
├── requirements.txt        # Dependencies
├── .env.example            # Environment template
├── README.md
│
├── handlers/
│   ├── __init__.py
│   ├── start.py            # /start & menu
│   ├── escrow.py           # /escrow & /link
│   ├── deal.py             # /dd (ConversationHandler)
│   ├── roles.py            # /seller & /buyer
│   ├── token.py            # /token & network
│   ├── deposit.py          # /deposit & payment check
│   ├── release_refund.py   # /release & /refund
│   └── dispute.py          # /dispute, /balance, /save, /verify
│
├── models/
│   ├── __init__.py
│   └── escrow_deal.py      # Data models & storage
│
├── utils/
│   ├── __init__.py
│   ├── keyboards.py        # Inline keyboards
│   ├── formatting.py       # Message formatters
│   └── wallet.py           # Address generation
│
└── data/
    └── deals.json          # Persistent storage (auto-created)
```

## ⚠️ Important Notes

1. **Simulated Transactions**: This bot simulates crypto transactions. In production, integrate with blockchain APIs (BlockCypher, Alchemy, TronGrid, etc.) for real fund management.

2. **Group Creation**: Telegram Bot API doesn't allow bots to create groups directly. Users must create a group, add the bot as admin, then use `/link` to connect it.

3. **Security**: For production use, add:
   - Proper wallet validation per network
   - Multi-signature escrow addresses
   - KYC/AML compliance
   - Rate limiting
   - Encrypted storage

4. **Admin Setup**: Set your Telegram user ID in `ADMIN_IDS` to receive dispute notifications.

## 🛡️ Security Considerations

- Never share your `BOT_TOKEN`
- Set `ADMIN_IDS` to restrict admin operations
- In production, use encrypted database instead of JSON
- Implement proper wallet key management
- Add rate limiting to prevent abuse

## 📜 License

MIT License - Use at your own risk. This is a demonstration project.
