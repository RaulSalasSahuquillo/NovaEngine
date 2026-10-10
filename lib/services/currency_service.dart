import 'dart:convert';
import 'package:http/http.dart' as http;

/// Multi-currency conversion service using canonical base EUR.
class CurrencyService {
  static final http.Client _client = http.Client();

  static final Map<String, double> _ratesAgainstEur = {
    'EUR': 1.0,
    'USD': 1.085,
    'GBP': 0.855,
    'JPY': 168.50,
    'CHF': 0.945,
    'CAD': 1.490,
    'AUD': 1.645,
    'SEK': 11.35,
    'MXN': 21.20,
    'BRL': 5.95,
  };

  static double getRate({required String fromCurrency, required String toCurrency}) {
    final from = fromCurrency.toUpperCase().trim();
    final to = toCurrency.toUpperCase().trim();
    if (from == to) return 1.0;

    final fromRate = _ratesAgainstEur[from] ?? 1.0;
    final toRate = _ratesAgainstEur[to] ?? 1.0;
    if (fromRate == 0.0) return 1.0;

    return toRate / fromRate;
  }

  static double convert({
    required double amount,
    required String fromCurrency,
    required String toCurrency,
  }) {
    final from = fromCurrency.toUpperCase().trim();
    final to = toCurrency.toUpperCase().trim();
    if (from == to) return amount;
    final rate = getRate(fromCurrency: from, toCurrency: to);
    return amount * rate;
  }

  static double toEur(double amount, String fromCurrency) =>
      convert(amount: amount, fromCurrency: fromCurrency, toCurrency: 'EUR');

  static double fromEur(double amount, String toCurrency) =>
      convert(amount: amount, fromCurrency: 'EUR', toCurrency: toCurrency);

  static Future<bool> refreshLiveRates() async {
    try {
      final url = Uri.parse('https://open.er-api.com/v6/latest/EUR');
      final response = await _client.get(url).timeout(const Duration(seconds: 4));
      if (response.statusCode == 200) {
        final data = json.decode(response.body) as Map<String, dynamic>;
        final rates = data['rates'] as Map<String, dynamic>?;
        if (rates != null) {
          for (final key in _ratesAgainstEur.keys) {
            final rate = (rates[key] as num?)?.toDouble();
            if (rate != null && rate > 0) {
              _ratesAgainstEur[key] = rate;
            }
          }
          return true;
        }
      }
    } catch (_) {
      // Preserve offline fallback matrix on network failure
    }
    return false;
  }
}
