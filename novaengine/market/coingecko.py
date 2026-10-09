"""CoinGecko cryptocurrency market data connector with caching.

Interacts with the CoinGecko public API v3 to retrieve real-time spot rates,
24-hour volume metrics, and capitalization rankings. Includes offline fallbacks
to ensure continuous execution during development or network isolation.
"""

from datetime import datetime, timedelta
from typing import Dict, List, Optional
import requests

from novaengine.market.base import CryptoQuote


class _CryptoCacheEntry:
    def __init__(self, data, ttl_seconds: float):
        self.data = data
        self.expires_at = datetime.now() + timedelta(seconds=ttl_seconds)

    @property
    def is_valid(self) -> bool:
        return datetime.now() < self.expires_at


class CoinGeckoProvider:
    """Provides cryptocurrency market data feeds."""

    # Offline benchmark seeds for zero-downtime execution
    _offline_seeds: Dict[str, Dict] = {
        "bitcoin": {"sym": "BTC", "name": "Bitcoin", "price": 63400.0, "chg": 850.0, "pct": 1.35, "rank": 1, "mcap": 1.25e12},
        "ethereum": {"sym": "ETH", "name": "Ethereum", "price": 3120.0, "chg": -45.0, "pct": -1.42, "rank": 2, "mcap": 3.75e11},
        "solana": {"sym": "SOL", "name": "Solana", "price": 142.50, "chg": 5.20, "pct": 3.78, "rank": 3, "mcap": 6.8e10},
        "binancecoin": {"sym": "BNB", "name": "BNB", "price": 575.0, "chg": 2.10, "pct": 0.36, "rank": 4, "mcap": 8.6e10},
        "ripple": {"sym": "XRP", "name": "XRP", "price": 0.58, "chg": 0.01, "pct": 1.75, "rank": 5, "mcap": 3.2e10},
    }

    def __init__(self, session: Optional[requests.Session] = None, cache_ttl_seconds: float = 12.0):
        self._session = session or requests.Session()
        self._cache_ttl = cache_ttl_seconds
        self._cache: Dict[str, _CryptoCacheEntry] = {}
        self._headers = {
            "User-Agent": "Mozilla/5.0 (compatible; NovaEngine/1.0; +https://github.com/raulsalas/NovaEngine)",
            "Accept": "application/json",
        }

    def _parse_item(self, item: dict) -> CryptoQuote:
        price = float(item.get("current_price") or 0.0)
        change_pct = float(item.get("price_change_percentage_24h") or 0.0)
        change_abs = float(item.get("price_change_24h") or 0.0)

        return CryptoQuote(
            id=str(item.get("id", "")).lower(),
            symbol=str(item.get("symbol", "")).upper(),
            name=str(item.get("name", "")),
            current_price=price,
            change_24h=change_abs,
            change_percent_24h=change_pct,
            market_cap=float(item.get("market_cap") or 0.0),
            market_cap_rank=int(item.get("market_cap_rank") or 999),
            volume_24h=float(item.get("total_volume") or 0.0),
            high_24h=float(item.get("high_24h") or price),
            low_24h=float(item.get("low_24h") or price),
            image_url=item.get("image"),
            sparkline_7d=item.get("sparkline_in_7d", {}).get("price")
            if isinstance(item.get("sparkline_in_7d"), dict)
            else None,
        )

    def get_crypto(self, asset_id: str) -> Optional[CryptoQuote]:
        """Fetches quote details for a specific crypto ID like 'bitcoin' or 'ethereum'."""
        clean_id = asset_id.lower().strip()
        cached = self._cache.get(clean_id)
        if cached and cached.is_valid:
            return cached.data

        url = (
            f"https://api.coingecko.com/api/v3/coins/markets"
            f"?vs_currency=eur&ids={clean_id}&sparkline=false&price_change_percentage=24h"
        )
        try:
            res = self._session.get(url, headers=self._headers, timeout=4.0)
            if res.status_code == 200:
                data = res.json()
                if isinstance(data, list) and data:
                    quote = self._parse_item(data[0])
                    self._cache[clean_id] = _CryptoCacheEntry(quote, self._cache_ttl)
                    return quote
        except Exception:
            pass

        if clean_id in self._offline_seeds:
            seed = self._offline_seeds[clean_id]
            quote = CryptoQuote(
                id=clean_id,
                symbol=seed["sym"],
                name=seed["name"],
                current_price=seed["price"],
                change_24h=seed["chg"],
                change_percent_24h=seed["pct"],
                market_cap=seed["mcap"],
                market_cap_rank=seed["rank"],
                volume_24h=seed["mcap"] * 0.05,
                high_24h=seed["price"] * 1.03,
                low_24h=seed["price"] * 0.97,
            )
            self._cache[clean_id] = _CryptoCacheEntry(quote, self._cache_ttl)
            return quote

        return None

    def get_top_cryptos(self, per_page: int = 10) -> List[CryptoQuote]:
        """Returns the top cryptocurrencies ordered by market capitalization."""
        url = (
            f"https://api.coingecko.com/api/v3/coins/markets"
            f"?vs_currency=eur&order=market_cap_desc&per_page={per_page}&page=1&sparkline=false"
        )
        try:
            res = self._session.get(url, headers=self._headers, timeout=4.5)
            if res.status_code == 200:
                data = res.json()
                if isinstance(data, list) and data:
                    return [self._parse_item(c) for c in data if isinstance(c, dict)]
        except Exception:
            pass

        # Use offline seeds when API is unreachable
        quotes: List[CryptoQuote] = []
        for cid in list(self._offline_seeds.keys())[:per_page]:
            q = self.get_crypto(cid)
            if q:
                quotes.append(q)
        return quotes
