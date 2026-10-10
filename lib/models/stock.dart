/// Represents an equity asset quote with intra-day metrics and pricing details.
class Stock {
  final String symbol;
  final String name;
  final double currentPrice;
  final double change;
  final double changePercent;
  final double high;
  final double low;
  final double open;
  final double previousClose;
  final String currency;
  final String? imageUrl;

  const Stock({
    required this.symbol,
    required this.name,
    required this.currentPrice,
    required this.change,
    required this.changePercent,
    required this.high,
    required this.low,
    required this.open,
    required this.previousClose,
    this.currency = 'USD',
    this.imageUrl,
  });

  factory Stock.fromJson(Map<String, dynamic> json) {
    final symbol = (json['symbol'] as String?) ?? '';
    final name = (json['shortName'] ?? json['longName'] ?? json['name'] ?? symbol) as String? ?? symbol;

    final currentPrice = (json['regularMarketPrice'] ?? json['currentPrice'] ?? json['price'] as num?)?.toDouble() ?? 0.0;
    final change = (json['regularMarketChange'] ?? json['change'] as num?)?.toDouble() ?? 0.0;
    final changePercent = (json['regularMarketChangePercent'] ?? json['changePercent'] as num?)?.toDouble() ?? 0.0;
    final high = (json['regularMarketDayHigh'] ?? json['high'] ?? json['dayHigh'] as num?)?.toDouble() ?? currentPrice;
    final low = (json['regularMarketDayLow'] ?? json['low'] ?? json['dayLow'] as num?)?.toDouble() ?? currentPrice;
    final open = (json['regularMarketOpen'] ?? json['open'] as num?)?.toDouble() ?? currentPrice;
    final previousClose = (json['regularMarketPreviousClose'] ?? json['previousClose'] as num?)?.toDouble() ?? (currentPrice - change);
    final currency = (json['currency'] as String?) ?? 'USD';
    final imageUrl = (json['imageUrl'] as String?) ??
        (symbol.isNotEmpty ? 'https://assets.parqet.com/logos/symbol/${symbol.toUpperCase()}?format=png' : null);

    return Stock(
      symbol: symbol,
      name: name,
      currentPrice: currentPrice,
      change: change,
      changePercent: changePercent,
      high: high,
      low: low,
      open: open,
      previousClose: previousClose,
      currency: currency,
      imageUrl: imageUrl,
    );
  }

  Map<String, dynamic> toJson() {
    return {
      'symbol': symbol,
      'name': name,
      'currentPrice': currentPrice,
      'change': change,
      'changePercent': changePercent,
      'high': high,
      'low': low,
      'open': open,
      'previousClose': previousClose,
      'currency': currency,
      'imageUrl': imageUrl,
    };
  }

  Stock copyWith({
    String? symbol,
    String? name,
    double? currentPrice,
    double? change,
    double? changePercent,
    double? high,
    double? low,
    double? open,
    double? previousClose,
    String? currency,
    String? imageUrl,
  }) {
    return Stock(
      symbol: symbol ?? this.symbol,
      name: name ?? this.name,
      currentPrice: currentPrice ?? this.currentPrice,
      change: change ?? this.change,
      changePercent: changePercent ?? this.changePercent,
      high: high ?? this.high,
      low: low ?? this.low,
      open: open ?? this.open,
      previousClose: previousClose ?? this.previousClose,
      currency: currency ?? this.currency,
      imageUrl: imageUrl ?? this.imageUrl,
    );
  }
}
