"""Order models, execution types, and transaction audit records."""

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Optional
import uuid


class OrderSide(str, Enum):
    """Side of the market order."""
    BUY = "buy"
    SELL = "sell"


class AssetType(str, Enum):
    """Category of the traded asset."""
    STOCK = "stock"
    CRYPTO = "crypto"


class OrderStatus(str, Enum):
    """Execution status of an order."""
    FILLED = "filled"
    REJECTED = "rejected"
    PENDING = "pending"


@dataclass
class OrderRequest:
    """Parameters required to place an execution request."""

    asset_id: str
    asset_name: str
    asset_type: AssetType
    side: OrderSide
    quantity: float
    price_per_unit: float
    country_code: Optional[str] = "ES"
    image_url: Optional[str] = None


@dataclass
class OrderReceipt:
    """Immutable audit trail for an executed or rejected transaction."""

    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    timestamp: datetime = field(default_factory=datetime.now)
    asset_id: str = ""
    asset_name: str = ""
    asset_type: str = "stock"
    side: str = "buy"
    quantity: float = 0.0
    price_per_unit: float = 0.0
    total_gross_amount: float = 0.0
    broker_fee: float = 0.0
    transaction_tax: float = 0.0
    capital_gains_tax: float = 0.0
    net_amount: float = 0.0
    country_code: str = "ES"
    status: OrderStatus = OrderStatus.FILLED
    rejection_reason: Optional[str] = None

    @property
    def total_friction(self) -> float:
        """Combined total of all broker fees, market exchange canons, and taxes."""
        return self.broker_fee + self.transaction_tax + self.capital_gains_tax
