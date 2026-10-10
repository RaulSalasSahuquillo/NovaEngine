"""Unit tests for position accounting and weighted average cost basis."""

import unittest
from novaengine.core.portfolio import PortfolioPosition, PortfolioState


class TestPortfolio(unittest.TestCase):
    def test_position_weighted_average_cost_basis(self):
        pos = PortfolioPosition(
            asset_id="AAPL",
            asset_name="Apple Inc.",
            asset_type="stock",
            quantity=10.0,
            avg_buy_price=100.0,
            current_price=100.0,
        )
        self.assertEqual(pos.total_cost, 1000.0)

        pos.add_volume(added_quantity=10.0, price_per_unit_eur=200.0)
        self.assertEqual(pos.quantity, 20.0)
        self.assertAlmostEqual(pos.avg_buy_price, 150.0, places=3)
        self.assertEqual(pos.total_cost, 3000.0)
        self.assertEqual(pos.current_price, 200.0)

    def test_position_partial_reduction(self):
        pos = PortfolioPosition(
            asset_id="AAPL",
            asset_name="Apple Inc.",
            asset_type="stock",
            quantity=20.0,
            avg_buy_price=150.0,
            current_price=200.0,
        )

        pos.reduce_volume(sold_quantity=5.0, exit_price_eur=210.0)
        self.assertEqual(pos.quantity, 15.0)
        self.assertEqual(pos.avg_buy_price, 150.0)
        self.assertEqual(pos.current_price, 210.0)

    def test_portfolio_net_worth_and_returns(self):
        state = PortfolioState(cash_balance=50000.0, initial_capital=100000.0)
        state.positions["AAPL"] = PortfolioPosition(
            asset_id="AAPL",
            asset_name="Apple Inc.",
            asset_type="stock",
            quantity=100.0,
            avg_buy_price=500.0,
            current_price=600.0,
        )

        self.assertEqual(state.total_invested, 60000.0)
        self.assertEqual(state.total_net_worth, 110000.0)
        self.assertEqual(state.total_profit_loss, 10000.0)
        self.assertEqual(state.total_profit_loss_percent, 10.0)


if __name__ == "__main__":
    unittest.main()
