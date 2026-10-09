"""Fiscal calculation engine and trade cost breakdown auditor.

Computes statutory capital gains taxes according to progressive bracket schedules
(including Spanish IRPF Base del Ahorro and Finnish Verohallinto brackets),
alongside transaction levies (Tobin Tax, SDRT, TTF, SEC Section 31 fees) and
brokerage commission minimums.
"""

from dataclasses import dataclass
from typing import Optional

from novaengine.tax.profile import CountryTaxProfile, get_tax_profile


@dataclass(frozen=True)
class TradeTaxBreakdown:
    """Financial breakdown of costs, fees, taxes, and proceeds for a trade."""

    gross_amount: float
    broker_fee: float
    exchange_fee: float
    transaction_tax: float
    capital_gains_tax: float
    net_amount: float
    realized_profit: float
    effective_tax_rate_description: str
    country: CountryTaxProfile

    @property
    def total_fees_and_taxes(self) -> float:
        """Total friction cost deducted from or added to the transaction."""
        return self.broker_fee + self.exchange_fee + self.transaction_tax + self.capital_gains_tax


class TaxCalculator:
    """Evaluates regulatory taxes and exchange friction across jurisdictions."""

    @staticmethod
    def calculate_spanish_hacienda_irpf(gain: float) -> float:
        """Calculates progressive capital gains tax under Spanish Ley 35/2006.

        Statutory brackets applied to the savings tax base:
        Up to €6,000: 19%
        From €6,000 to €50,000: 21%
        From €50,000 to €200,000: 23%
        From €200,000 to €300,000: 27%
        Above €300,000: 28%
        """
        if gain <= 0.0:
            return 0.0

        if gain <= 6000.0:
            return gain * 0.19
        if gain <= 50000.0:
            return (6000.0 * 0.19) + ((gain - 6000.0) * 0.21)
        if gain <= 200000.0:
            return (6000.0 * 0.19) + (44000.0 * 0.21) + ((gain - 50000.0) * 0.23)
        if gain <= 300000.0:
            return (
                (6000.0 * 0.19)
                + (44000.0 * 0.21)
                + (150000.0 * 0.23)
                + ((gain - 200000.0) * 0.27)
            )

        return (
            (6000.0 * 0.19)
            + (44000.0 * 0.21)
            + (150000.0 * 0.23)
            + (100000.0 * 0.27)
            + ((gain - 300000.0) * 0.28)
        )

    @staticmethod
    def calculate_finnish_capital_tax(gain: float) -> float:
        """Calculates progressive capital gains tax under Finnish Verohallinto rules.

        Statutory brackets:
        Up to €30,000: 30%
        Excess above €30,000: 34%
        """
        if gain <= 0.0:
            return 0.0
        if gain <= 30000.0:
            return gain * 0.30
        return (30000.0 * 0.30) + ((gain - 30000.0) * 0.34)

    @classmethod
    def calculate_capital_gains_tax(cls, realized_profit: float, country: CountryTaxProfile) -> float:
        """Determines the tax liability on a positive realized gain."""
        if realized_profit <= 0.0:
            return 0.0

        if country.code == "ES":
            return cls.calculate_spanish_hacienda_irpf(realized_profit)
        if country.code == "FI":
            return cls.calculate_finnish_capital_tax(realized_profit)

        return realized_profit * country.capital_gains_tax_rate

    @classmethod
    def get_effective_tax_description(cls, realized_profit: float, country: CountryTaxProfile) -> str:
        """Produces a human-readable summary of the effective tax rate applied."""
        if realized_profit <= 0.0:
            return "0.0%"

        if country.code == "ES":
            tax = cls.calculate_spanish_hacienda_irpf(realized_profit)
            effective = (tax / realized_profit) * 100.0
            return f"{effective:.1f}% (Progressive IRPF AEAT)"
        if country.code == "FI":
            tax = cls.calculate_finnish_capital_tax(realized_profit)
            effective = (tax / realized_profit) * 100.0
            return f"{effective:.1f}% (Verohallinto)"

        return f"{(country.capital_gains_tax_rate * 100.0):.1f}%"

    @classmethod
    def calculate_buy_breakdown(
        cls,
        quantity: float,
        price_per_unit: float,
        is_stock: bool,
        country_code: Optional[str] = None,
    ) -> TradeTaxBreakdown:
        """Computes all friction costs and the total cash outlay required for a purchase."""
        country = get_tax_profile(country_code)
        gross_amount = quantity * price_per_unit

        # Broker commission with statutory minimum floor
        calc_broker = gross_amount * country.broker_fee_rate
        broker_fee = (
            max(country.minimum_broker_fee, calc_broker) if gross_amount > 0.0 else 0.0
        )

        # Exchange execution canon with minimum floor
        calc_exchange = gross_amount * country.exchange_fee_rate
        exchange_fee = (
            max(country.minimum_exchange_fee, calc_exchange)
            if (gross_amount > 0.0 and country.exchange_fee_rate > 0.0)
            else 0.0
        )

        # Transaction tax applied on gross purchase amount (e.g. Spanish Tobin, UK SDRT, French TTF)
        rate = country.stock_transaction_tax_rate if is_stock else country.crypto_transaction_tax_rate
        transaction_tax = gross_amount * rate

        # Total capital required to settle the position
        net_amount = gross_amount + broker_fee + exchange_fee + transaction_tax

        return TradeTaxBreakdown(
            gross_amount=gross_amount,
            broker_fee=broker_fee,
            exchange_fee=exchange_fee,
            transaction_tax=transaction_tax,
            capital_gains_tax=0.0,
            net_amount=net_amount,
            realized_profit=0.0,
            effective_tax_rate_description="0.0%",
            country=country,
        )

    @classmethod
    def calculate_sell_breakdown(
        cls,
        quantity: float,
        price_per_unit: float,
        avg_buy_price: float,
        is_stock: bool,
        country_code: Optional[str] = None,
    ) -> TradeTaxBreakdown:
        """Computes net proceeds realized upon position liquidation, withholding taxes where required."""
        country = get_tax_profile(country_code)
        gross_amount = quantity * price_per_unit
        cost_basis = quantity * avg_buy_price
        raw_profit = gross_amount - cost_basis
        realized_profit = max(0.0, raw_profit)

        # Broker commission on sale
        calc_broker = gross_amount * country.broker_fee_rate
        broker_fee = (
            max(country.minimum_broker_fee, calc_broker) if gross_amount > 0.0 else 0.0
        )

        # Exchange settlement fee
        calc_exchange = gross_amount * country.exchange_fee_rate
        exchange_fee = (
            max(country.minimum_exchange_fee, calc_exchange)
            if (gross_amount > 0.0 and country.exchange_fee_rate > 0.0)
            else 0.0
        )

        # Regulatory sales transaction fee (such as US SEC Section 31 assessment)
        regulatory_tax = gross_amount * country.sell_regulatory_fee_rate

        # Statutory capital gains tax withholding on positive gains
        capital_gains_tax = cls.calculate_capital_gains_tax(realized_profit, country)
        tax_desc = cls.get_effective_tax_description(realized_profit, country)

        # Net cash proceeds credited to the portfolio account
        net_proceeds = max(
            0.0,
            gross_amount - broker_fee - exchange_fee - regulatory_tax - capital_gains_tax,
        )

        return TradeTaxBreakdown(
            gross_amount=gross_amount,
            broker_fee=broker_fee,
            exchange_fee=exchange_fee,
            transaction_tax=regulatory_tax,
            capital_gains_tax=capital_gains_tax,
            net_amount=net_proceeds,
            realized_profit=raw_profit,
            effective_tax_rate_description=tax_desc,
            country=country,
        )
