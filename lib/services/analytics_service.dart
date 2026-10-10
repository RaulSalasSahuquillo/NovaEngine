import '../models/transaction.dart';

/// Summary performance and risk metrics evaluated across the transaction ledger.
class PerformanceMetrics {
  final double totalReturnPercent;
  final double netProfitLoss;
  final int totalTrades;
  final int winningTrades;
  final int losingTrades;
  final double winRatePercent;
  final double profitFactor;
  final double totalFeesPaid;
  final double totalTaxesWithheld;
  final double maxDrawdownPercent;

  const PerformanceMetrics({
    required this.totalReturnPercent,
    required this.netProfitLoss,
    required this.totalTrades,
    required this.winningTrades,
    required this.losingTrades,
    required this.winRatePercent,
    required this.profitFactor,
    required this.totalFeesPaid,
    required this.totalTaxesWithheld,
    required this.maxDrawdownPercent,
  });
}

/// Evaluates quantitative returns and statutory friction over the portfolio state.
class AnalyticsService {
  static PerformanceMetrics evaluate({
    required double netWorth,
    required double initialCapital,
    required List<Transaction> transactions,
  }) {
    final netPl = netWorth - initialCapital;
    final totalReturnPct = initialCapital > 0 ? (netPl / initialCapital) * 100.0 : 0.0;

    int winning = 0;
    int losing = 0;
    double grossGains = 0.0;
    double grossLosses = 0.0;
    double totalFees = 0.0;
    double totalTaxes = 0.0;

    for (final tx in transactions) {
      totalFees += tx.brokerFee;
      totalTaxes += (tx.transactionTax + tx.capitalGainsTax);

      if (tx.isSell) {
        final gain = tx.netAmount - tx.totalAmount;
        if (tx.capitalGainsTax > 0 || gain >= 0) {
          winning++;
          grossGains += (tx.capitalGainsTax > 0 ? tx.capitalGainsTax / 0.19 : gain.abs());
        } else {
          losing++;
          grossLosses += gain.abs();
        }
      }
    }

    final sellsCount = winning + losing;
    final winRate = sellsCount > 0 ? (winning / sellsCount) * 100.0 : 0.0;
    final profitFactor = grossLosses > 0 ? (grossGains / grossLosses) : (grossGains > 0 ? grossGains : 1.0);

    double drawdown = 0.0;
    if (netWorth < initialCapital && initialCapital > 0) {
      drawdown = ((initialCapital - netWorth) / initialCapital) * 100.0;
    }

    return PerformanceMetrics(
      totalReturnPercent: totalReturnPct,
      netProfitLoss: netPl,
      totalTrades: transactions.length,
      winningTrades: winning,
      losingTrades: losing,
      winRatePercent: winRate,
      profitFactor: profitFactor,
      totalFeesPaid: totalFees,
      totalTaxesWithheld: totalTaxes,
      maxDrawdownPercent: drawdown,
    );
  }
}
