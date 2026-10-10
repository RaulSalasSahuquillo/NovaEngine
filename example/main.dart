import 'package:novaengine/novaengine.dart';

void main() async {
  print('Initializing NovaEngine Headless Runtime in Dart...');

  final engine = NovaEngine(
    userCountry: 'ES',
    cashBalance: 100000.0,
    storageProvider: JsonFileStorageProvider(filePath: 'example_portfolio.json'),
  );

  print('Initial Cash Balance: €${engine.cashBalance.toStringAsFixed(2)}');

  // 1. Buy equity position (Apple Inc.) with Spanish Tobin tax and broker fee
  print('\nExecuting simulated purchase of 50 AAPL shares...');
  final buyReceipt = await engine.buy(
    assetId: 'AAPL',
    quantity: 50.0,
    pricePerUnit: 228.45,
    assetName: 'Apple Inc.',
    assetType: AssetClass.stock,
  );

  print('Order Status:      ${buyReceipt.status.name}');
  print('Settled Outlay:    €${buyReceipt.netAmount.toStringAsFixed(2)}');
  print('Broker Fee Paid:   €${buyReceipt.brokerFee.toStringAsFixed(2)}');
  print('Tobin Tax Levied:  €${buyReceipt.transactionTax.toStringAsFixed(2)}');
  print('Remaining Balance: €${engine.cashBalance.toStringAsFixed(2)}');

  // 2. Liquidate 25 shares at profit with progressive Spanish IRPF withholding
  print('\nExecuting simulated sale of 25 AAPL shares at profit (€260.00)...');
  final sellReceipt = await engine.sell(
    assetId: 'AAPL',
    quantity: 25.0,
    pricePerUnit: 260.00,
    assetType: AssetClass.stock,
  );

  print('Order Status:      ${sellReceipt.status.name}');
  print('Gross Proceeds:    €${sellReceipt.totalGrossAmount.toStringAsFixed(2)}');
  print('Capital Gains Tax: €${sellReceipt.capitalGainsTax.toStringAsFixed(2)}');
  print('Net Cash Credited: €${sellReceipt.netAmount.toStringAsFixed(2)}');
  print('Updated Balance:   €${engine.cashBalance.toStringAsFixed(2)}');

  // 3. Print valuation statement
  print('\nCompiling account valuation statement...');
  final statement = engine.getStatement();
  print('Total Net Worth:   €${(statement['total_net_worth'] as double).toStringAsFixed(2)}');
  print('Total Return:      ${(statement['total_profit_loss_pct'] as double).toStringAsFixed(2)}%');

  // 4. Evaluate quantitative metrics
  final metrics = engine.evaluatePerformance();
  print('Win Rate:          ${metrics.winRatePercent.toStringAsFixed(1)}%');
  print('Profit Factor:     ${metrics.profitFactor.toStringAsFixed(2)}');
  print('Total Friction:    €${(metrics.totalFeesPaid + metrics.totalTaxesWithheld).toStringAsFixed(2)}');
}
