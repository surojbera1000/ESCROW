"""
Data models for the P2P Crypto Escrow Bot
"""
import json
import time
import uuid
import os
from dataclasses import dataclass, field, asdict
from typing import Optional


@dataclass
class EscrowDeal:
    """Represents a single escrow deal between buyer and seller."""
    
    deal_id: str = field(default_factory=lambda: str(uuid.uuid4())[:8].upper())
    chat_id: Optional[int] = None  # Group chat ID
    creator_id: Optional[int] = None  # User who created the escrow
    deal_type: str = "p2p"  # "p2p" or "product"
    
    # Deal details (from /dd)
    quantity: Optional[str] = None
    rate: Optional[str] = None
    conditions: Optional[str] = None
    
    # Seller info
    seller_id: Optional[int] = None
    seller_username: Optional[str] = None
    seller_wallet: Optional[str] = None
    
    # Buyer info
    buyer_id: Optional[int] = None
    buyer_username: Optional[str] = None
    buyer_wallet: Optional[str] = None
    
    # Token & Network
    token: Optional[str] = None  # BTC, LTC, USDT
    network: Optional[str] = None  # BSC(BEP20), TRON(TRC20), Bitcoin, Litecoin
    
    # Deal state
    status: str = "created"  # created, details_filled, roles_set, token_selected, accepted, deposited, released, refunded, disputed, expired
    
    # Deposit info
    escrow_address: Optional[str] = None
    transaction_id: Optional[str] = None
    deposit_amount: Optional[str] = None
    deposit_time: Optional[float] = None
    
    # Timestamps
    created_at: float = field(default_factory=time.time)
    updated_at: float = field(default_factory=time.time)
    
    # Group invite link
    invite_link: Optional[str] = None
    
    def to_dict(self) -> dict:
        """Convert deal to dictionary."""
        return asdict(self)
    
    @classmethod
    def from_dict(cls, data: dict) -> "EscrowDeal":
        """Create deal from dictionary."""
        return cls(**{k: v for k, v in data.items() if k in cls.__dataclass_fields__})
    
    def update_status(self, new_status: str):
        """Update deal status and timestamp."""
        self.status = new_status
        self.updated_at = time.time()
    
    def has_both_roles(self) -> bool:
        """Check if both buyer and seller are set."""
        return (
            self.seller_id is not None 
            and self.buyer_id is not None
            and self.seller_wallet is not None
            and self.buyer_wallet is not None
        )
    
    def has_deal_details(self) -> bool:
        """Check if deal details are filled."""
        return (
            self.quantity is not None
            and self.rate is not None
        )
    
    def is_participant(self, user_id: int) -> bool:
        """Check if user is a participant in this deal."""
        return user_id in (self.seller_id, self.buyer_id, self.creator_id)


class DealStore:
    """In-memory deal storage with JSON persistence."""
    
    def __init__(self, data_dir: str = "data"):
        self._deals: dict[str, EscrowDeal] = {}  # deal_id -> EscrowDeal
        self._chat_deals: dict[int, str] = {}  # chat_id -> deal_id
        self._user_deals: dict[int, list[str]] = {}  # user_id -> [deal_ids]
        self._data_dir = data_dir
        self._data_file = os.path.join(data_dir, "deals.json")
        self._load()
    
    def create_deal(self, creator_id: int, deal_type: str = "p2p") -> EscrowDeal:
        """Create a new escrow deal."""
        deal = EscrowDeal(
            creator_id=creator_id,
            deal_type=deal_type,
        )
        self._deals[deal.deal_id] = deal
        
        # Track user deals
        if creator_id not in self._user_deals:
            self._user_deals[creator_id] = []
        self._user_deals[creator_id].append(deal.deal_id)
        
        self._save()
        return deal
    
    def get_deal(self, deal_id: str) -> Optional[EscrowDeal]:
        """Get deal by ID."""
        return self._deals.get(deal_id)
    
    def get_deal_by_chat(self, chat_id: int) -> Optional[EscrowDeal]:
        """Get deal associated with a chat/group."""
        deal_id = self._chat_deals.get(chat_id)
        if deal_id:
            return self._deals.get(deal_id)
        return None
    
    def get_user_deals(self, user_id: int) -> list[EscrowDeal]:
        """Get all deals for a user."""
        deal_ids = self._user_deals.get(user_id, [])
        return [self._deals[did] for did in deal_ids if did in self._deals]
    
    def link_chat(self, deal_id: str, chat_id: int):
        """Associate a chat/group with a deal."""
        deal = self._deals.get(deal_id)
        if deal:
            deal.chat_id = chat_id
            self._chat_deals[chat_id] = deal_id
            self._save()
    
    def update_deal(self, deal: EscrowDeal):
        """Update an existing deal."""
        deal.updated_at = time.time()
        self._deals[deal.deal_id] = deal
        if deal.chat_id:
            self._chat_deals[deal.chat_id] = deal.deal_id
        self._save()
    
    def delete_deal(self, deal_id: str):
        """Delete a deal."""
        deal = self._deals.pop(deal_id, None)
        if deal:
            if deal.chat_id and deal.chat_id in self._chat_deals:
                del self._chat_deals[deal.chat_id]
            # Remove from user deals
            for uid, dids in self._user_deals.items():
                if deal_id in dids:
                    dids.remove(deal_id)
            self._save()
    
    def save(self):
        """Public save method."""
        self._save()
    
    def _save(self):
        """Persist deals to JSON file."""
        os.makedirs(self._data_dir, exist_ok=True)
        data = {
            "deals": {did: deal.to_dict() for did, deal in self._deals.items()},
            "chat_deals": {str(k): v for k, v in self._chat_deals.items()},
            "user_deals": {str(k): v for k, v in self._user_deals.items()},
        }
        try:
            with open(self._data_file, "w") as f:
                json.dump(data, f, indent=2)
        except Exception as e:
            print(f"Error saving deals: {e}")
    
    def _load(self):
        """Load deals from JSON file."""
        if not os.path.exists(self._data_file):
            return
        try:
            with open(self._data_file, "r") as f:
                data = json.load(f)
            
            # Restore deals
            for did, deal_data in data.get("deals", {}).items():
                self._deals[did] = EscrowDeal.from_dict(deal_data)
            
            # Restore chat mappings
            for chat_id_str, deal_id in data.get("chat_deals", {}).items():
                self._chat_deals[int(chat_id_str)] = deal_id
            
            # Restore user mappings
            for uid_str, dids in data.get("user_deals", {}).items():
                self._user_deals[int(uid_str)] = dids
                
        except Exception as e:
            print(f"Error loading deals: {e}")


# Global deal store instance
deal_store = DealStore()
