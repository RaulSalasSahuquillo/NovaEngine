"""Tax profile definitions and statutory regulatory configurations.

This module models fiscal policies across major financial jurisdictions,
accounting for national transaction taxes (Tobin Tax, SDRT, TTF), exchange canons,
brokerage commission baselines, and statutory capital gains benchmarks.
"""

from dataclasses import dataclass
from typing import Dict, List, Optional


@dataclass(frozen=True)
class CountryTaxProfile:
    """Represents a national tax regime and market friction parameters."""

    code: str
    name: str
    tax_authority: str
    currency_code: str
    currency_symbol: str
    currency_decimals: int
    stock_transaction_tax_rate: float
    crypto_transaction_tax_rate: float
    capital_gains_tax_rate: float
    broker_fee_rate: float
    minimum_broker_fee: float
    exchange_fee_rate: float
    minimum_exchange_fee: float
    sell_regulatory_fee_rate: float
    tax_name: str
    capital_gains_tax_name: str
    description: str

    def format_currency(self, amount: float, decimals: Optional[int] = None) -> str:
        """Formats a numeric monetary value using the jurisdiction symbol."""
        dec = decimals if decimals is not None else self.currency_decimals
        return f"{self.currency_symbol}{amount:,.{dec}f}"


SUPPORTED_TAX_PROFILES: Dict[str, CountryTaxProfile] = {
    "ES": CountryTaxProfile(
        code="ES",
        name="Spain",
        tax_authority="Agencia Tributaria (AEAT / Hacienda)",
        currency_code="EUR",
        currency_symbol="€",
        currency_decimals=2,
        stock_transaction_tax_rate=0.0020,
        crypto_transaction_tax_rate=0.0,
        capital_gains_tax_rate=0.19,
        broker_fee_rate=0.0007,
        minimum_broker_fee=1.00,
        exchange_fee_rate=0.0003,
        minimum_exchange_fee=0.50,
        sell_regulatory_fee_rate=0.0,
        tax_name="Tobin Tax (ITF Ley 5/2020 0.20%)",
        capital_gains_tax_name="IRPF Base del Ahorro (19% to 28%)",
        description="Spanish progressive savings base tax on capital gains plus 0.20% Financial Transaction Tax and BME market canons.",
    ),
    "US": CountryTaxProfile(
        code="US",
        name="United States",
        tax_authority="Internal Revenue Service (IRS)",
        currency_code="USD",
        currency_symbol="$",
        currency_decimals=2,
        stock_transaction_tax_rate=0.0,
        crypto_transaction_tax_rate=0.0,
        capital_gains_tax_rate=0.15,
        broker_fee_rate=0.0005,
        minimum_broker_fee=0.50,
        exchange_fee_rate=0.0001,
        minimum_exchange_fee=0.20,
        sell_regulatory_fee_rate=0.0000278,
        tax_name="SEC Section 31 & FINRA TAF",
        capital_gains_tax_name="IRS Long-Term Capital Gains (15% - 20%)",
        description="Federal capital gains benchmarks along with SEC regulatory sales fee per million traded.",
    ),
    "GB": CountryTaxProfile(
        code="GB",
        name="United Kingdom",
        tax_authority="HM Revenue & Customs (HMRC)",
        currency_code="GBP",
        currency_symbol="£",
        currency_decimals=2,
        stock_transaction_tax_rate=0.0050,
        crypto_transaction_tax_rate=0.0,
        capital_gains_tax_rate=0.20,
        broker_fee_rate=0.0008,
        minimum_broker_fee=1.00,
        exchange_fee_rate=0.0002,
        minimum_exchange_fee=0.50,
        sell_regulatory_fee_rate=0.0,
        tax_name="HMRC Stamp Duty (SDRT 0.50%)",
        capital_gains_tax_name="HMRC Capital Gains Tax (20%)",
        description="Statutory 0.50% Stamp Duty Reserve Tax levied on UK equity purchases with higher-rate capital gains benchmarks.",
    ),
    "FR": CountryTaxProfile(
        code="FR",
        name="France",
        tax_authority="Direction Générale des Finances Publiques (DGFiP)",
        currency_code="EUR",
        currency_symbol="€",
        currency_decimals=2,
        stock_transaction_tax_rate=0.0030,
        crypto_transaction_tax_rate=0.0,
        capital_gains_tax_rate=0.30,
        broker_fee_rate=0.0008,
        minimum_broker_fee=1.00,
        exchange_fee_rate=0.0002,
        minimum_exchange_fee=0.50,
        sell_regulatory_fee_rate=0.0,
        tax_name="DGFiP TTF (0.30%)",
        capital_gains_tax_name="Flat Tax PFU (30.0%)",
        description="French 0.30% Taxe sur les Transactions Financieres alongside the 30% single flat withholding tax.",
    ),
    "DE": CountryTaxProfile(
        code="DE",
        name="Germany",
        tax_authority="Bundeszentralamt für Steuern (BZSt)",
        currency_code="EUR",
        currency_symbol="€",
        currency_decimals=2,
        stock_transaction_tax_rate=0.0,
        crypto_transaction_tax_rate=0.0,
        capital_gains_tax_rate=0.26375,
        broker_fee_rate=0.0008,
        minimum_broker_fee=1.00,
        exchange_fee_rate=0.0002,
        minimum_exchange_fee=0.50,
        sell_regulatory_fee_rate=0.0,
        tax_name="Xetra Trading Fee",
        capital_gains_tax_name="Abgeltungsteuer + Soli (26.38%)",
        description="German flat settlement withholding tax of 25% combined with the mandatory 5.5% solidarity surcharge.",
    ),
    "IT": CountryTaxProfile(
        code="IT",
        name="Italy",
        tax_authority="Agenzia delle Entrate",
        currency_code="EUR",
        currency_symbol="€",
        currency_decimals=2,
        stock_transaction_tax_rate=0.0010,
        crypto_transaction_tax_rate=0.0,
        capital_gains_tax_rate=0.26,
        broker_fee_rate=0.0008,
        minimum_broker_fee=1.00,
        exchange_fee_rate=0.0002,
        minimum_exchange_fee=0.50,
        sell_regulatory_fee_rate=0.0,
        tax_name="Italian Tobin Tax (0.10%)",
        capital_gains_tax_name="Imposta Sostitutiva Plusvalenze (26.0%)",
        description="Regulated market transaction tax on equity purchases combined with substitute tax on net gains.",
    ),
    "PT": CountryTaxProfile(
        code="PT",
        name="Portugal",
        tax_authority="Autoridade Tributaria e Aduaneira (AT)",
        currency_code="EUR",
        currency_symbol="€",
        currency_decimals=2,
        stock_transaction_tax_rate=0.0,
        crypto_transaction_tax_rate=0.0,
        capital_gains_tax_rate=0.28,
        broker_fee_rate=0.0008,
        minimum_broker_fee=1.00,
        exchange_fee_rate=0.0002,
        minimum_exchange_fee=0.50,
        sell_regulatory_fee_rate=0.0,
        tax_name="Stamp Duty on Commissions (4%)",
        capital_gains_tax_name="IRS Mais-valias (28.0%)",
        description="Autonomous 28% capital gains rate under CIRS Art. 72 and stamp duty levied on financial brokerage fees.",
    ),
    "SE": CountryTaxProfile(
        code="SE",
        name="Sweden",
        tax_authority="Skatteverket",
        currency_code="SEK",
        currency_symbol="kr",
        currency_decimals=2,
        stock_transaction_tax_rate=0.0,
        crypto_transaction_tax_rate=0.0,
        capital_gains_tax_rate=0.30,
        broker_fee_rate=0.0009,
        minimum_broker_fee=1.00,
        exchange_fee_rate=0.0001,
        minimum_exchange_fee=0.50,
        sell_regulatory_fee_rate=0.0,
        tax_name="Courtage & Exchange Fee",
        capital_gains_tax_name="Kapitalvinstskatt (30.0%)",
        description="Swedish 30% state tax applied to realized capital gains within conventional custody accounts.",
    ),
    "NL": CountryTaxProfile(
        code="NL",
        name="Netherlands",
        tax_authority="Belastingdienst",
        currency_code="EUR",
        currency_symbol="€",
        currency_decimals=2,
        stock_transaction_tax_rate=0.0,
        crypto_transaction_tax_rate=0.0,
        capital_gains_tax_rate=0.32,
        broker_fee_rate=0.0008,
        minimum_broker_fee=1.00,
        exchange_fee_rate=0.0002,
        minimum_exchange_fee=0.50,
        sell_regulatory_fee_rate=0.0,
        tax_name="Euronext Exchange Cost",
        capital_gains_tax_name="Box 3 Rendementsheffing (32.0%)",
        description="Dutch wealth yield taxation regime applied to recognized investment returns under Box 3.",
    ),
    "FI": CountryTaxProfile(
        code="FI",
        name="Finland",
        tax_authority="Verohallinto",
        currency_code="EUR",
        currency_symbol="€",
        currency_decimals=2,
        stock_transaction_tax_rate=0.0,
        crypto_transaction_tax_rate=0.0,
        capital_gains_tax_rate=0.30,
        broker_fee_rate=0.0008,
        minimum_broker_fee=1.00,
        exchange_fee_rate=0.0002,
        minimum_exchange_fee=0.50,
        sell_regulatory_fee_rate=0.0,
        tax_name="Nasdaq Helsinki Fee",
        capital_gains_tax_name="Pääomatulovero (30% to 34%)",
        description="Finnish two-tier capital income tax: 30% up to EUR 30,000 and 34% on the excess portion.",
    ),
    "CH": CountryTaxProfile(
        code="CH",
        name="Switzerland",
        tax_authority="Eidgenössische Steuerverwaltung (ESTV)",
        currency_code="CHF",
        currency_symbol="CHF",
        currency_decimals=2,
        stock_transaction_tax_rate=0.0015,
        crypto_transaction_tax_rate=0.0,
        capital_gains_tax_rate=0.0,
        broker_fee_rate=0.0009,
        minimum_broker_fee=1.50,
        exchange_fee_rate=0.0001,
        minimum_exchange_fee=0.50,
        sell_regulatory_fee_rate=0.0,
        tax_name="Swiss Federal Stamp Duty (0.15%)",
        capital_gains_tax_name="Private Capital Gains (Tax-Exempt 0%)",
        description="Federal stamp duty on turnover for domestic securities with private capital gains tax exemption for non-professional investors.",
    ),
    "GLOBAL": CountryTaxProfile(
        code="GLOBAL",
        name="International Benchmark",
        tax_authority="Standard International Guidelines",
        currency_code="USD",
        currency_symbol="$",
        currency_decimals=2,
        stock_transaction_tax_rate=0.0,
        crypto_transaction_tax_rate=0.0,
        capital_gains_tax_rate=0.20,
        broker_fee_rate=0.0005,
        minimum_broker_fee=1.00,
        exchange_fee_rate=0.0001,
        minimum_exchange_fee=0.25,
        sell_regulatory_fee_rate=0.0,
        tax_name="Standard Exchange Fee",
        capital_gains_tax_name="Standard Capital Gains Benchmark (20.0%)",
        description="Standard global reference baseline for unmapped countries and international modeling.",
    ),
}


def get_tax_profile(country_code: Optional[str]) -> CountryTaxProfile:
    """Resolves a tax profile by ISO code, falling back to the global profile."""
    if not country_code:
        return SUPPORTED_TAX_PROFILES["GLOBAL"]
    return SUPPORTED_TAX_PROFILES.get(country_code.upper().strip(), SUPPORTED_TAX_PROFILES["GLOBAL"])
