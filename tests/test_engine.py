"""Unit tests for the NovaEngine simulation coordinator and order execution."""

import pytest
from novaengine.core.engine import NovaEngine
from novaengine.core.orders import AssetType, OrderSide, OrderStatus


def test_engine_buy_and_sell_cycle():
    engine = NovaEngine(country_code="ES", initial_capital=100000.0)

    # Buy 100 units of asset at €100
    buy_receipt = engine.buy(
        asset_id="AAPL",
        quantity=100.0,
        price_per_unit=100.0,
        asset_name="Apple Inc.",
        asset_type=AssetType.STOCK,
    )

    assert buy_receipt.status == OrderStatus.FILLED
    assert buy_receipt.side == OrderSide.BUY.value
    assert "AAPL" in engine.positions
    assert engine.positions["AAPL"].quantity == 100.0
    assert engine.cash_balance < 100000.0  # Cash debited by cost + tax + fees

    # Sell 50 units at profit (€150)
    sell_receipt = engine.sell(
        asset_id="AAPL",
        quantity=50.0,
        price_per_unit=150.0,
        asset_type=AssetType.STOCK,
    )

    assert sell_receipt.status == OrderStatus.FILLED
    assert sell_receipt.capital_gains_tax > 0.0  # Capital gains tax withheld
    assert engine.positions["AAPL"].quantity == 50.0

    # Sell remaining 50 units
    final_sell = engine.sell(
        asset_id="AAPL",
        quantity=50.0,
        price_per_unit=150.0,
        asset_type=AssetType.STOCK,
    )
    assert final_sell.status == OrderStatus.FILLED
    assert "AAPL" not in engine.positions  # Fully liquidated position removed


def test_engine_rejects_insufficient_funds():
    engine = NovaEngine(country_code="ES", initial_capital=1000.0)

    # Attempt to buy €100,000 worth of stock with only €1,000 in reserves
    receipt = engine.buy(
        asset_id="TSLA",
        quantity=500.0,
        price_per_unit=200.0,
        asset_type=AssetType.STOCK,
    )

    assert receipt.status == OrderStatus.REJECTED
    assert "Insufficient funds" in receipt.rejection_reason
    assert "TSLA" not in engine.positions
    assert engine.cash_balance == 1000.0


def test_engine_rejects_selling_unowned_asset():
    engine = NovaEngine(country_code="ES", initial_capital=10000.0)

    receipt = engine.sell(
        asset_id="NVDA",
        quantity=10.0,
        price_per_unit=130.0,
        asset_type=AssetType.STOCK,
    )

    assert receipt.status == OrderStatus.REJECTED
    assert "Insufficient position" in receipt.rejection_reason


def test_statement_generation():
    engine = NovaEngine(country_code="ES", initial_capital=20000.0)
    engine.buy(
        asset_id="BTC",
        quantity=0.1,
        price_per_unit=60000.0,
        asset_name="Bitcoin",
        asset_type=AssetType.CRYPTO,
    )

    statement = engine.get_statement(currency_code="EUR")
    assert statement["currency"] == "EUR"
    assert len(statement["holdings"]) == 1
    assert statement["holdings"][0]["asset_id"] == "BTC"
    assert statement["holdings"][0]["quantity"] == 0.1
