import 'package:test/test.dart';
import 'package:novaengine/novaengine.dart';

void main() {
  group('CurrencyService', () {
    test('EUR identity conversion', () {
      expect(CurrencyService.toEur(100.0, 'EUR'), equals(100.0));
      expect(CurrencyService.fromEur(100.0, 'EUR'), equals(100.0));
    });

    test('Cross-currency conversions', () {
      // 100 EUR to USD
      final usd = CurrencyService.fromEur(100.0, 'USD');
      expect(usd, greaterThan(100.0));

      // Invert back to EUR
      final eur = CurrencyService.toEur(usd, 'USD');
      expect(eur, closeTo(100.0, 0.001));
    });
  });
}
