"""Abstract market models and data provider contracts."""

from abc import ABC, abstractmethod
from dataclasses import dataclass
from datetime import datetime
from typing import Dict, List, Optional


@dataclass
class MarketQuote:
    """Represents a standard security quote for equities or exchange-traded funds."""

    symbol: str
    name: str
    current_price: float
    change: float
    change_percent: float
    high: float
    low: float
    open: float
    previous_close: float
    currency: str = "USD"
    image_url: Optional[str] = None
    volume: Optional[int] = None
    market_cap: Optional[float] = None
    timestamp: Optional[datetime] = None


@dataclass
class CryptoQuote:
    """Represents a cryptocurrency market quote with ranking and circulating metrics."""

    id: str
    symbol: str
    name: str
    current_price: float
    change_24h: float
    change_percent_24h: float
    market_cap: float
    market_cap_rank: int
    volume_24h: float
    high_24h: float
    low_24h: float
    image_url: Optional[str] = None
    sparkline_7d: Optional[List[float]] = None


class MarketDataProvider(ABC):
    """Abstract interface for security and cryptocurrency market data sources."""

    @abstractmethod
    def get_quote(self, symbol: str) -> Optional[MarketQuote]:
        """Fetches the latest snapshot for a single ticker symbol."""

    @abstractmethod
    def get_quotes(self, symbols: List[str]) -> Dict[str, MarketQuote]:
        """Batch fetches quotes for multiple ticker symbols."""
