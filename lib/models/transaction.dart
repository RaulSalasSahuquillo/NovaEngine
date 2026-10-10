/// Financial transaction record auditing fees, levies, and realized capital gains.
class Transaction {
  final String id;
  final String assetId;
  final String assetName;
  final String assetType;
  final String type; // 'buy' or 'sell'
  final double quantity;
  final double pricePerUnit;
  final double totalAmount;
  final DateTime timestamp;
  final double brokerFee;
  final double transactionTax;
  final double capitalGainsTax;
  final double netAmount;
  final String? countryCode;

  Transaction({
    required this.id,
    required this.assetId,
    required this.assetName,
    required this.assetType,
    required this.type,
    required this.quantity,
    required this.pricePerUnit,
    required this.totalAmount,
    required this.timestamp,
    this.brokerFee = 0.0,
    this.transactionTax = 0.0,
    this.capitalGainsTax = 0.0,
    double? netAmount,
    this.countryCode,
  }) : netAmount = netAmount ?? totalAmount;

  bool get isBuy => type.toLowerCase() == 'buy';
  bool get isSell => type.toLowerCase() == 'sell';
  bool get isStock => assetType.toLowerCase() == 'stock';
  bool get isCrypto => assetType.toLowerCase() == 'crypto';
  double get totalTaxesAndFees => brokerFee + transactionTax + capitalGainsTax;

  Map<String, dynamic> toJson() {
    return {
      'id': id,
      'assetId': assetId,
      'assetName': assetName,
      'assetType': assetType,
      'type': type,
      'quantity': quantity,
      'pricePerUnit': pricePerUnit,
      'totalAmount': totalAmount,
      'timestamp': timestamp.toIso8601String(),
      'brokerFee': brokerFee,
      'transactionTax': transactionTax,
      'capitalGainsTax': capitalGainsTax,
      'netAmount': netAmount,
      'countryCode': countryCode,
    };
  }

  factory Transaction.fromJson(Map<String, dynamic> json) {
    return Transaction(
      id: json['id'] as String,
      assetId: json['assetId'] as String,
      assetName: json['assetName'] as String,
      assetType: json['assetType'] as String,
      type: json['type'] as String,
      quantity: (json['quantity'] as num).toDouble(),
      pricePerUnit: (json['pricePerUnit'] as num).toDouble(),
      totalAmount: (json['totalAmount'] as num).toDouble(),
      timestamp: DateTime.parse(json['timestamp'] as String),
      brokerFee: (json['brokerFee'] as num?)?.toDouble() ?? 0.0,
      transactionTax: (json['transactionTax'] as num?)?.toDouble() ?? 0.0,
      capitalGainsTax: (json['capitalGainsTax'] as num?)?.toDouble() ?? 0.0,
      netAmount: (json['netAmount'] as num?)?.toDouble(),
      countryCode: json['countryCode'] as String?,
    );
  }
}
