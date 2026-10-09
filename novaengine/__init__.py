"""NovaEngine: Headless Quantitative Trading, Market Feeds, and Fiscal Auditing Core.

Extracted from Stock_Simulator as a modular, GUI-independent engine.
"""

from novaengine.analytics.metrics import AnalyticsEngine, PerformanceMetrics
from novaengine.core.engine import NovaEngine
from novaengine.core.orders import AssetType, OrderReceipt, OrderSide, OrderStatus
from novaengine.core.portfolio import PortfolioPosition, PortfolioState
from novaengine.market.coingecko import CoinGeckoProvider
from novaengine.market.currency import CurrencyService, default_currency_service
from novaengine.market.yahoo import YahooFinanceProvider
from novaengine.storage.base import StorageProvider
from novaengine.storage.json_store import JsonStorageProvider
from novaengine.storage.sqlite_store import SqliteStorageProvider
from novaengine.tax.calculator import TaxCalculator, TradeTaxBreakdown
from novaengine.tax.profile import CountryTaxProfile, SUPPORTED_TAX_PROFILES, get_tax_profile

__version__ = "1.0.0"
__author__ = "Raúl Salas Sahuquillo <raulsalassahuquillo.dev@gmail.com>"

__all__ = [
    "NovaEngine",
    "AssetType",
    "OrderReceipt",
    "OrderSide",
    "OrderStatus",
    "PortfolioPosition",
    "PortfolioState",
    "YahooFinanceProvider",
    "CoinGeckoProvider",
    "CurrencyService",
    "default_currency_service",
    "TaxCalculator",
    "TradeTaxBreakdown",
    "CountryTaxProfile",
    "SUPPORTED_TAX_PROFILES",
    "get_tax_profile",
    "StorageProvider",
    "JsonStorageProvider",
    "SqliteStorageProvider",
    "AnalyticsEngine",
    "PerformanceMetrics",
]
