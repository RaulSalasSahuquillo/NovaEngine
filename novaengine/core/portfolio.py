"""Portfolio accounting, weighted average cost tracking, and P&L computation.

All internal financial values are stored in canonical EUR to eliminate cross-currency
drift during multi-asset holding periods. Conversions to display currencies occur
dynamically at the reporting boundary.
"""

from dataclasses import dataclass, field
from typing import Dict, List, Optional
from novaengine.core.orders import OrderReceipt


@dataclass
class PortfolioPosition:
    """Represents an open position in an individual equity or cryptocurrency."""

    asset_id: str
    asset_name: str
    asset_type: str
    quantity: float
    avg_buy_price: float
    current_price: float
    image_url: Optional[str] = None

    @property
    def total_value(self) -> float:
        """Current market value of the position in canonical EUR."""
        return self.quantity * self.current_price

    @property
    def total_cost(self) -> float:
        """Historical acquisition cost invested into the position in canonical EUR."""
        return self.quantity * self.avg_buy_price

    @property
    def profit_loss(self) -> float:
        """Unrealized net profit or loss in canonical EUR."""
        return self.total_value - self.total_cost

    @property
    def profit_loss_percent(self) -> float:
        """Unrealized return percentage relative to invested cost."""
        if self.total_cost <= 0.0:
            return 0.0
        return (self.profit_loss / self.total_cost) * 100.0

    def add_volume(self, added_quantity: float, price_per_unit_eur: float) -> None:
        """Adjusts holdings and recalculates the weighted average acquisition cost."""
        if added_quantity <= 0.0:
            return

        combined_cost = self.total_cost + (added_quantity * price_per_unit_eur)
        new_quantity = self.quantity + added_quantity
        self.avg_buy_price = combined_cost / new_quantity
        self.quantity = new_quantity
        self.current_price = price_per_unit_eur

    def reduce_volume(self, sold_quantity: float, exit_price_eur: float) -> None:
        """Reduces open position volume following a partial or complete sale."""
        self.quantity = max(0.0, self.quantity - sold_quantity)
        self.current_price = exit_price_eur


@dataclass
class PortfolioState:
    """Ledger state tracking cash balances, open positions, and execution history."""

    cash_balance: float = 100000.0
    initial_capital: float = 100000.0
    positions: Dict[str, PortfolioPosition] = field(default_factory=dict)
    transactions: List[OrderReceipt] = field(default_factory=list)

    @property
    def total_invested(self) -> float:
        """Aggregate market valuation across all open positions in canonical EUR."""
        return sum(pos.total_value for pos in self.positions.values())

    @property
    def total_net_worth(self) -> float:
        """Total equity value combining active cash reserves and open positions."""
        return self.cash_balance + self.total_invested

    @property
    def total_profit_loss(self) -> float:
        """Aggregate account return relative to initial funding capital."""
        return self.total_net_worth - self.initial_capital

    @property
    def total_profit_loss_percent(self) -> float:
        """Aggregate portfolio return percentage."""
        if self.initial_capital <= 0.0:
            return 0.0
        return (self.total_profit_loss / self.initial_capital) * 100.0

    @property
    def holdings_profit_loss(self) -> float:
        """Combined unrealized return across currently held assets."""
        return sum(pos.profit_loss for pos in self.positions.values())

    def get_position(self, asset_id: str) -> Optional[PortfolioPosition]:
        """Looks up a position by its case-insensitive ticker or asset ID."""
        return self.positions.get(asset_id.upper().strip()) or self.positions.get(asset_id.lower().strip())
