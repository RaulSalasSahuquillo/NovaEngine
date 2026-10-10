"""Unit tests for multi-jurisdiction tax calculations and statutory trade breakdowns."""

import unittest
from novaengine.tax.calculator import TaxCalculator
from novaengine.tax.profile import get_tax_profile


class TestTax(unittest.TestCase):
    def test_spanish_hacienda_irpf_brackets(self):
        self.assertEqual(TaxCalculator.calculate_spanish_hacienda_irpf(0.0), 0.0)
        self.assertEqual(TaxCalculator.calculate_spanish_hacienda_irpf(-500.0), 0.0)

        # Bracket 1: Up to €6,000 at 19%
        self.assertEqual(TaxCalculator.calculate_spanish_hacienda_irpf(6000.0), 1140.0)

        # Bracket 2: €10,000 (€6,000 @ 19% + €4,000 @ 21%)
        self.assertEqual(TaxCalculator.calculate_spanish_hacienda_irpf(10000.0), 1140.0 + 840.0)

        # Bracket 3: €100,000 (€6,000 @ 19% + €44,000 @ 21% + €50,000 @ 23%)
        expected_100k = (6000 * 0.19) + (44000 * 0.21) + (50000 * 0.23)
        self.assertEqual(TaxCalculator.calculate_spanish_hacienda_irpf(100000.0), expected_100k)

        # Bracket 5: > €300,000
        expected_400k = (
            (6000 * 0.19)
            + (44000 * 0.21)
            + (150000 * 0.23)
            + (100000 * 0.27)
            + (100000 * 0.28)
        )
        self.assertEqual(TaxCalculator.calculate_spanish_hacienda_irpf(400000.0), expected_400k)

    def test_buy_breakdown_with_tobin_tax(self):
        breakdown = TaxCalculator.calculate_buy_breakdown(
            quantity=100.0,
            price_per_unit=100.0,
            is_stock=True,
            country_code="ES",
        )

        self.assertEqual(breakdown.gross_amount, 10000.0)
        self.assertEqual(breakdown.broker_fee, 7.00)
        self.assertAlmostEqual(breakdown.exchange_fee, 3.00, places=3)
        self.assertEqual(breakdown.transaction_tax, 20.00)
        self.assertAlmostEqual(breakdown.net_amount, 10030.00, places=3)

    def test_sell_breakdown_with_capital_gains(self):
        breakdown = TaxCalculator.calculate_sell_breakdown(
            quantity=50.0,
            price_per_unit=150.0,
            avg_buy_price=100.0,
            is_stock=True,
            country_code="ES",
        )

        self.assertEqual(breakdown.gross_amount, 7500.0)
        self.assertEqual(breakdown.realized_profit, 2500.0)
        self.assertEqual(breakdown.capitalGainsTax if hasattr(breakdown, 'capitalGainsTax') else breakdown.capital_gains_tax, 475.00)
        self.assertEqual(breakdown.broker_fee, 5.25)
        self.assertEqual(breakdown.exchange_fee, 2.25)
        expected_net = 7500.0 - 5.25 - 2.25 - 0.0 - 475.00
        self.assertEqual(breakdown.net_amount, expected_net)

    def test_minimum_broker_fee_enforcement(self):
        breakdown = TaxCalculator.calculate_buy_breakdown(
            quantity=1.0,
            price_per_unit=100.0,
            is_stock=True,
            country_code="ES",
        )
        profile = get_tax_profile("ES")
        self.assertEqual(breakdown.broker_fee, profile.minimum_broker_fee)


if __name__ == "__main__":
    unittest.main()
