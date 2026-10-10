import 'package:test/test.dart';
import 'package:novaengine/novaengine.dart';

void main() {
  group('PortfolioItem', () {
    test('Weighted average acquisition cost recalculates on additional purchases', () {
      final pos = PortfolioItem(
        assetId: 'AAPL',
        assetName: 'Apple Inc.',
        assetType: 'stock',
        quantity: 10.0,
        avgBuyPrice: 100.0,
        currentPrice: 100.0,
      );

      expect(pos.totalCost, equals(1000.0));

      // Add 10 shares at €200 (Total = 20 shares, total cost = €3,000, avg = €150)
      pos.addVolume(10.0, 200.0);
      expect(pos.quantity, equals(20.0));
      expect(pos.avgBuyPrice, equals(150.0));
      expect(pos.totalCost, equals(3000.0));
      expect(pos.currentPrice, equals(200.0));
    });

    test('Volume reduction updates quantity without shifting average cost', () {
      final pos = PortfolioItem(
        assetId: 'AAPL',
        assetName: 'Apple Inc.',
        assetType: 'stock',
        quantity: 20.0,
        avgBuyPrice: 150.0,
        currentPrice: 200.0,
      );

      pos.reduceVolume(5.0, 210.0);
      expect(pos.quantity, equals(15.0));
      expect(pos.avgBuyPrice, equals(150.0));
      expect(pos.currentPrice, equals(210.0));
    });
  });
}
