"""Unit tests for position accounting and weighted average cost basis."""

import pytest
from novaengine.core.portfolio import PortfolioPosition, PortfolioState


def test_position_weighted_average_cost_basis():
    # Buy 10 shares at €100 (Total cost = €1,000)
    pos = PortfolioPosition(
        asset_id="AAPL",
        asset_name="Apple Inc.",
        asset_type="stock",
        quantity=10.0,
        avg_buy_price=100.0,
        current_price=100.0,
    )
    assert pos.total_cost == 1000.0

    # Add 10 shares at €200 (Added cost = €2,000)
    # Total quantity = 20, Total cost = €3,000, New average = €150
    pos.add_volume(added_quantity=10.0, price_per_unit_eur=200.0)
    assert pos.quantity == 20.0
    assert pytest.approx(pos.avg_buy_price, 0.001) == 150.0
    assert pos.total_cost == 3000.0
    assert pos.current_price == 200.0


def test_position_partial_reduction():
    pos = PortfolioPosition(
        asset_id="AAPL",
        asset_name="Apple Inc.",
        asset_type="stock",
        quantity=20.0,
        avg_buy_price=150.0,
        current_price=200.0,
    )

    # Sell 5 shares at €210
    pos.reduce_volume(sold_quantity=5.0, exit_price_eur=210.0)
    assert pos.quantity == 15.0
    # Average purchase price remains unchanged
    assert pos.avg_buy_price == 150.0
    assert pos.current_price == 210.0


def test_portfolio_net_worth_and_returns():
    state = PortfolioState(cash_balance=50000.0, initial_capital=100000.0)
    state.positions["AAPL"] = PortfolioPosition(
        asset_id="AAPL",
        asset_name="Apple Inc.",
        asset_type="stock",
        quantity=100.0,
        avg_buy_price=500.0,
        current_price=600.0,
    )

    # Total invested = 100 * 600 = €60,000
    assert state.total_invested == 60000.0
    # Net worth = €50,000 cash + €60,000 invested = €110,000
    assert state.total_net_worth == 110000.0
    # Total profit = €110,000 - €100,000 = €10,000
    assert state.total_profit_loss == 10000.0
    # Return = +10.0%
    assert state.total_profit_loss_percent == 10.0
