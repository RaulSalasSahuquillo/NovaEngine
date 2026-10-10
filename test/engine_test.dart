import 'package:test/test.dart';
import 'package:novaengine/novaengine.dart';

void main() {
  group('NovaEngine Simulation', () {
    test('Buy and sell execution lifecycle', () async {
      final engine = NovaEngine(userCountry: 'ES', cashBalance: 100000.0);

      // Buy 100 shares at €100
      final buyReceipt = await engine.buy(
        assetId: 'AAPL',
        quantity: 100.0,
        pricePerUnit: 100.0,
        assetName: 'Apple Inc.',
        assetType: AssetClass.stock,
      );

      expect(buyReceipt.status, equals(ExecutionStatus.filled));
      expect(buyReceipt.side, equals(OrderSide.buy));
      expect(engine.holdings.length, equals(1));
      expect(engine.holdings.first.quantity, equals(100.0));
      expect(engine.cashBalance, lessThan(100000.0));

      // Sell 50 shares at €150
      final sellReceipt = await engine.sell(
        assetId: 'AAPL',
        quantity: 50.0,
        pricePerUnit: 150.0,
        assetType: AssetClass.stock,
      );

      expect(sellReceipt.status, equals(ExecutionStatus.filled));
      expect(sellReceipt.capitalGainsTax, greaterThan(0.0));
      expect(engine.holdings.first.quantity, equals(50.0));

      // Liquidate remaining 50 shares
      final finalSell = await engine.sell(
        assetId: 'AAPL',
        quantity: 50.0,
        pricePerUnit: 150.0,
        assetType: AssetClass.stock,
      );
      expect(finalSell.status, equals(ExecutionStatus.filled));
      expect(engine.holdings.isEmpty, isTrue);
    });

    test('Solvency check rejects order exceeding available balance', () async {
      final engine = NovaEngine(userCountry: 'ES', cashBalance: 1000.0);

      final receipt = await engine.buy(
        assetId: 'TSLA',
        quantity: 500.0,
        pricePerUnit: 200.0,
        assetType: AssetClass.stock,
      );

      expect(receipt.status, equals(ExecutionStatus.rejected));
      expect(receipt.rejectionReason, contains('Insufficient funds'));
      expect(engine.holdings.isEmpty, isTrue);
      expect(engine.cashBalance, equals(1000.0));
    });

    test('Rejection on selling unowned asset', () async {
      final engine = NovaEngine(userCountry: 'ES', cashBalance: 10000.0);

      final receipt = await engine.sell(
        assetId: 'NVDA',
        quantity: 10.0,
        pricePerUnit: 130.0,
        assetType: AssetClass.stock,
      );

      expect(receipt.status, equals(ExecutionStatus.rejected));
      expect(receipt.rejectionReason, contains('Insufficient position'));
    });
  });
}
