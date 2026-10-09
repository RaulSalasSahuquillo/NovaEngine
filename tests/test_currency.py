"""Unit tests for currency matrix conversions and base harmonization."""

import pytest
from novaengine.market.currency import CurrencyService


def test_eur_base_conversion():
    service = CurrencyService(custom_rates={"USD": 1.10, "GBP": 0.88})

    # €100 into USD
    assert service.from_eur(100.0, "USD") == 110.0

    # $110 into EUR
    assert pytest.approx(service.to_eur(110.0, "USD"), 0.001) == 100.0

    # Identity conversion for EUR
    assert service.to_eur(150.0, "EUR") == 150.0
    assert service.from_eur(150.0, "EUR") == 150.0


def test_cross_currency_conversion():
    service = CurrencyService(custom_rates={"USD": 1.10, "GBP": 0.88})

    # Convert $110 USD to GBP: $110 USD -> €100 EUR -> £88 GBP
    converted = service.convert(110.0, from_currency="USD", to_currency="GBP")
    assert pytest.approx(converted, 0.001) == 88.0


def test_fallback_unsupported_currency():
    service = CurrencyService()
    # Unregistered currency falls back gracefully to a 1.0 rate
    assert service.get_rate_against_eur("XYZ") == 1.0
    assert service.to_eur(50.0, "XYZ") == 50.0
