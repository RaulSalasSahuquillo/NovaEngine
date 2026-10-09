"""Multi-currency exchange rate harmonization engine.

Operates with EUR as the canonical internal base currency. All portfolio valuation,
cross-border order conversions, and fiscal withholdings are harmonized through this
service to ensure deterministic arithmetic across heterogeneous currency quotes.
"""

from typing import Dict, Optional
import requests


class CurrencyService:
    """Manages FX conversion matrices with fallback rates and live synchronization."""

    # Benchmark conversion baselines against 1.00 EUR
    _fallback_rates: Dict[str, float] = {
        "EUR": 1.0,
        "USD": 1.085,
        "GBP": 0.855,
        "JPY": 168.50,
        "CHF": 0.945,
        "CAD": 1.490,
        "AUD": 1.645,
        "SEK": 11.35,
        "MXN": 21.20,
        "BRL": 5.95,
    }

    def __init__(self, custom_rates: Optional[Dict[str, float]] = None):
        self._rates = dict(self._fallback_rates)
        if custom_rates:
            for symbol, rate in custom_rates.items():
                if rate > 0:
                    self._rates[symbol.upper().strip()] = float(rate)

    @property
    def current_rates(self) -> Dict[str, float]:
        """Returns an immutable copy of the active exchange rates against EUR."""
        return dict(self._rates)

    def get_rate_against_eur(self, currency_code: str) -> float:
        """Returns the rate of 1 EUR in target currency."""
        code = currency_code.upper().strip()
        return self._rates.get(code, 1.0)

    def to_eur(self, amount: float, from_currency: str) -> float:
        """Converts an amount from a specified currency into canonical EUR."""
        code = from_currency.upper().strip()
        if code == "EUR":
            return amount
        rate = self.get_rate_against_eur(code)
        if rate <= 0:
            return amount
        return amount / rate

    def from_eur(self, amount: float, to_currency: str) -> float:
        """Converts an amount from canonical EUR into the target currency."""
        code = to_currency.upper().strip()
        if code == "EUR":
            return amount
        rate = self.get_rate_against_eur(code)
        return amount * rate

    def convert(self, amount: float, from_currency: str, to_currency: str) -> float:
        """Cross-converts an amount directly between any two supported currencies."""
        from_code = from_currency.upper().strip()
        to_code = to_currency.upper().strip()
        if from_code == to_code:
            return amount
        eur_value = self.to_eur(amount, from_code)
        return self.from_eur(eur_value, to_code)

    def refresh_live_rates(self, timeout_seconds: float = 3.5) -> bool:
        """Attempts to update exchange rates from the public open exchange rates endpoint."""
        url = "https://open.er-api.com/v6/latest/EUR"
        try:
            response = requests.get(
                url,
                headers={"User-Agent": "NovaEngine/1.0 (Headless Financial Core)"},
                timeout=timeout_seconds,
            )
            if response.status_code == 200:
                payload = response.json()
                api_rates = payload.get("rates", {})
                if isinstance(api_rates, dict):
                    for code in self._fallback_rates:
                        if code in api_rates and float(api_rates[code]) > 0:
                            self._rates[code] = float(api_rates[code])
                    return True
        except Exception:
            # Network failures silently preserve offline baseline rates
            pass
        return False


# Shared default singleton instance for convenience
default_currency_service = CurrencyService()
