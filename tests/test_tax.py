"""Unit tests for multi-jurisdiction tax calculations and statutory trade breakdowns."""

from novaengine.tax.calculator import TaxCalculator
from novaengine.tax.profile import get_tax_profile


def test_spanish_hacienda_irpf_brackets():
    # Negative or zero gain produces zero tax
    assert TaxCalculator.calculate_spanish_hacienda_irpf(0.0) == 0.0
    assert TaxCalculator.calculate_spanish_hacienda_irpf(-500.0) == 0.0

    # Bracket 1: Up to €6,000 at 19%
    assert TaxCalculator.calculate_spanish_hacienda_irpf(6000.0) == 1140.0

    # Bracket 2: €10,000 (€6,000 @ 19% + €4,000 @ 21%)
    assert TaxCalculator.calculate_spanish_hacienda_irpf(10000.0) == 1140.0 + 840.0

    # Bracket 3: €100,000 (€6,000 @ 19% + €44,000 @ 21% + €50,000 @ 23%)
    expected_100k = (6000 * 0.19) + (44000 * 0.21) + (50000 * 0.23)
    assert TaxCalculator.calculate_spanish_hacienda_irpf(100000.0) == expected_100k

    # Bracket 5: > €300,000
    expected_400k = (
        (6000 * 0.19)
        + (44000 * 0.21)
        + (150000 * 0.23)
        + (100000 * 0.27)
        + (100000 * 0.28)
    )
    assert TaxCalculator.calculate_spanish_hacienda_irpf(400000.0) == expected_400k


def test_buy_breakdown_with_tobin_tax():
    # Buy €10,000 of stock in Spain (ES)
    breakdown = TaxCalculator.calculate_buy_breakdown(
        quantity=100.0,
        price_per_unit=100.0,
        is_stock=True,
        country_code="ES",
    )

    assert breakdown.gross_amount == 10000.0
    # Broker commission: 0.07% of €10,000 = €7.00
    assert breakdown.broker_fee == 7.00
    # Exchange canon: 0.03% of €10,000 = €3.00
    assert breakdown.exchange_fee == 3.00
    # Spanish Tobin Tax: 0.20% of €10,000 = €20.00
    assert breakdown.transaction_tax == 20.00
    # Net cost should sum all friction components
    assert breakdown.net_amount == 10000.0 + 7.00 + 3.00 + 20.00


def test_sell_breakdown_with_capital_gains():
    # Sell 50 shares bought at €100 for €150 (Gain = €2,500)
    breakdown = TaxCalculator.calculate_sell_breakdown(
        quantity=50.0,
        price_per_unit=150.0,
        avg_buy_price=100.0,
        is_stock=True,
        country_code="ES",
    )

    assert breakdown.gross_amount == 7500.0
    assert breakdown.realized_profit == 2500.0
    # Spanish IRPF on €2,500 is 19% = €475.00
    assert breakdown.capital_gains_tax == 475.00
    # Broker fee on €7,500 at 0.07% is €5.25
    assert breakdown.broker_fee == 5.25
    # Exchange canon on €7,500 at 0.03% is €2.25
    assert breakdown.exchange_fee == 2.25
    # Net proceeds received after friction deductions
    expected_net = 7500.0 - 5.25 - 2.25 - 0.0 - 475.00
    assert breakdown.net_amount == expected_net


def test_minimum_broker_fee_enforcement():
    # Small trade of €100 where 0.07% would be €0.07, so the minimum €1.00 fee applies
    breakdown = TaxCalculator.calculate_buy_breakdown(
        quantity=1.0,
        price_per_unit=100.0,
        is_stock=True,
        country_code="ES",
    )
    profile = get_tax_profile("ES")
    assert breakdown.broker_fee == profile.minimum_broker_fee
