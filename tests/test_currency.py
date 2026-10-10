"""Unit tests for currency matrix conversions and base harmonization."""

import unittest
from novaengine.market.currency import CurrencyService


class TestCurrency(unittest.TestCase):
    def test_eur_base_conversion(self):
        service = CurrencyService(custom_rates={"USD": 1.10, "GBP": 0.88})

        self.assertAlmostEqual(service.from_eur(100.0, "USD"), 110.0, places=3)
        self.assertAlmostEqual(service.to_eur(110.0, "USD"), 100.0, places=3)
        self.assertEqual(service.to_eur(150.0, "EUR"), 150.0)
        self.assertEqual(service.from_eur(150.0, "EUR"), 150.0)

    def test_cross_currency_conversion(self):
        service = CurrencyService(custom_rates={"USD": 1.10, "GBP": 0.88})
        converted = service.convert(110.0, from_currency="USD", to_currency="GBP")
        self.assertAlmostEqual(converted, 88.0, places=3)

    def test_fallback_unsupported_currency(self):
        service = CurrencyService()
        self.assertEqual(service.get_rate_against_eur("XYZ"), 1.0)
        self.assertEqual(service.to_eur(50.0, "XYZ"), 50.0)


if __name__ == "__main__":
    unittest.main()
