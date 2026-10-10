import 'package:uuid/uuid.dart';

/// Side of the transaction order.
enum OrderSide { buy, sell }

/// Asset class of the traded security.
enum AssetClass { stock, crypto }

/// Status of the simulated trade execution.
enum ExecutionStatus { filled, rejected }

/// Immutable trade receipt auditing statutory friction, fees, and execution price.
class OrderReceipt {
  final String id;
  final DateTime timestamp;
  final String assetId;
  final String assetName;
  final AssetClass assetType;
  final OrderSide side;
  final double quantity;
  final double pricePerUnit;
  final double totalGrossAmount;
  final double brokerFee;
  final double transactionTax;
  final double capitalGainsTax;
  final double netAmount;
  final String countryCode;
  final ExecutionStatus status;
  final String? rejectionReason;

  OrderReceipt({
    String? id,
    DateTime? timestamp,
    required this.assetId,
    required this.assetName,
    required this.assetType,
    required this.side,
    required this.quantity,
    required this.pricePerUnit,
    required this.totalGrossAmount,
    this.brokerFee = 0.0,
    this.transactionTax = 0.0,
    this.capitalGainsTax = 0.0,
    required this.netAmount,
    required this.countryCode,
    this.status = ExecutionStatus.filled,
    this.rejectionReason,
  })  : id = id ?? const Uuid().v4(),
        timestamp = timestamp ?? DateTime.now();

  double get totalFriction => brokerFee + transactionTax + capitalGainsTax;

  Map<String, dynamic> toJson() => {
        'id': id,
        'timestamp': timestamp.toIso8601String(),
        'assetId': assetId,
        'assetName': assetName,
        'assetType': assetType.name,
        'side': side.name,
        'quantity': quantity,
        'pricePerUnit': pricePerUnit,
        'totalGrossAmount': totalGrossAmount,
        'brokerFee': brokerFee,
        'transactionTax': transactionTax,
        'capitalGainsTax': capitalGainsTax,
        'netAmount': netAmount,
        'countryCode': countryCode,
        'status': status.name,
        'rejectionReason': rejectionReason,
      };

  factory OrderReceipt.fromJson(Map<String, dynamic> json) => OrderReceipt(
        id: json['id'] as String?,
        timestamp: json['timestamp'] != null ? DateTime.parse(json['timestamp'] as String) : null,
        assetId: json['assetId'] as String,
        assetName: json['assetName'] as String,
        assetType: AssetClass.values.firstWhere((e) => e.name == json['assetType']),
        side: OrderSide.values.firstWhere((e) => e.name == json['side']),
        quantity: (json['quantity'] as num).toDouble(),
        pricePerUnit: (json['pricePerUnit'] as num).toDouble(),
        totalGrossAmount: (json['totalGrossAmount'] as num).toDouble(),
        brokerFee: (json['brokerFee'] as num?)?.toDouble() ?? 0.0,
        transactionTax: (json['transactionTax'] as num?)?.toDouble() ?? 0.0,
        capitalGainsTax: (json['capitalGainsTax'] as num?)?.toDouble() ?? 0.0,
        netAmount: (json['netAmount'] as num).toDouble(),
        countryCode: json['countryCode'] as String,
        status: ExecutionStatus.values.firstWhere((e) => e.name == json['status']),
        rejectionReason: json['rejectionReason'] as String?,
      );
}
