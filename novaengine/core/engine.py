"""Main headless simulation engine coordinator.

Orchestrates multi-asset order execution, currency conversions, multi-jurisdiction
fiscal tax audits, position sizing, and persistent ledger commitments without
relying on any visual interface or graphical framework.
"""

from typing import Dict, List, Optional
import uuid

from novaengine.analytics.metrics import AnalyticsEngine, PerformanceMetrics
from novaengine.core.orders import AssetType, OrderReceipt, OrderSide, OrderStatus
from novaengine.core.portfolio import PortfolioPosition, PortfolioState
from novaengine.market.coingecko import CoinGeckoProvider
from novaengine.market.currency import CurrencyService, default_currency_service
from novaengine.market.yahoo import YahooFinanceProvider
from novaengine.storage.base import StorageProvider
from novaengine.tax.calculator import TaxCalculator
from novaengine.tax.profile import get_tax_profile


class NovaEngine:
    """Headless quantitative execution runtime and portfolio coordinator."""

    def __init__(
        self,
        country_code: str = "ES",
        initial_capital: float = 100000.0,
        currency_service: Optional[CurrencyService] = None,
        yahoo_provider: Optional[YahooFinanceProvider] = None,
        coingecko_provider: Optional[CoinGeckoProvider] = None,
        storage_provider: Optional[StorageProvider] = None,
    ):
        self.country_code = country_code.upper().strip()
        self.currency_service = currency_service or default_currency_service
        self.yahoo_provider = yahoo_provider or YahooFinanceProvider()
        self.coingecko_provider = coingecko_provider or CoinGeckoProvider()
        self.storage_provider = storage_provider

        # Attempt restoration from storage or initialize fresh portfolio
        loaded_state = self.storage_provider.load() if self.storage_provider else None
        if loaded_state:
            self.state = loaded_state
        else:
            self.state = PortfolioState(
                cash_balance=initial_capital,
                initial_capital=initial_capital,
            )

    @property
    def cash_balance(self) -> float:
        """Active cash reserve held in canonical EUR."""
        return self.state.cash_balance

    @property
    def total_net_worth(self) -> float:
        """Total current equity in canonical EUR."""
        return self.state.total_net_worth

    @property
    def positions(self) -> Dict[str, PortfolioPosition]:
        """Currently held asset positions indexed by ticker or coin identifier."""
        return self.state.positions

    @property
    def transactions(self) -> List[OrderReceipt]:
        """Immutable execution receipts recording trade history."""
        return self.state.transactions

    def _persist_if_configured(self) -> None:
        if self.storage_provider:
            self.storage_provider.save(self.state)

    def buy(
        self,
        asset_id: str,
        quantity: float,
        price_per_unit: Optional[float] = None,
        asset_name: Optional[str] = None,
        asset_type: AssetType = AssetType.STOCK,
        country_code: Optional[str] = None,
    ) -> OrderReceipt:
        """Executes a purchase order with full statutory friction and tax audit."""
        if quantity <= 0:
            return OrderReceipt(
                status=OrderStatus.REJECTED,
                rejection_reason="Order quantity must be positive.",
            )

        active_country = (country_code or self.country_code).upper().strip()
        tax_profile = get_tax_profile(active_country)
        clean_id = asset_id.strip()

        # Resolve asset price and quote currency
        resolved_price = price_per_unit
        resolved_name = asset_name or clean_id
        quote_currency = tax_profile.currency_code

        if resolved_price is None:
            if asset_type == AssetType.STOCK:
                quote = self.yahoo_provider.get_quote(clean_id)
                if not quote:
                    return OrderReceipt(
                        status=OrderStatus.REJECTED,
                        rejection_reason=f"Unable to retrieve quote for stock {clean_id}.",
                    )
                resolved_price = quote.current_price
                resolved_name = quote.name
                quote_currency = quote.currency
            else:
                c_quote = self.coingecko_provider.get_crypto(clean_id)
                if not c_quote:
                    return OrderReceipt(
                        status=OrderStatus.REJECTED,
                        rejection_reason=f"Unable to retrieve quote for crypto {clean_id}.",
                    )
                resolved_price = c_quote.current_price
                resolved_name = c_quote.name
                quote_currency = "EUR"

        if resolved_price <= 0:
            return OrderReceipt(
                status=OrderStatus.REJECTED,
                rejection_reason="Asset price must be positive.",
            )

        # Harmonize execution quote to the user's jurisdiction currency for tax computation
        unit_price_in_user_curr = self.currency_service.convert(
            amount=resolved_price,
            from_currency=quote_currency,
            to_currency=tax_profile.currency_code,
        )

        breakdown = TaxCalculator.calculate_buy_breakdown(
            quantity=quantity,
            price_per_unit=unit_price_in_user_curr,
            is_stock=(asset_type == AssetType.STOCK),
            country_code=active_country,
        )

        # Convert net outlay to internal canonical EUR
        total_cost_eur = self.currency_service.to_eur(
            breakdown.net_amount,
            from_currency=tax_profile.currency_code,
        )
        unit_price_eur = self.currency_service.to_eur(
            unit_price_in_user_curr,
            from_currency=tax_profile.currency_code,
        )

        # Ensure solvency before debiting ledger
        if total_cost_eur > self.state.cash_balance + 1e-4:
            return OrderReceipt(
                asset_id=clean_id,
                asset_name=resolved_name,
                asset_type=asset_type.value,
                side=OrderSide.BUY.value,
                quantity=quantity,
                price_per_unit=unit_price_in_user_curr,
                total_gross_amount=breakdown.gross_amount,
                net_amount=breakdown.net_amount,
                country_code=active_country,
                status=OrderStatus.REJECTED,
                rejection_reason=f"Insufficient funds. Required: {total_cost_eur:.2f} EUR, Available: {self.state.cash_balance:.2f} EUR",
            )

        # Update position and recalculate weighted average cost basis
        lookup_key = clean_id.upper() if asset_type == AssetType.STOCK else clean_id.lower()
        if lookup_key in self.state.positions:
            self.state.positions[lookup_key].add_volume(quantity, unit_price_eur)
        else:
            self.state.positions[lookup_key] = PortfolioPosition(
                asset_id=clean_id,
                asset_name=resolved_name,
                asset_type=asset_type.value,
                quantity=quantity,
                avg_buy_price=unit_price_eur,
                current_price=unit_price_eur,
            )

        # Debit cash reserves
        self.state.cash_balance -= total_cost_eur

        receipt = OrderReceipt(
            id=str(uuid.uuid4()),
            asset_id=clean_id,
            asset_name=resolved_name,
            asset_type=asset_type.value,
            side=OrderSide.BUY.value,
            quantity=quantity,
            price_per_unit=unit_price_in_user_curr,
            total_gross_amount=breakdown.gross_amount,
            broker_fee=breakdown.broker_fee,
            transaction_tax=breakdown.transaction_tax + breakdown.exchange_fee,
            capital_gains_tax=0.0,
            net_amount=breakdown.net_amount,
            country_code=active_country,
            status=OrderStatus.FILLED,
        )

        self.state.transactions.insert(0, receipt)
        self._persist_if_configured()
        return receipt

    def sell(
        self,
        asset_id: str,
        quantity: float,
        price_per_unit: Optional[float] = None,
        asset_type: AssetType = AssetType.STOCK,
        country_code: Optional[str] = None,
    ) -> OrderReceipt:
        """Executes a sale order, calculates capital gains, and credits net proceeds."""
        if quantity <= 0:
            return OrderReceipt(
                status=OrderStatus.REJECTED,
                rejection_reason="Sale quantity must be positive.",
            )

        clean_id = asset_id.strip()
        lookup_key = clean_id.upper() if asset_type == AssetType.STOCK else clean_id.lower()
        position = self.state.positions.get(lookup_key)

        if not position or position.quantity < quantity - 1e-6:
            held = position.quantity if position else 0.0
            return OrderReceipt(
                status=OrderStatus.REJECTED,
                rejection_reason=f"Insufficient position. Held: {held}, Requested sale: {quantity}.",
            )

        active_country = (country_code or self.country_code).upper().strip()
        tax_profile = get_tax_profile(active_country)

        resolved_price = price_per_unit
        quote_currency = tax_profile.currency_code

        if resolved_price is None:
            if asset_type == AssetType.STOCK:
                quote = self.yahoo_provider.get_quote(clean_id)
                if not quote:
                    return OrderReceipt(
                        status=OrderStatus.REJECTED,
                        rejection_reason=f"Unable to retrieve quote for stock {clean_id}.",
                    )
                resolved_price = quote.current_price
                quote_currency = quote.currency
            else:
                c_quote = self.coingecko_provider.get_crypto(clean_id)
                if not c_quote:
                    return OrderReceipt(
                        status=OrderStatus.REJECTED,
                        rejection_reason=f"Unable to retrieve quote for crypto {clean_id}.",
                    )
                resolved_price = c_quote.current_price
                quote_currency = "EUR"

        # Convert execution price and historical cost basis to jurisdiction currency
        unit_price_in_user_curr = self.currency_service.convert(
            amount=resolved_price,
            from_currency=quote_currency,
            to_currency=tax_profile.currency_code,
        )
        avg_cost_in_user_curr = self.currency_service.from_eur(
            position.avg_buy_price,
            to_currency=tax_profile.currency_code,
        )

        breakdown = TaxCalculator.calculate_sell_breakdown(
            quantity=quantity,
            price_per_unit=unit_price_in_user_curr,
            avg_buy_price=avg_cost_in_user_curr,
            is_stock=(asset_type == AssetType.STOCK),
            country_code=active_country,
        )

        # Convert net proceeds to canonical EUR
        net_proceeds_eur = self.currency_service.to_eur(
            breakdown.net_amount,
            from_currency=tax_profile.currency_code,
        )
        exit_price_eur = self.currency_service.to_eur(
            unit_price_in_user_curr,
            from_currency=tax_profile.currency_code,
        )

        # Reduce or liquidate position
        if quantity >= position.quantity - 1e-6:
            del self.state.positions[lookup_key]
        else:
            position.reduce_volume(quantity, exit_price_eur)

        # Credit net cash proceeds
        self.state.cash_balance += net_proceeds_eur

        receipt = OrderReceipt(
            id=str(uuid.uuid4()),
            asset_id=clean_id,
            asset_name=position.asset_name,
            asset_type=asset_type.value,
            side=OrderSide.SELL.value,
            quantity=quantity,
            price_per_unit=unit_price_in_user_curr,
            total_gross_amount=breakdown.gross_amount,
            broker_fee=breakdown.broker_fee,
            transaction_tax=breakdown.transaction_tax + breakdown.exchange_fee,
            capital_gains_tax=breakdown.capital_gains_tax,
            net_amount=breakdown.net_amount,
            country_code=active_country,
            status=OrderStatus.FILLED,
        )

        self.state.transactions.insert(0, receipt)
        self._persist_if_configured()
        return receipt

    def sync_market_prices(self) -> None:
        """Synchronizes spot valuations across all active holdings in the portfolio."""
        stock_symbols = [
            pos.asset_id for pos in self.state.positions.values() if pos.asset_type == "stock"
        ]
        crypto_ids = [
            pos.asset_id for pos in self.state.positions.values() if pos.asset_type == "crypto"
        ]

        if stock_symbols:
            quotes = self.yahoo_provider.get_quotes(stock_symbols)
            for sym, quote in quotes.items():
                pos = self.state.get_position(sym)
                if pos:
                    eur_price = self.currency_service.to_eur(quote.current_price, quote.currency)
                    pos.current_price = eur_price

        for cid in crypto_ids:
            c_quote = self.coingecko_provider.get_crypto(cid)
            if c_quote:
                pos = self.state.get_position(cid)
                if pos:
                    pos.current_price = c_quote.current_price

    def get_statement(self, currency_code: Optional[str] = None) -> Dict:
        """Compiles a complete financial statement converted to the target currency."""
        target_curr = (currency_code or get_tax_profile(self.country_code).currency_code).upper()
        sym = get_tax_profile(self.country_code).currency_symbol

        cash = self.currency_service.from_eur(self.state.cash_balance, target_curr)
        invested = self.currency_service.from_eur(self.state.total_invested, target_curr)
        net_worth = cash + invested
        pl = self.currency_service.from_eur(self.state.total_profit_loss, target_curr)

        holdings_data = []
        for pos in self.state.positions.values():
            holdings_data.append({
                "asset_id": pos.asset_id,
                "name": pos.asset_name,
                "type": pos.asset_type,
                "quantity": pos.quantity,
                "avg_buy_price": self.currency_service.from_eur(pos.avg_buy_price, target_curr),
                "current_price": self.currency_service.from_eur(pos.current_price, target_curr),
                "total_value": self.currency_service.from_eur(pos.total_value, target_curr),
                "profit_loss": self.currency_service.from_eur(pos.profit_loss, target_curr),
                "profit_loss_pct": pos.profit_loss_percent,
            })

        return {
            "currency": target_curr,
            "currency_symbol": sym,
            "cash_balance": cash,
            "invested_value": invested,
            "total_net_worth": net_worth,
            "total_profit_loss": pl,
            "total_profit_loss_pct": self.state.total_profit_loss_percent,
            "holdings": holdings_data,
        }

    def evaluate_performance(self) -> PerformanceMetrics:
        """Calculates risk, drawdown, and efficiency metrics on the portfolio ledger."""
        return AnalyticsEngine.evaluate(self.state)
