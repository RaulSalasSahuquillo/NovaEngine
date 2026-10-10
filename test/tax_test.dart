import 'package:test/test.dart';
import 'package:novaengine/novaengine.dart';

void main() {
  group('TaxService', () {
    test('Spanish IRPF brackets evaluate accurately', () {
      expect(TaxService.calculateSpanishHaciendaIRPF(0.0), equals(0.0));
      expect(TaxService.calculateSpanishHaciendaIRPF(-100.0), equals(0.0));

      // Up to €6,000 at 19%
      expect(TaxService.calculateSpanishHaciendaIRPF(6000.0), equals(1140.0));

      // €10,000 (€6,000 @ 19% + €4,000 @ 21%)
      expect(TaxService.calculateSpanishHaciendaIRPF(10000.0), equals(1140.0 + 840.0));

      // €100,000 (€6,000 @ 19% + €44,000 @ 21% + €50,000 @ 23%)
      final expected100k = (6000 * 0.19) + (44000 * 0.21) + (50000 * 0.23);
      expect(TaxService.calculateSpanishHaciendaIRPF(100000.0), equals(expected100k));
    });

    test('Buy breakdown includes Tobin Tax and minimum broker fee', () {
      final breakdown = TaxService.calculateBuyBreakdown(
        quantity: 100.0,
        pricePerUnit: 100.0,
        isStock: true,
        countryCode: 'ES',
      );

      expect(breakdown.grossAmount, equals(10000.0));
      expect(breakdown.brokerFee, equals(7.0)); // 0.07% of €10,000
      expect(breakdown.exchangeFee, closeTo(3.0, 0.001)); // 0.03% of €10,000
      expect(breakdown.transactionTax, equals(20.0)); // 0.20% Tobin tax
      expect(breakdown.netAmount, closeTo(10030.0, 0.001));
    });

    test('Sell breakdown computes capital gains withholding', () {
      final breakdown = TaxService.calculateSellBreakdown(
        quantity: 50.0,
        pricePerUnit: 150.0,
        avgBuyPrice: 100.0,
        isStock: true,
        countryCode: 'ES',
      );

      expect(breakdown.grossAmount, equals(7500.0));
      expect(breakdown.realizedProfit, equals(2500.0));
      expect(breakdown.capitalGainsTax, equals(475.0)); // 19% on €2,500
      expect(breakdown.brokerFee, equals(5.25));
      expect(breakdown.exchangeFee, equals(2.25));
      expect(breakdown.netAmount, equals(7500.0 - 5.25 - 2.25 - 475.0));
    });
  });
}
