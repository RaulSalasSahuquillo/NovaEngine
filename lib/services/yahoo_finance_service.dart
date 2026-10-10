import 'dart:async';
import 'dart:convert';
import 'package:http/http.dart' as http;
import '../models/stock.dart';

class _CacheEntry<T> {
  final T data;
  final DateTime timestamp;
  _CacheEntry(this.data) : timestamp = DateTime.now();
  bool isValid(Duration ttl) => DateTime.now().difference(timestamp) < ttl;
}

/// Service providing stock quotes from public Yahoo Finance endpoints with caching.
class YahooFinanceService {
  final http.Client _client;

  YahooFinanceService({http.Client? client}) : _client = client ?? http.Client();

  static const Duration _timeoutDuration = Duration(milliseconds: 3500);
  static const Duration _quoteCacheTtl = Duration(seconds: 10);

  static const Map<String, String> _headers = {
    'User-Agent': 'Mozilla/5.0 (compatible; NovaEngine/1.0; +https://github.com/raulsalas/NovaEngine)',
    'Accept': 'application/json',
  };

  static const List<String> popularSymbols = [
    'AAPL', 'MSFT', 'GOOGL', 'AMZN', 'TSLA',
    'META', 'NVDA', 'JPM', 'V', 'JNJ',
    'WMT', 'PG', 'DIS', 'NFLX', 'AMD',
  ];

  static const Map<String, Map<String, dynamic>> _fallbackQuotes = {
    'AAPL': {'name': 'Apple Inc.', 'price': 228.45, 'change': 3.12, 'pct': 1.38, 'currency': 'USD'},
    'MSFT': {'name': 'Microsoft Corporation', 'price': 422.80, 'change': 4.50, 'pct': 1.08, 'currency': 'USD'},
    'GOOGL': {'name': 'Alphabet Inc.', 'price': 182.30, 'change': 2.10, 'pct': 1.17, 'currency': 'USD'},
    'AMZN': {'name': 'Amazon.com Inc.', 'price': 195.60, 'change': -1.20, 'pct': -0.61, 'currency': 'USD'},
    'TSLA': {'name': 'Tesla Inc.', 'price': 250.10, 'change': 6.80, 'pct': 2.79, 'currency': 'USD'},
  };

  final Map<String, _CacheEntry<Stock>> _quoteCache = {};

  Future<Stock?> getQuote(String symbol) async {
    final sym = symbol.toUpperCase().trim();
    final cached = _quoteCache[sym];
    if (cached != null && cached.isValid(_quoteCacheTtl)) {
      return cached.data;
    }

    final url = Uri.parse(
      'https://query1.finance.yahoo.com/v8/finance/chart/$sym?interval=1d&range=1d',
    );

    try {
      final response = await _client.get(url, headers: _headers).timeout(_timeoutDuration);
      if (response.statusCode == 200) {
        final data = json.decode(response.body) as Map<String, dynamic>;
        final resultList = data['chart']?['result'] as List<dynamic>?;
        if (resultList != null && resultList.isNotEmpty) {
          final meta = resultList[0]['meta'] as Map<String, dynamic>;
          final stock = Stock.fromJson(meta);
          _quoteCache[sym] = _CacheEntry(stock);
          return stock;
        }
      }
    } catch (_) {
      // Fall through to offline benchmarks
    }

    if (_fallbackQuotes.containsKey(sym)) {
      final fb = _fallbackQuotes[sym]!;
      final price = (fb['price'] as num).toDouble();
      final change = (fb['change'] as num).toDouble();
      final stock = Stock(
        symbol: sym,
        name: fb['name'] as String,
        currentPrice: price,
        change: change,
        changePercent: (fb['pct'] as num).toDouble(),
        high: price * 1.01,
        low: price * 0.99,
        open: price - change,
        previousClose: price - change,
        currency: fb['currency'] as String,
      );
      _quoteCache[sym] = _CacheEntry(stock);
      return stock;
    }

    return null;
  }

  Future<Map<String, double>> getMultipleQuotes(List<String> symbols) async {
    final Map<String, double> result = {};
    for (final sym in symbols) {
      final quote = await getQuote(sym);
      if (quote != null) {
        result[quote.symbol] = quote.currentPrice;
      }
    }
    return result;
  }
}
