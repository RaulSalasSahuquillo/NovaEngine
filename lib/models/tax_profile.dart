import 'package:intl/intl.dart';

/// Represents statutory tax rules and exchange friction for a specific jurisdiction.
class CountryTaxProfile {
  final String code;
  final String name;
  final String taxAuthority;
  final String currencyCode;
  final String currencySymbol;
  final int currencyDecimals;
  final double stockTransactionTaxRate;
  final double cryptoTransactionTaxRate;
  final double capitalGainsTaxRate;
  final double brokerFeeRate;
  final double minimumBrokerFee;
  final double exchangeFeeRate;
  final double minimumExchangeFee;
  final double sellRegulatoryFeeRate;
  final String taxName;
  final String capitalGainsTaxName;
  final String description;

  const CountryTaxProfile({
    required this.code,
    required this.name,
    required this.taxAuthority,
    this.currencyCode = 'EUR',
    this.currencySymbol = '€',
    this.currencyDecimals = 2,
    required this.stockTransactionTaxRate,
    this.cryptoTransactionTaxRate = 0.0,
    required this.capitalGainsTaxRate,
    this.brokerFeeRate = 0.0007,
    this.minimumBrokerFee = 1.00,
    this.exchangeFeeRate = 0.0,
    this.minimumExchangeFee = 0.0,
    this.sellRegulatoryFeeRate = 0.0,
    required this.taxName,
    required this.capitalGainsTaxName,
    required this.description,
  });

  String formatCurrency(num amount, {int? decimals}) {
    return NumberFormat.currency(
      symbol: currencySymbol,
      decimalDigits: decimals ?? currencyDecimals,
    ).format(amount);
  }
}

/// Detailed financial breakdown of a buy or sell trade.
class TradeTaxBreakdown {
  final double grossAmount;
  final double brokerFee;
  final double exchangeFee;
  final double transactionTax;
  final double capitalGainsTax;
  final double netAmount;
  final double realizedProfit;
  final String effectiveTaxRateDescription;
  final CountryTaxProfile country;

  const TradeTaxBreakdown({
    required this.grossAmount,
    required this.brokerFee,
    required this.exchangeFee,
    required this.transactionTax,
    required this.capitalGainsTax,
    required this.netAmount,
    required this.realizedProfit,
    required this.effectiveTaxRateDescription,
    required this.country,
  });

  double get totalFeesAndTaxes =>
      brokerFee + exchangeFee + transactionTax + capitalGainsTax;
}
