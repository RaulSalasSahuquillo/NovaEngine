"""Command-line interface for headless execution and portfolio inspection.

Allows developers and automated trading pipelines to interact directly with
NovaEngine without graphical dependencies.
"""

import argparse
import sys

try:
    from tabulate import tabulate
except ImportError:
    def tabulate(rows, headers=None, tablefmt=None):
        """Fallback table formatter when tabulate is not installed."""
        all_rows = []
        if headers:
            all_rows.append([str(h) for h in headers])
        for r in rows:
            all_rows.append([str(c) for c in r])
        if not all_rows:
            return ""
        col_widths = [max(len(row[i]) for row in all_rows) for i in range(len(all_rows[0]))]
        lines = []
        if headers:
            header_line = " | ".join(h.ljust(col_widths[i]) for i, h in enumerate(all_rows[0]))
            sep_line = "-+-".join("-" * col_widths[i] for i in range(len(col_widths)))
            lines.append(header_line)
            lines.append(sep_line)
            data_rows = all_rows[1:]
        else:
            data_rows = all_rows
        for row in data_rows:
            lines.append(" | ".join(cell.ljust(col_widths[i]) for i, cell in enumerate(row)))
        return "\n".join(lines)

from novaengine.core.engine import NovaEngine
from novaengine.core.orders import AssetType, OrderStatus
from novaengine.market.currency import default_currency_service
from novaengine.storage.json_store import JsonStorageProvider
from novaengine.tax.profile import SUPPORTED_TAX_PROFILES, get_tax_profile


def _get_engine(country_code: str = "ES", store_file: str = "portfolio_state.json") -> NovaEngine:
    storage = JsonStorageProvider(store_file)
    return NovaEngine(country_code=country_code, storage_provider=storage)


def cmd_quote(args: argparse.Namespace) -> None:
    """Fetches and displays a stock or ETF quote."""
    engine = _get_engine(args.country)
    quote = engine.yahoo_provider.get_quote(args.symbol)
    if not quote:
        print(f"Error: Unable to locate quote for symbol '{args.symbol}'.")
        sys.exit(1)

    table = [
        ["Symbol", quote.symbol],
        ["Name", quote.name],
        ["Price", f"{quote.current_price:.2f} {quote.currency}"],
        ["Change", f"{quote.change:+.2f} ({quote.change_percent:+.2f}%)"],
        ["Day Range", f"{quote.low:.2f} - {quote.high:.2f}"],
        ["Previous Close", f"{quote.previous_close:.2f} {quote.currency}"],
    ]
    print(tabulate(table, headers=["Metric", "Value"], tablefmt="rounded_grid"))


def cmd_crypto(args: argparse.Namespace) -> None:
    """Fetches and displays cryptocurrency market data."""
    engine = _get_engine(args.country)
    quote = engine.coingecko_provider.get_crypto(args.coin_id)
    if not quote:
        print(f"Error: Unable to locate cryptocurrency '{args.coin_id}'.")
        sys.exit(1)

    table = [
        ["Asset", f"{quote.name} ({quote.symbol})"],
        ["Market Rank", f"#{quote.market_cap_rank}"],
        ["Spot Price", f"€{quote.current_price:,.2f}"],
        ["24h Change", f"{quote.change_percent_24h:+.2f}%"],
        ["Market Cap", f"€{quote.market_cap:,.0f}"],
        ["24h Volume", f"€{quote.volume_24h:,.0f}"],
    ]
    print(tabulate(table, headers=["Metric", "Value"], tablefmt="rounded_grid"))


def cmd_buy(args: argparse.Namespace) -> None:
    """Executes a simulated buy order with full tax audit."""
    engine = _get_engine(args.country)
    asset_type = AssetType.CRYPTO if args.crypto else AssetType.STOCK

    receipt = engine.buy(
        asset_id=args.asset,
        quantity=args.quantity,
        price_per_unit=args.price,
        asset_type=asset_type,
        country_code=args.country,
    )

    if receipt.status == OrderStatus.REJECTED:
        print(f"Execution Rejected: {receipt.rejection_reason}")
        sys.exit(1)

    tax_profile = get_tax_profile(args.country)
    print("\nOrder Executed Successfully")
    table = [
        ["Receipt ID", receipt.id],
        ["Asset", f"{receipt.asset_name} ({receipt.asset_id})"],
        ["Side", receipt.side.upper()],
        ["Quantity", f"{receipt.quantity:.4f}"],
        ["Unit Price", f"{tax_profile.currency_symbol}{receipt.price_per_unit:.2f}"],
        ["Gross Outlay", f"{tax_profile.currency_symbol}{receipt.total_gross_amount:.2f}"],
        ["Broker Commission", f"{tax_profile.currency_symbol}{receipt.broker_fee:.2f}"],
        ["Transaction Tax / Canons", f"{tax_profile.currency_symbol}{receipt.transaction_tax:.2f}"],
        ["Total Settled Outlay", f"{tax_profile.currency_symbol}{receipt.net_amount:.2f}"],
        ["Cash Remaining", f"€{engine.cash_balance:,.2f}"],
    ]
    print(tabulate(table, headers=["Audit Field", "Value"], tablefmt="rounded_grid"))


def cmd_sell(args: argparse.Namespace) -> None:
    """Executes a simulated sell order with capital gains withholding."""
    engine = _get_engine(args.country)
    asset_type = AssetType.CRYPTO if args.crypto else AssetType.STOCK

    receipt = engine.sell(
        asset_id=args.asset,
        quantity=args.quantity,
        price_per_unit=args.price,
        asset_type=asset_type,
        country_code=args.country,
    )

    if receipt.status == OrderStatus.REJECTED:
        print(f"Execution Rejected: {receipt.rejection_reason}")
        sys.exit(1)

    tax_profile = get_tax_profile(args.country)
    print("\nOrder Executed Successfully")
    table = [
        ["Receipt ID", receipt.id],
        ["Asset", f"{receipt.asset_name} ({receipt.asset_id})"],
        ["Side", receipt.side.upper()],
        ["Quantity Sold", f"{receipt.quantity:.4f}"],
        ["Execution Price", f"{tax_profile.currency_symbol}{receipt.price_per_unit:.2f}"],
        ["Gross Proceeds", f"{tax_profile.currency_symbol}{receipt.total_gross_amount:.2f}"],
        ["Broker Commission", f"{tax_profile.currency_symbol}{receipt.broker_fee:.2f}"],
        ["Capital Gains Tax Withheld", f"{tax_profile.currency_symbol}{receipt.capital_gains_tax:.2f}"],
        ["Net Cash Credited", f"{tax_profile.currency_symbol}{receipt.net_amount:.2f}"],
        ["Updated Cash Balance", f"€{engine.cash_balance:,.2f}"],
    ]
    print(tabulate(table, headers=["Audit Field", "Value"], tablefmt="rounded_grid"))


def cmd_statement(args: argparse.Namespace) -> None:
    """Prints a financial portfolio statement."""
    engine = _get_engine(args.country)
    statement = engine.get_statement(args.currency)

    sym = statement["currency_symbol"]
    summary_table = [
        ["Cash Balance", f"{sym}{statement['cash_balance']:,.2f}"],
        ["Invested Assets", f"{sym}{statement['invested_value']:,.2f}"],
        ["Total Net Worth", f"{sym}{statement['total_net_worth']:,.2f}"],
        ["Total Profit / Loss", f"{sym}{statement['total_profit_loss']:+,.2f} ({statement['total_profit_loss_pct']:+.2f}%)"],
    ]

    print("\nAccount Valuation Summary")
    print(tabulate(summary_table, headers=["Metric", "Amount"], tablefmt="rounded_grid"))

    holdings = statement["holdings"]
    if holdings:
        h_table = []
        for h in holdings:
            h_table.append([
                h["asset_id"],
                h["name"],
                h["type"].upper(),
                f"{h['quantity']:.4f}",
                f"{sym}{h['avg_buy_price']:.2f}",
                f"{sym}{h['current_price']:.2f}",
                f"{sym}{h['total_value']:.2f}",
                f"{sym}{h['profit_loss']:+.2f} ({h['profit_loss_pct']:+.2f}%)",
            ])
        print("\nOpen Positions")
        print(tabulate(h_table, headers=["Symbol", "Name", "Type", "Qty", "Avg Cost", "Current", "Valuation", "Unrealized P&L"], tablefmt="rounded_grid"))
    else:
        print("\nNo open positions in ledger.")


def cmd_taxes(args: argparse.Namespace) -> None:
    """Lists fiscal parameters for supported jurisdictions."""
    rows = []
    for code, p in SUPPORTED_TAX_PROFILES.items():
        rows.append([
            p.code,
            p.name,
            p.currency_code,
            f"{p.stock_transaction_tax_rate * 100:.2f}%",
            f"{p.capital_gains_tax_rate * 100:.2f}%",
            f"{p.broker_fee_rate * 100:.2f}% (min {p.currency_symbol}{p.minimum_broker_fee:.2f})",
            p.tax_authority,
        ])
    print("\nSupported National Tax Regimes")
    print(tabulate(rows, headers=["ISO", "Country", "Currency", "Transaction Tax", "Baseline CGT", "Broker Rate", "Authority"], tablefmt="rounded_grid"))


def main() -> None:
    """Entry point for the NovaEngine CLI."""
    parser = argparse.ArgumentParser(description="NovaEngine: Headless Quantitative Trading and Tax Auditing Core")
    subparsers = parser.add_subparsers(dest="command", required=True)

    # quote
    p_quote = subparsers.add_parser("quote", help="Lookup a stock or ETF quote")
    p_quote.add_argument("symbol", help="Ticker symbol (e.g. AAPL, SAN.MC)")
    p_quote.add_argument("--country", default="ES", help="Country tax profile code (default: ES)")
    p_quote.set_defaults(func=cmd_quote)

    # crypto
    p_crypto = subparsers.add_parser("crypto", help="Lookup a cryptocurrency quote")
    p_crypto.add_argument("coin_id", help="Coin ID (e.g. bitcoin, ethereum, solana)")
    p_crypto.add_argument("--country", default="ES", help="Country tax profile code (default: ES)")
    p_crypto.set_defaults(func=cmd_crypto)

    # buy
    p_buy = subparsers.add_parser("buy", help="Execute a simulated buy order")
    p_buy.add_argument("asset", help="Asset ticker or coin identifier")
    p_buy.add_argument("quantity", type=float, help="Number of shares or coins")
    p_buy.add_argument("--price", type=float, default=None, help="Explicit unit price (optional)")
    p_buy.add_argument("--crypto", action="store_true", help="Flag indicating asset is crypto")
    p_buy.add_argument("--country", default="ES", help="Country tax code (default: ES)")
    p_buy.set_defaults(func=cmd_buy)

    # sell
    p_sell = subparsers.add_parser("sell", help="Execute a simulated sell order")
    p_sell.add_argument("asset", help="Asset ticker or coin identifier")
    p_sell.add_argument("quantity", type=float, help="Number of shares or coins")
    p_sell.add_argument("--price", type=float, default=None, help="Explicit unit price (optional)")
    p_sell.add_argument("--crypto", action="store_true", help="Flag indicating asset is crypto")
    p_sell.add_argument("--country", default="ES", help="Country tax code (default: ES)")
    p_sell.set_defaults(func=cmd_sell)

    # statement
    p_stmt = subparsers.add_parser("statement", help="Print account valuation and open holdings")
    p_stmt.add_argument("--country", default="ES", help="Country profile code (default: ES)")
    p_stmt.add_argument("--currency", default=None, help="Display currency override (e.g. EUR, USD, GBP)")
    p_stmt.set_defaults(func=cmd_statement)

    # taxes
    p_taxes = subparsers.add_parser("taxes", help="Display statutory tax regimes and fees")
    p_taxes.set_defaults(func=cmd_taxes)

    parsed = parser.parse_args()
    parsed.func(parsed)


if __name__ == "__main__":
    main()
