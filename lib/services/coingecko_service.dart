import 'dart:async';
import 'dart:convert';
import 'package:http/http.dart' as http;
import '../models/crypto.dart';

class _CacheEntry<T> {
  final T data;
  final DateTime timestamp;
  _CacheEntry(this.data) : timestamp = DateTime.now();
  bool isValid(Duration ttl) => DateTime.now().difference(timestamp) < ttl;
}

/// Service providing cryptocurrency market feeds with caching and offline resilience.
class CoinGeckoService {
  final http.Client _client;

  CoinGeckoService({http.Client? client}) : _client = client ?? http.Client();

  static const Duration _timeoutDuration = Duration(seconds: 4);
  static const Duration _cacheTtl = Duration(seconds: 12);

  static const Map<String, String> _headers = {
    'User-Agent': 'Mozilla/5.0 (compatible; NovaEngine/1.0; +https://github.com/raulsalas/NovaEngine)',
    'Accept': 'application/json',
  };

  static const Map<String, Map<String, dynamic>> _fallbackCoins = {
    'bitcoin': {'symbol': 'BTC', 'name': 'Bitcoin', 'price': 63400.0, 'change': 850.0, 'pct': 1.35, 'rank': 1, 'mcap': 1.25e12},
    'ethereum': {'symbol': 'ETH', 'name': 'Ethereum', 'price': 3120.0, 'change': -45.0, 'pct': -1.42, 'rank': 2, 'mcap': 3.75e11},
    'solana': {'symbol': 'SOL', 'name': 'Solana', 'price': 142.50, 'change': 5.20, 'pct': 3.78, 'rank': 3, 'mcap': 6.8e10},
  };

  final Map<String, _CacheEntry<Crypto>> _detailCache = {};

  Future<Crypto?> getCrypto(String coinId) async {
    final id = coinId.toLowerCase().trim();
    final cached = _detailCache[id];
    if (cached != null && cached.isValid(_cacheTtl)) {
      return cached.data;
    }

    final url = Uri.parse(
      'https://api.coingecko.com/api/v3/coins/markets?vs_currency=eur&ids=$id&sparkline=false&price_change_percentage=24h',
    );

    try {
      final response = await _client.get(url, headers: _headers).timeout(_timeoutDuration);
      if (response.statusCode == 200) {
        final List<dynamic> jsonList = json.decode(response.body) as List<dynamic>;
        if (jsonList.isNotEmpty) {
          final crypto = Crypto.fromJson(jsonList.first as Map<String, dynamic>);
          _detailCache[id] = _CacheEntry(crypto);
          return crypto;
        }
      }
    } catch (_) {
      // Fall through to offline benchmarks
    }

    if (_fallbackCoins.containsKey(id)) {
      final seed = _fallbackCoins[id]!;
      final crypto = Crypto(
        id: id,
        symbol: seed['symbol'] as String,
        name: seed['name'] as String,
        currentPrice: (seed['price'] as num).toDouble(),
        priceChange24h: (seed['change'] as num).toDouble(),
        priceChangePercentage24h: (seed['pct'] as num).toDouble(),
        marketCap: (seed['mcap'] as num).toDouble(),
        marketCapRank: seed['rank'] as int,
        totalVolume: (seed['mcap'] as num).toDouble() * 0.05,
        high24h: (seed['price'] as num).toDouble() * 1.03,
        low24h: (seed['price'] as num).toDouble() * 0.97,
      );
      _detailCache[id] = _CacheEntry(crypto);
      return crypto;
    }

    return null;
  }

  Future<Map<String, double>> getMultiplePrices(List<String> coinIds) async {
    final Map<String, double> result = {};
    for (final id in coinIds) {
      final quote = await getCrypto(id);
      if (quote != null) {
        result[quote.id] = quote.currentPrice;
      }
    }
    return result;
  }
}
