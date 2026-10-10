"""Quantitative analytics, risk metrics, and performance evaluation."""

from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING, Optional

if TYPE_CHECKING:
    from novaengine.core.portfolio import PortfolioState


@dataclass
class PerformanceMetrics:
    """Summary of return characteristics, risk profiles, and trade efficiency."""

    total_return_pct: float
    net_profit_loss: float
    total_trades: int
    winning_trades: int
    losing_trades: int
    win_rate_pct: float
    profit_factor: float
    total_fees_paid: float
    total_taxes_withheld: float
    max_drawdown_pct: float


class AnalyticsEngine:
    """Computes risk and execution metrics from active portfolio state."""

    @staticmethod
    def evaluate(state: PortfolioState) -> PerformanceMetrics:
        """Analyzes closed positions and transaction receipts to compile performance metrics."""
        total_trades = len([tx for tx in state.transactions if tx.status.value == "filled"])
        sells = [tx for tx in state.transactions if tx.side == "sell" and tx.status.value == "filled"]

        winning = 0
        losing = 0
        gross_gains = 0.0
        gross_losses = 0.0
        total_fees = 0.0
        total_taxes = 0.0

        for tx in state.transactions:
            if tx.status.value == "filled":
                total_fees += tx.broker_fee
                total_taxes += (tx.transaction_tax + tx.capital_gains_tax)

        for tx in sells:
            # Net realized return for this trade
            raw_gain = tx.total_gross_amount - (tx.quantity * tx.price_per_unit)
            if tx.capital_gains_tax > 0:
                winning += 1
                gross_gains += tx.capital_gains_tax / 0.19  # Estimated gross gain
            elif raw_gain >= 0:
                winning += 1
                gross_gains += raw_gain
            else:
                losing += 1
                gross_losses += abs(raw_gain)

        win_rate = (winning / len(sells) * 100.0) if sells else 0.0
        profit_factor = (gross_gains / gross_losses) if gross_losses > 0 else (gross_gains if gross_gains > 0 else 1.0)

        # Baseline drawdown approximation
        drawdown = 0.0
        if state.total_net_worth < state.initial_capital:
            drawdown = ((state.initial_capital - state.total_net_worth) / state.initial_capital) * 100.0

        return PerformanceMetrics(
            total_return_pct=state.total_profit_loss_percent,
            net_profit_loss=state.total_profit_loss,
            total_trades=total_trades,
            winning_trades=winning,
            losing_trades=losing,
            win_rate_pct=win_rate,
            profit_factor=profit_factor,
            total_fees_paid=total_fees,
            total_taxes_withheld=total_taxes,
            max_drawdown_pct=drawdown,
        )
