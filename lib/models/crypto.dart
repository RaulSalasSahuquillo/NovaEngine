/// Represents a cryptocurrency asset with market capitalization metrics and sparklines.
class Crypto {
  final String id;
  final String symbol;
  final String name;
  final double currentPrice;
  final double priceChange24h;
  final double priceChangePercentage24h;
  final double marketCap;
  final int marketCapRank;
  final double totalVolume;
  final double high24h;
  final double low24h;
  final String? imageUrl;
  final List<double>? sparklineIn7d;

  const Crypto({
    required this.id,
    required this.symbol,
    required this.name,
    required this.currentPrice,
    required this.priceChange24h,
    required this.priceChangePercentage24h,
    required this.marketCap,
    required this.marketCapRank,
    required this.totalVolume,
    required this.high24h,
    required this.low24h,
    this.imageUrl,
    this.sparklineIn7d,
  });

  factory Crypto.fromJson(Map<String, dynamic> json) {
    List<double>? sparkline;
    if (json['sparkline_in_7d'] != null && json['sparkline_in_7d']['price'] != null) {
      sparkline = (json['sparkline_in_7d']['price'] as List<dynamic>)
          .map((p) => (p as num).toDouble())
          .toList();
    }

    return Crypto(
      id: (json['id'] as String?) ?? '',
      symbol: ((json['symbol'] as String?) ?? '').toUpperCase(),
      name: (json['name'] as String?) ?? '',
      currentPrice: (json['current_price'] as num?)?.toDouble() ?? 0.0,
      priceChange24h: (json['price_change_24h'] as num?)?.toDouble() ?? 0.0,
      priceChangePercentage24h: (json['price_change_percentage_24h'] as num?)?.toDouble() ?? 0.0,
      marketCap: (json['market_cap'] as num?)?.toDouble() ?? 0.0,
      marketCapRank: (json['market_cap_rank'] as num?)?.toInt() ?? 0,
      totalVolume: (json['total_volume'] as num?)?.toDouble() ?? 0.0,
      high24h: (json['high_24h'] as num?)?.toDouble() ?? 0.0,
      low24h: (json['low_24h'] as num?)?.toDouble() ?? 0.0,
      imageUrl: json['image'] as String?,
      sparklineIn7d: sparkline,
    );
  }

  Map<String, dynamic> toJson() {
    return {
      'id': id,
      'symbol': symbol,
      'name': name,
      'current_price': currentPrice,
      'price_change_24h': priceChange24h,
      'price_change_percentage_24h': priceChangePercentage24h,
      'market_cap': marketCap,
      'market_cap_rank': marketCapRank,
      'total_volume': totalVolume,
      'high_24h': high24h,
      'low_24h': low24h,
      'image': imageUrl,
      if (sparklineIn7d != null) 'sparkline_in_7d': {'price': sparklineIn7d},
    };
  }
}
