/// Represents an open holding position within the portfolio ledger.
class PortfolioItem {
  final String assetId;
  final String assetName;
  final String assetType; // 'stock' or 'crypto'
  double quantity;
  double avgBuyPrice;
  double currentPrice;
  String? imageUrl;

  PortfolioItem({
    required this.assetId,
    required this.assetName,
    required this.assetType,
    required this.quantity,
    required this.avgBuyPrice,
    required this.currentPrice,
    this.imageUrl,
  });

  /// Total market value in canonical EUR.
  double get totalValue => quantity * currentPrice;

  /// Historical acquisition cost in canonical EUR.
  double get totalCost => quantity * avgBuyPrice;

  /// Unrealized profit or loss in canonical EUR.
  double get profitLoss => totalValue - totalCost;

  /// Unrealized profit or loss percentage.
  double get profitLossPercent =>
      totalCost == 0.0 ? 0.0 : (profitLoss / totalCost) * 100.0;

  bool get isStock => assetType.toLowerCase() == 'stock';
  bool get isCrypto => assetType.toLowerCase() == 'crypto';

  /// Adds purchased volume and recalculates weighted average acquisition cost.
  void addVolume(double addedQuantity, double unitPriceEur) {
    if (addedQuantity <= 0) return;
    final double combinedCost = totalCost + (addedQuantity * unitPriceEur);
    final double newQuantity = quantity + addedQuantity;
    avgBuyPrice = combinedCost / newQuantity;
    quantity = newQuantity;
    currentPrice = unitPriceEur;
  }

  /// Reduces volume upon sale and updates current price.
  void reduceVolume(double soldQuantity, double exitPriceEur) {
    quantity = (quantity - soldQuantity).clamp(0.0, double.infinity);
    currentPrice = exitPriceEur;
  }

  PortfolioItem copyWith({
    String? assetId,
    String? assetName,
    String? assetType,
    double? quantity,
    double? avgBuyPrice,
    double? currentPrice,
    String? imageUrl,
  }) {
    return PortfolioItem(
      assetId: assetId ?? this.assetId,
      assetName: assetName ?? this.assetName,
      assetType: assetType ?? this.assetType,
      quantity: quantity ?? this.quantity,
      avgBuyPrice: avgBuyPrice ?? this.avgBuyPrice,
      currentPrice: currentPrice ?? this.currentPrice,
      imageUrl: imageUrl ?? this.imageUrl,
    );
  }

  Map<String, dynamic> toJson() {
    return {
      'assetId': assetId,
      'assetName': assetName,
      'assetType': assetType,
      'quantity': quantity,
      'avgBuyPrice': avgBuyPrice,
      'currentPrice': currentPrice,
      'imageUrl': imageUrl,
    };
  }

  factory PortfolioItem.fromJson(Map<String, dynamic> json) {
    return PortfolioItem(
      assetId: json['assetId'] as String,
      assetName: json['assetName'] as String,
      assetType: json['assetType'] as String,
      quantity: (json['quantity'] as num).toDouble(),
      avgBuyPrice: (json['avgBuyPrice'] as num).toDouble(),
      currentPrice: (json['currentPrice'] as num).toDouble(),
      imageUrl: json['imageUrl'] as String?,
    );
  }
}
