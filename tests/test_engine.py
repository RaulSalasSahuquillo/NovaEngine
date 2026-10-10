"""Unit tests for the NovaEngine simulation coordinator and order execution."""

import unittest
from novaengine.core.engine import NovaEngine
from novaengine.core.orders import AssetType, OrderSide, OrderStatus


class TestEngine(unittest.TestCase):
    def test_engine_buy_and_sell_cycle(self):
        engine = NovaEngine(country_code="ES", initial_capital=100000.0)

        # Buy 100 units of asset at €100
        buy_receipt = engine.buy(
            asset_id="AAPL",
            quantity=100.0,
            price_per_unit=100.0,
            asset_name="Apple Inc.",
            asset_type=AssetType.STOCK,
        )

        self.assertEqual(buy_receipt.status, OrderStatus.FILLED)
        self.assertEqual(buy_receipt.side, OrderSide.BUY.value)
        self.assertIn("AAPL", engine.positions)
        self.assertEqual(engine.positions["AAPL"].quantity, 100.0)
        self.assertLess(engine.cash_balance, 100000.0)

        # Sell 50 units at profit (€150)
        sell_receipt = engine.sell(
            asset_id="AAPL",
            quantity=50.0,
            price_per_unit=150.0,
            asset_type=AssetType.STOCK,
        )

        self.assertEqual(sell_receipt.status, OrderStatus.FILLED)
        self.assertGreater(sell_receipt.capital_gains_tax, 0.0)
        self.assertEqual(engine.positions["AAPL"].quantity, 50.0)

        # Sell remaining 50 units
        final_sell = engine.sell(
            asset_id="AAPL",
            quantity=50.0,
            price_per_unit=150.0,
            asset_type=AssetType.STOCK,
        )
        self.assertEqual(final_sell.status, OrderStatus.FILLED)
        self.assertNotIn("AAPL", engine.positions)

    def test_engine_rejects_insufficient_funds(self):
        engine = NovaEngine(country_code="ES", initial_capital=1000.0)

        receipt = engine.buy(
            asset_id="TSLA",
            quantity=500.0,
            price_per_unit=200.0,
            asset_type=AssetType.STOCK,
        )

        self.assertEqual(receipt.status, OrderStatus.REJECTED)
        self.assertIn("Insufficient funds", receipt.rejection_reason)
        self.assertNotIn("TSLA", engine.positions)
        self.assertEqual(engine.cash_balance, 1000.0)

    def test_engine_rejects_selling_unowned_asset(self):
        engine = NovaEngine(country_code="ES", initial_capital=10000.0)

        receipt = engine.sell(
            asset_id="NVDA",
            quantity=10.0,
            price_per_unit=130.0,
            asset_type=AssetType.STOCK,
        )

        self.assertEqual(receipt.status, OrderStatus.REJECTED)
        self.assertIn("Insufficient position", receipt.rejection_reason)

    def test_statement_generation(self):
        engine = NovaEngine(country_code="ES", initial_capital=20000.0)
        engine.buy(
            asset_id="BTC",
            quantity=0.1,
            price_per_unit=60000.0,
            asset_name="Bitcoin",
            asset_type=AssetType.CRYPTO,
        )

        statement = engine.get_statement(currency_code="EUR")
        self.assertEqual(statement["currency"], "EUR")
        self.assertEqual(len(statement["holdings"]), 1)
        self.assertEqual(statement["holdings"][0]["asset_id"], "BTC")
        self.assertEqual(statement["holdings"][0]["quantity"], 0.1)


if __name__ == "__main__":
    unittest.main()
