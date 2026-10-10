import '../models/tax_profile.dart';

/// Fiscal calculation engine modeling official national tax authorities.
class TaxService {
  static const List<CountryTaxProfile> supportedCountries = [
    CountryTaxProfile(
      code: 'ES',
      name: 'Spain',
      taxAuthority: 'Agencia Tributaria (AEAT / Hacienda)',
      currencyCode: 'EUR',
      currencySymbol: '€',
      currencyDecimals: 2,
      stockTransactionTaxRate: 0.0020,
      cryptoTransactionTaxRate: 0.0,
      capitalGainsTaxRate: 0.19,
      brokerFeeRate: 0.0007,
      minimumBrokerFee: 1.00,
      exchangeFeeRate: 0.0003,
      minimumExchangeFee: 0.50,
      taxName: 'Tobin Tax (ITF Ley 5/2020 0.20%)',
      capitalGainsTaxName: 'IRPF Base del Ahorro (19% to 28%)',
      description: 'AEAT: Progressive savings tax on capital gains plus 0.20% Financial Transaction Tax.',
    ),
    CountryTaxProfile(
      code: 'US',
      name: 'United States',
      taxAuthority: 'Internal Revenue Service (IRS)',
      currencyCode: 'USD',
      currencySymbol: r'$',
      currencyDecimals: 2,
      stockTransactionTaxRate: 0.0,
      cryptoTransactionTaxRate: 0.0,
      capitalGainsTaxRate: 0.15,
      brokerFeeRate: 0.0005,
      minimumBrokerFee: 0.50,
      exchangeFeeRate: 0.0001,
      minimumExchangeFee: 0.20,
      sellRegulatoryFeeRate: 0.0000278,
      taxName: 'SEC Section 31 & FINRA TAF',
      capitalGainsTaxName: 'IRS Capital Gains (15% - 20%)',
      description: 'IRS: Federal capital gains benchmarks and SEC regulatory transaction assessment.',
    ),
    CountryTaxProfile(
      code: 'GB',
      name: 'United Kingdom',
      taxAuthority: 'HM Revenue & Customs (HMRC)',
      currencyCode: 'GBP',
      currencySymbol: '£',
      currencyDecimals: 2,
      stockTransactionTaxRate: 0.0050,
      cryptoTransactionTaxRate: 0.0,
      capitalGainsTaxRate: 0.20,
      brokerFeeRate: 0.0008,
      minimumBrokerFee: 1.00,
      exchangeFeeRate: 0.0002,
      minimumExchangeFee: 0.50,
      taxName: 'HMRC Stamp Duty (SDRT 0.50%)',
      capitalGainsTaxName: 'HMRC Capital Gains Tax (20%)',
      description: 'HMRC: 0.50% Stamp Duty Reserve Tax on UK share purchases with capital gains baselines.',
    ),
    CountryTaxProfile(
      code: 'FR',
      name: 'France',
      taxAuthority: 'Direction Générale des Finances Publiques (DGFiP)',
      currencyCode: 'EUR',
      currencySymbol: '€',
      currencyDecimals: 2,
      stockTransactionTaxRate: 0.0030,
      cryptoTransactionTaxRate: 0.0,
      capitalGainsTaxRate: 0.30,
      brokerFeeRate: 0.0008,
      minimumBrokerFee: 1.00,
      exchangeFeeRate: 0.0002,
      minimumExchangeFee: 0.50,
      taxName: 'DGFiP TTF (0.30%)',
      capitalGainsTaxName: 'Flat Tax PFU (30.0%)',
      description: 'DGFiP: 0.30% Taxe sur les Transactions Financières alongside the 30% single flat tax.',
    ),
    CountryTaxProfile(
      code: 'DE',
      name: 'Germany',
      taxAuthority: 'Bundeszentralamt für Steuern (BZSt)',
      currencyCode: 'EUR',
      currencySymbol: '€',
      currencyDecimals: 2,
      stockTransactionTaxRate: 0.0,
      cryptoTransactionTaxRate: 0.0,
      capitalGainsTaxRate: 0.26375,
      brokerFeeRate: 0.0008,
      minimumBrokerFee: 1.00,
      exchangeFeeRate: 0.0002,
      minimumExchangeFee: 0.50,
      taxName: 'Xetra Trading Fee',
      capitalGainsTaxName: 'Abgeltungsteuer + Soli (26.38%)',
      description: 'BZSt: Flat settlement tax of 25% plus 5.5% solidarity surcharge.',
    ),
    CountryTaxProfile(
      code: 'IT',
      name: 'Italy',
      taxAuthority: 'Agenzia delle Entrate',
      currencyCode: 'EUR',
      currencySymbol: '€',
      currencyDecimals: 2,
      stockTransactionTaxRate: 0.0010,
      cryptoTransactionTaxRate: 0.0,
      capitalGainsTaxRate: 0.26,
      brokerFeeRate: 0.0008,
      minimumBrokerFee: 1.00,
      exchangeFeeRate: 0.0002,
      minimumExchangeFee: 0.50,
      taxName: 'Tobin Tax (0.10%)',
      capitalGainsTaxName: 'Imposta Sostitutiva Plusvalenze (26.0%)',
      description: 'Regulated market transaction tax on equity purchases and 26% substitute tax.',
    ),
    CountryTaxProfile(
      code: 'PT',
      name: 'Portugal',
      taxAuthority: 'Autoridade Tributária e Aduaneira (AT)',
      currencyCode: 'EUR',
      currencySymbol: '€',
      currencyDecimals: 2,
      stockTransactionTaxRate: 0.0,
      cryptoTransactionTaxRate: 0.0,
      capitalGainsTaxRate: 0.28,
      brokerFeeRate: 0.0008,
      minimumBrokerFee: 1.00,
      exchangeFeeRate: 0.0002,
      minimumExchangeFee: 0.50,
      taxName: 'Stamp Duty on Commissions (4%)',
      capitalGainsTaxName: 'IRS Mais-valias (28.0%)',
      description: 'Autonomous 28% capital gains rate under CIRS Art. 72 and stamp duty on commissions.',
    ),
    CountryTaxProfile(
      code: 'SE',
      name: 'Sweden',
      taxAuthority: 'Skatteverket',
      currencyCode: 'SEK',
      currencySymbol: 'kr',
      currencyDecimals: 2,
      stockTransactionTaxRate: 0.0,
      cryptoTransactionTaxRate: 0.0,
      capitalGainsTaxRate: 0.30,
      brokerFeeRate: 0.0009,
      minimumBrokerFee: 1.00,
      exchangeFeeRate: 0.0001,
      minimumExchangeFee: 0.50,
      taxName: 'Courtage & Exchange Fee',
      capitalGainsTaxName: 'Kapitalvinstskatt (30.0%)',
      description: 'Swedish 30% state tax applied to realized capital gains within custody accounts.',
    ),
    CountryTaxProfile(
      code: 'NL',
      name: 'Netherlands',
      taxAuthority: 'Belastingdienst',
      currencyCode: 'EUR',
      currencySymbol: '€',
      currencyDecimals: 2,
      stockTransactionTaxRate: 0.0,
      cryptoTransactionTaxRate: 0.0,
      capitalGainsTaxRate: 0.32,
      brokerFeeRate: 0.0008,
      minimumBrokerFee: 1.00,
      exchangeFeeRate: 0.0002,
      minimumExchangeFee: 0.50,
      taxName: 'Euronext Exchange Cost',
      capitalGainsTaxName: 'Box 3 Rendementsheffing (32.0%)',
      description: 'Dutch wealth yield taxation applied to investment returns under Box 3.',
    ),
    CountryTaxProfile(
      code: 'FI',
      name: 'Finland',
      taxAuthority: 'Verohallinto',
      currencyCode: 'EUR',
      currencySymbol: '€',
      currencyDecimals: 2,
      stockTransactionTaxRate: 0.0,
      cryptoTransactionTaxRate: 0.0,
      capitalGainsTaxRate: 0.30,
      brokerFeeRate: 0.0008,
      minimumBrokerFee: 1.00,
      exchangeFeeRate: 0.0002,
      minimumExchangeFee: 0.50,
      taxName: 'Nasdaq Helsinki Fee',
      capitalGainsTaxName: 'Pääomatulovero (30% to 34%)',
      description: 'Finnish progressive capital income tax: 30% up to €30,000 and 34% on excess.',
    ),
    CountryTaxProfile(
      code: 'CH',
      name: 'Switzerland',
      taxAuthority: 'Eidgenössische Steuerverwaltung (ESTV)',
      currencyCode: 'CHF',
      currencySymbol: 'CHF',
      currencyDecimals: 2,
      stockTransactionTaxRate: 0.0015,
      cryptoTransactionTaxRate: 0.0,
      capitalGainsTaxRate: 0.0,
      brokerFeeRate: 0.0009,
      minimumBrokerFee: 1.50,
      exchangeFeeRate: 0.0001,
      minimumExchangeFee: 0.50,
      taxName: 'Swiss Federal Stamp Duty (0.15%)',
      capitalGainsTaxName: 'Private Capital Gains (Exempt 0%)',
      description: 'Federal turnover duty with private capital gains tax exemption.',
    ),
    CountryTaxProfile(
      code: 'GLOBAL',
      name: 'International Reference',
      taxAuthority: 'International Standards',
      currencyCode: 'USD',
      currencySymbol: r'$',
      currencyDecimals: 2,
      stockTransactionTaxRate: 0.0,
      cryptoTransactionTaxRate: 0.0,
      capitalGainsTaxRate: 0.20,
      brokerFeeRate: 0.0005,
      minimumBrokerFee: 1.00,
      exchangeFeeRate: 0.0001,
      minimumExchangeFee: 0.25,
      taxName: 'Exchange Canon',
      capitalGainsTaxName: 'Baseline Capital Gains (20%)',
      description: 'Default international reference baseline.',
    ),
  ];

  static CountryTaxProfile getProfile(String? countryCode) {
    if (countryCode == null || countryCode.isEmpty) {
      return supportedCountries.firstWhere((c) => c.code == 'GLOBAL');
    }
    return supportedCountries.firstWhere(
      (c) => c.code.toUpperCase() == countryCode.toUpperCase(),
      orElse: () => supportedCountries.firstWhere((c) => c.code == 'GLOBAL'),
    );
  }

  /// Evaluates Spanish progressive savings tax base (Ley 35/2006 de IRPF).
  static double calculateSpanishHaciendaIRPF(double gain) {
    if (gain <= 0) return 0.0;
    if (gain <= 6000.0) {
      return gain * 0.19;
    } else if (gain <= 50000.0) {
      return (6000.0 * 0.19) + ((gain - 6000.0) * 0.21);
    } else if (gain <= 200000.0) {
      return (6000.0 * 0.19) + (44000.0 * 0.21) + ((gain - 50000.0) * 0.23);
    } else if (gain <= 300000.0) {
      return (6000.0 * 0.19) + (44000.0 * 0.21) + (150000.0 * 0.23) + ((gain - 200000.0) * 0.27);
    } else {
      return (6000.0 * 0.19) + (44000.0 * 0.21) + (150000.0 * 0.23) + (100000.0 * 0.27) + ((gain - 300000.0) * 0.28);
    }
  }

  /// Evaluates Finnish two-tier progressive capital income tax.
  static double calculateFinnishCapitalTax(double gain) {
    if (gain <= 0) return 0.0;
    if (gain <= 30000.0) {
      return gain * 0.30;
    } else {
      return (30000.0 * 0.30) + ((gain - 30000.0) * 0.34);
    }
  }

  static double calculateCapitalGainsTax({
    required double realizedProfit,
    required CountryTaxProfile country,
  }) {
    if (realizedProfit <= 0) return 0.0;
    if (country.code == 'ES') {
      return calculateSpanishHaciendaIRPF(realizedProfit);
    }
    if (country.code == 'FI') {
      return calculateFinnishCapitalTax(realizedProfit);
    }
    return realizedProfit * country.capitalGainsTaxRate;
  }

  static TradeTaxBreakdown calculateBuyBreakdown({
    required double quantity,
    required double pricePerUnit,
    required bool isStock,
    String? countryCode,
  }) {
    final country = getProfile(countryCode);
    final grossAmount = quantity * pricePerUnit;

    final calcBroker = grossAmount * country.brokerFeeRate;
    final brokerFee = grossAmount > 0
        ? (calcBroker < country.minimumBrokerFee ? country.minimumBrokerFee : calcBroker)
        : 0.0;

    final calcExchange = grossAmount * country.exchangeFeeRate;
    final exchangeFee = (grossAmount > 0 && country.exchangeFeeRate > 0)
        ? (calcExchange < country.minimumExchangeFee ? country.minimumExchangeFee : calcExchange)
        : 0.0;

    final rate = isStock ? country.stockTransactionTaxRate : country.cryptoTransactionTaxRate;
    final transactionTax = grossAmount * rate;
    final netAmount = grossAmount + brokerFee + exchangeFee + transactionTax;

    return TradeTaxBreakdown(
      grossAmount: grossAmount,
      brokerFee: brokerFee,
      exchangeFee: exchangeFee,
      transactionTax: transactionTax,
      capitalGainsTax: 0.0,
      netAmount: netAmount,
      realizedProfit: 0.0,
      effectiveTaxRateDescription: '0.0%',
      country: country,
    );
  }

  static TradeTaxBreakdown calculateSellBreakdown({
    required double quantity,
    required double pricePerUnit,
    required double avgBuyPrice,
    required bool isStock,
    String? countryCode,
  }) {
    final country = getProfile(countryCode);
    final grossAmount = quantity * pricePerUnit;
    final costBasis = quantity * avgBuyPrice;
    final rawProfit = grossAmount - costBasis;
    final realizedProfit = rawProfit > 0 ? rawProfit : 0.0;

    final calcBroker = grossAmount * country.brokerFeeRate;
    final brokerFee = grossAmount > 0
        ? (calcBroker < country.minimumBrokerFee ? country.minimumBrokerFee : calcBroker)
        : 0.0;

    final calcExchange = grossAmount * country.exchangeFeeRate;
    final exchangeFee = (grossAmount > 0 && country.exchangeFeeRate > 0)
        ? (calcExchange < country.minimumExchangeFee ? country.minimumExchangeFee : calcExchange)
        : 0.0;

    final regulatoryTax = grossAmount * country.sellRegulatoryFeeRate;
    final capitalGainsTax = calculateCapitalGainsTax(realizedProfit: realizedProfit, country: country);

    final netAmount = (grossAmount - brokerFee - exchangeFee - regulatoryTax - capitalGainsTax).clamp(0.0, double.infinity);

    return TradeTaxBreakdown(
      grossAmount: grossAmount,
      brokerFee: brokerFee,
      exchangeFee: exchangeFee,
      transactionTax: regulatoryTax,
      capitalGainsTax: capitalGainsTax,
      netAmount: netAmount,
      realizedProfit: rawProfit,
      effectiveTaxRateDescription: '${(country.capitalGainsTaxRate * 100).toStringAsFixed(1)}%',
      country: country,
    );
  }
}
